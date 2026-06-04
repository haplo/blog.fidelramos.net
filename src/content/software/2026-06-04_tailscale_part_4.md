Title: Self-hosted Tailscale, Part 4: Tailscale-Only Web Services
Date: 2026-06-04
Lang: en
Category: Software
Tags: howto,linux,security,tailscale,vpn
Slug: tailscale-4-web-services
Series: Self-hosted Tailscale

I've been running a [home server]({filename}/software/2023-12-29_homelab.md) with a bunch of self-hosted services (Immich, Jellyfin, Nextcloud...) behind a single Caddy instance using `caddy-docker-proxy` (documented [in this post]({filename}/software/2023-11-09_switch_nginx_caddy_docker_compose.md)).
Some of them have genuine public uses, e.g. sharing a folder in Nextcloud or an album in Immich, or connecting to Jellyfin through another device (like a Smart TV).
However the overwhelming majority of my interaction with those services is personal, from my own devices, and exposing them to the public internet is a considerable **security risk**, as they are entry points to my internal systems.

The solution now that I have [Tailscale running]({filename}/software/2026-05-05_tailscale_part_1.md) is to make as many services as practicable accessible only through the tailnet.
To achieve this I will run **two Caddy instances in parallel**: one bound to the public interface, for public-facing services; another bound to the Tailscale interface, for tailnet-only ones.
It wasn't immediately obvious how to do that with `caddy-docker-proxy`, but I got it working without dirty hacks.

This post is the write-up of the setup I landed on, and the pile of gotchas I hit getting there.

## The architecture

Two separate Caddy instances in Docker, both using `caddy-docker-proxy`:

- **`caddy-public`**: bound to the LAN IP, reached from the Internet via the router's port forward on 80/443. Handles public services.
- **`caddy-tailscale`**: bound to the host's Tailscale IP (`100.x.y.z`), reachable only from devices on my tailnet. Handles private services.

Each Caddy watches Docker labels with a different prefix, so services opt in to one or the other (or both, rarely) by using the appropriate label prefix and joining the appropriate Docker network.

Private services use certificates issued via [DNS-01 challenge](https://letsencrypt.org/docs/challenge-types/#dns-01-challenge) through Gandi (my DNS hosting provider).
Public services keep using normal certs via HTTP-01.

Here's the high-level picture:

```
Internet ──► router:443 ──► host:LAN_IP:443 ──► caddy-public    ──► headscale
Tailnet  ──► host:TAILSCALE_IP:443          ──► caddy-tailscale ──► immich, jellyfin, nextcloud, etc.
```

## Why two Caddys and not one with an IP allowlist?

I considered this.
A single Caddy with a [`remote_ip`](https://caddyserver.com/docs/modules/http.matchers.remote_ip) matcher restricting certain hostnames to `100.64.0.0/10` would have worked.
**But**:

- Port 443 would still be reachable from the internet for those hostnames. I'd be relying on Layer 7 filtering to keep attackers out of services that shouldn't be WAN-exposed at all.
- Private services need DNS-01 certs (because Let's Encrypt can't reach a `100.x` address for HTTP-01), public services don't.
- One forgotten Docker label and an internal service is on the public internet.

Two separate Caddys gives me network-layer isolation: the private services literally aren't listening on a WAN-reachable socket.
That's a much stronger guarantee than "listening but configured to reject".

## The Docker Compose setup

Here's the essential shape (with some env vars for clarity):

```yaml
services:
  caddy-public:
    build:
      context: .
      dockerfile: Dockerfile.caddy
    image: caddy-docker-proxy-gandi:local
    container_name: caddy-public
    restart: unless-stopped
    environment:
      - CADDY_INGRESS_NETWORKS=caddy_public
    ports:
      - "${LAN_IP:?LAN_IP must be set}:80:80"
      - "${LAN_IP:?LAN_IP must be set}:443:443"
    labels:
      caddy.email: ${CADDY_EMAIL}
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ${CADDY_FILES_PATH}/public:/data
    networks:
      - caddy_public
    dns:
      - 1.1.1.1
      - 9.9.9.9

  caddy-tailscale:
    build:
      context: .
      dockerfile: Dockerfile.caddy
    image: caddy-docker-proxy-gandi:local
    container_name: caddy-tailscale
    restart: unless-stopped
    environment:
      - CADDY_INGRESS_NETWORKS=caddy_tailscale
      - CADDY_DOCKER_LABEL_PREFIX=caddy_ts
      - GANDI_BEARER_TOKEN=${GANDI_BEARER_TOKEN}
    ports:
      - "${TAILSCALE_IP:?TAILSCALE_IP must be set}:80:80"
      - "${TAILSCALE_IP:?TAILSCALE_IP must be set}:443:443"
    labels:
      caddy_ts.email: ${CADDY_EMAIL}
      caddy_ts.acme_dns: "gandi {env.GANDI_BEARER_TOKEN}"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ${CADDY_FILES_PATH}/tailscale:/data
    networks:
      - caddy_tailscale
    dns:
      - 1.1.1.1
      - 9.9.9.9

networks:
  caddy_public:
    name: caddy_public
  caddy_tailscale:
    name: caddy_tailscale
```

A few things worth calling out:

- **Separate label namespaces.** `CADDY_DOCKER_LABEL_PREFIX=caddy_ts` tells the tailnet Caddy to read labels starting with `caddy_ts`. The public Caddy uses the default `caddy`. Services opt in by prefix, no possibility of cross-contamination.

- **`CADDY_INGRESS_NETWORKS`**: Each Caddy is scoped to discover only containers on its own network. Without this, each Caddy would try to proxy every labeled container it could see via the Docker socket, and they'd fight.

- **Separate `/data` volumes.** The two Caddys have their own certificates storage. Sharing would work but separate is cleaner and removes an edge case.

- **Binding to specific IPs, not `0.0.0.0`.** This one cost me an embarrassing amount of debugging time (see below).

- **The `:?` guards on env vars.** Compose silently falls back to `0.0.0.0` if the host-IP part of a port spec is empty. The `:?` syntax makes it fail loudly instead. After getting burned by this twice, I will always use this kind of guard when setting up services that must be bound to a specific IP.

## Building a Caddy image with the Gandi DNS plugin

I use Gandi as my DNS provider, and luckily Caddy has [a plugin for it](https://github.com/caddy-dns/gandi).
However the `lucaslorentz/caddy-docker-proxy` image doesn't include any DNS plugins, and they have to be compiled in, you can't add them at runtime.
I built a small custom image by creating a `Dockerfile.caddy` file:

```dockerfile
ARG CADDY_VERSION=2

FROM caddy:${CADDY_VERSION}-builder AS builder

RUN xcaddy build \
--with github.com/lucaslorentz/caddy-docker-proxy/v2 \
--with github.com/caddy-dns/gandi

FROM caddy:${CADDY_VERSION}-alpine

COPY --from=builder /usr/bin/caddy /usr/bin/caddy

CMD ["caddy", "docker-proxy"]
```

Then `docker compose build caddy-tailscale` would trigger the image build.

This pattern is common and [documented to make custom Caddy images](https://hub.docker.com/_/caddy#adding-custom-caddy-modules).

A key detail is the final `CMD`. `caddy-docker-proxy` runs in a different mode than the normal Caddy server, and you have to override it explicitly.

For the Gandi side, I created a Personal Access Token (not a legacy API key) with "Manage domain technical configurations" permission.
I stuffed it into `.env` as `GANDI_BEARER_TOKEN`.

## Moving services to the tailscale Caddy

With DNS-01 working, now it's time to move my web services to the tailnet.

The changes are easy: put the services in the `caddy_tailscale` network, and change the `caddy` labels to `caddy_ts`.

For example my Immich service (only the relevant parts):

```yaml
immich-server:
  labels:
    caddy_ts: immich.ts.fidelramos.net
    caddy_ts.reverse_proxy: "{{upstreams 2283}}"
  networks:
    - caddy_tailscale
    - immich
```

Beautiful, isn't it?

## DNS setup

There are no public DNS records.
Instead I rely on Blocky's `customDNS` (see [Part 2]({filename}/software/2026-05-11_tailscale_part_2.md)) to create DNS records that will only be visible to my tailnet devices.

In Blocky's configuration:

```yaml
customDNS:
  customTTL: 1h
  filterUnmappedTypes: true
  rewrite:
    ts.fidelramos.net: tail   # allows 'X.ts.fidelramos.net' as alias for 'X.tail'
  mapping:
    # Friendly names for services on tailnet
    immich.tail: 100.64.0.1
    jellyfin.tail: 100.64.0.1
    nextcloud.tail: 100.64.0.1
```

This requires manually managing the entries and IPs, but this being a humble home network they don't change that often and it's a reasonable compromise.

## Verification

After `docker-compose up -d` I check the logs of the containers that everything looks good.
Both caddy instances spin up correctly.
`caddy-tailscale` issues new certs through DNS-01 challenge.

In the host I verify that each caddy listens on their bound IP:

```bash
$ ss -tlnp | grep -E ':80|:443'
LISTEN 0 4096 192.168.1.50:80   0.0.0.0:*
LISTEN 0 4096 192.168.1.50:443  0.0.0.0:*
LISTEN 0 4096 100.64.0.1:80     0.0.0.0:*
LISTEN 0 4096 100.64.0.1:443    0.0.0.0:*
```

The router only forwards to the LAN IP, so the tailnet listener is invisible to the Internet.

Public services remain reachable at `https://<service>.fidelramos.net` from anywhere.
Private services are reachable at `https://immich.ts.fidelramos.net` only from devices on my tailnet.

New private services need a DNS record in Blocky and a couple labels and a network attachment in Docker compose to be live.

## The gotchas I hit so you won't have to

This is the part I wish someone had written down for me, they took significant time to figure out.

### Compose silently falls back to `0.0.0.0`

If you write `${TAILSCALE_IP}:80:80` and `TAILSCALE_IP` is empty, Docker binds `0.0.0.0:80`.
Both Caddys then fight for the same port and one fails to start with `port is already allocated`.

I used `${TAILSCALE_IP:?...}` to make it fail loudly if the environment variable is not defined.

Solving this was quick enough, but then I found the next gotcha...

### Failed containers leave zombies

When a container fails to bind its ports, Docker leaves it in a weird half-state: `NetworkMode` is set correctly, but the container is actually attached to no network.
`docker inspect` shows `"Networks": {}`, and `ip addr` inside the container shows only `lo`.
A subsequent `docker compose up -d` sees the container "exists" and just starts it without fixing anything.
You end up with a running container that has no connectivity at all.

The fix was to start with a clean slate, `docker compose down`, then `docker compose up -d`.

### Binding `0.0.0.0:80` conflicts with `100.x.y.z:80`

Even if both IPs are "valid", Docker treats `0.0.0.0` as a superset. I had `caddy-public` binding `0.0.0.0:80` and `caddy-tailscale` binding `100.64.0.1:80` and got intermittent startup failures depending on order.

The fix is to pin **both** to specific IPs (LAN IP for public, Tailscale IP for tailnet).

No overlap, no race.

### `caddy-docker-proxy` needs the service's network

The Caddy's `CADDY_INGRESS_NETWORKS` filter and the actual routing both require the proxied service to be on the same Docker network as the Caddy.
A service can be on additional networks (for its own database, etc.), but it needs at least the Caddy's ingress network, or it's invisible.

## Would I do it again?

Yes.
The initial setup was surprisingly painful because there were multiple failures stacking on top of each other, but the resulting architecture is clean and cheap to extend.

Every new service I add goes through the same dead-simple decision:

* Public: `caddy.*` labels, `caddy_public` network, DNS record in Gandi.
* Private: `caddy_ts.*` labels, `caddy_tailscale` network, DNS record in Blocky.

No firewall rules to keep in sync; no per-service auth middleware; no "I'll just expose it temporarily" that becomes permanent.

The short lesson from the whole exercise: Tailscale is excellent at making "just me" services reachable from my devices, but integrating it with a Docker-based reverse proxy has more sharp edges than either technology has on its own.
Binding your listeners to specific IPs, failing loudly on missing env vars, and giving containers explicit DNS resolvers are the three habits that would have saved me most of the pain.

## Future improvement: limited access for other people

With this setup I lost the ability to share an Immich album with my family or friends, or to share a Nextcloud folder by sending a link.
These are genuine helpful use cases that I would like to restore in some way.

For my family I will study getting them access to my tailnet, and then using ACLs to restrict their devices to only the services they need.

For file sharing I'm researching options like [Filestash](https://www.filestash.app/) or [FileBrowser Quantum](https://filebrowserquantum.com/), which are tailored services for this particular use case.
What I want is to make the full admin UI accessible only through tailnet, and make their public sharing endpoints Internet-routable.

Whatever solutions I land on I will likely write blog posts about them.
