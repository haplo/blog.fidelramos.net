Title: Self-hosted Tailscale, Part 2: Ad-blocking DNS
Date: 2026-05-11
Lang: en
Category: Software
Tags: dns,howto,linux,security,tailscale,vpn
Slug: tailscale-2-ad-blocking-dns
Series: Self-hosted Tailscale

In [Part 1]({filename}/software/2026-05-05_tailscale_part_1.md) I set up Headscale and had every tailnet client use Cloudflare DNS.
That works, but it's leaving value on the table: every device that connects to my Tailscale gets whatever DNS servers I set, so I might as well run my own DNS server inside the private network and get ad-blocking, tracker-blocking, and internal name resolution everywhere I go.

This post swaps Cloudflare for [Blocky](https://0xerr0r.github.io/blocky/), a lightweight DNS proxy with built-in blocklist support.

I chose Blocky over [Pi-hole](https://pi-hole.net/) or [AdGuard Home](https://github.com/AdguardTeam/Adguardhome) because it's simpler, configured in a single YAML file.
It doesn't try to be a full web product, just a DNS server that does its job and stays out of the way.

You could easily replace Blocky with some other DNS server or proxy of your choice by keeping the Headscale and Tailscale bits.

[TOC]

## Goals

1. Block ads and trackers at the DNS level on every tailnet device.
2. Keep DNS encrypted on the wire (DoT upstream), even though traffic between my devices and Blocky is already protected by WireGuard.
3. Have internal name resolution, so for example `homeserver.ts.fidelramos.net` still resolves.
4. No device-level DNS configuration. Everything is pushed by Headscale and clients pick it up automatically.

## Why not just Android's Private DNS?

Android has a built-in "Private DNS" feature that does [DoT](https://en.wikipedia.org/wiki/DNS_over_TLS) to any public resolver.
I was previously using a private AdGuard DNS's server (`xxxxxxxx.d.adguard-dns.com`).
I tried using it alongside Tailscale, but it doesn't work: as soon as Tailscale pushes any DNS settings to the client, Android routes DNS through the tunnel via Tailscale's internal resolver (`100.100.100.100`), which doesn't speak DoT.
Android's Private DNS probe fails with "cannot connect" and DNS resolution breaks device-wide.

You can disable "Use Tailscale DNS" in the app to get Private DNS back, but then you lose MagicDNS.

Forced to choose, I went the other way: run my own DNS on the tailnet and let Headscale push it to all clients.

## Architecture

```
  Device on tailnet
        │
        │ plain DNS (over WireGuard tunnel)
        ▼
  Blocky  ──▶  blocklists (local)
        │
        │ DNS-over-TLS (DoT) to upstream
        ▼
  Cloudflare / Quad9 / Google DNS / etc.
```

- Clients talk plain DNS to Blocky's tailnet IP. "Plain" is fine because the whole path is inside a WireGuard tunnel.
- Blocky does the filtering against blocklists it maintains locally.
- For anything that isn't blocked, Blocky forwards upstream over DoT.
- Blocky also keeps mappings for local tailnet domains to tailnet IPs.

## Blocky in Docker Compose

I run Blocky in my existing Docker Compose project that runs everything else in my home server.

`compose.yml`:

```yaml
services:
  blocky:
    image: spx01/blocky:latest
    container_name: blocky
    network_mode: host
    restart: unless-stopped
    volumes:
      - ${BLOCKY_ROOT}/config.yml:/app/config.yml:ro
      - /var/log/blocky:/logs:rw
    environment:
      - TZ=${TZ}
    healthcheck:
      test: ["CMD", "/app/blocky", "healthcheck"]
      interval: 1m
      timeout: 10s
      retries: 3
```

Highlights:

- **network_mode: host.** This is a bit lazy on my part, but opening the Docker port only to the tailnet IP is trickier than one would expect. Blocky will be configured in the next section to only bind to the tailnet IP, so I don't think it's a big security risk. I'm trusting Blocky not to bind to other interfaces or ports in the system.
- **Config file is read-only** inside the container. It's safer, and reminds me that the source of truth is my versioned config on disk.
- I had to `chown 100 /var/log/blocky`, as that is the UID that the blocky container uses. Otherwise I'd be getting permission errors in Blocky's Docker logs.

## Blocky configuration

This is my configuration with internal names redacted. Check out the [Blocky docs](https://0xerr0r.github.io/blocky/latest/) for full details.

```/var/opt/blocky/config/config.yml```

```yaml
# =================================================================
# Blocky config — Tailscale/headscale global resolver
# =================================================================

# ---------------------------------------------------------------
# Upstream resolvers (encrypted via DoT)
# ---------------------------------------------------------------
upstreams:
  init:
    strategy: blocking
  groups:
    default:
      - tcp-tls:dns.quad9.net:853
      - tcp-tls:one.one.one.one:853

# Explicit IPs for upstream resolution at startup
# (avoids chicken-and-egg when Blocky is itself the system resolver)
bootstrapDns:
  - upstream: tcp-tls:1.1.1.1:853
    ips:
      - 1.1.1.1
      - 1.0.0.1
  - upstream: tcp-tls:9.9.9.9:853
    ips:
      - 9.9.9.9
      - 149.112.112.112

# ---------------------------------------------------------------
# Client identification (static, since no DHCP on tailnet)
# Add a new entry here whenever you add a tailscale node
# ---------------------------------------------------------------
clientLookup:
  clients:
    homeserver:
      - 100.64.0.1
    laptop:
      - 100.64.0.2
    phone:
      - 100.64.0.3
    desktop:
      - 100.64.0.4

# ---------------------------------------------------------------
# Custom local DNS records for your tailnet nodes
# Add a new entry here whenever you add a tailscale node
# ---------------------------------------------------------------
customDNS:
  customTTL: 1h
  filterUnmappedTypes: true
  rewrite:
    ts.fidelramos.net: tail   # allows 'X.ts.fidelramos.net' as shortcut for 'X.tail'
  mapping:
    homeserver.tail: 100.64.0.1
    laptop.tail: 100.64.0.2
    phone.tail: 100.64.0.3
    desktop.tail: 100.64.0.4
    # Friendly names for services on tailnet (for Part 4)
    immich.tail: 100.64.0.1
    jellyfin.tail: 100.64.0.1
    nextcloud.tail: 100.64.0.1

# ---------------------------------------------------------------
# Blocking
# ---------------------------------------------------------------
blocking:
  denylists:
    ads:
      - https://adguardteam.github.io/AdGuardSDNSFilter/Filters/filter.txt
      - https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts
      - https://adaway.org/hosts.txt
      - https://v.firebog.net/hosts/AdguardDNS.txt
      - https://v.firebog.net/hosts/Easyprivacy.txt
    malware:
      - https://urlhaus.abuse.ch/downloads/hostfile/
      - https://v.firebog.net/hosts/Prigent-Malware.txt
    tracking:
      - https://v.firebog.net/hosts/Easyprivacy.txt
    smart-tv:
      - https://perflyst.github.io/PiHoleBlocklist/SmartTV.txt
    kids:
      - https://blocklistproject.github.io/Lists/porn.txt
      - https://blocklistproject.github.io/Lists/gambling.txt

  allowlists:
    ads:
      - |
        # Common false positives
        clients4.google.com
        clients2.google.com
        googleads.g.doubleclick.net

  clientGroupsBlock:
    default:
      - ads
      - malware
      - tracking
    # Per-client overrides by name (from clientLookup above)
    # phone:
    #   - ads
    #   - malware
    #   - tracking
    #   - smart-tv
    # kids-tablet:
    #   - ads
    #   - malware
    #   - kids

  loading:
    refreshPeriod: 24h
    downloads:
      timeout: 60s
      attempts: 3
      cooldown: 10s
    strategy: blocking
    maxErrorsPerSource: 5
  blockType: zeroIp
  blockTTL: 1m

# ---------------------------------------------------------------
# Caching
# ---------------------------------------------------------------
caching:
  minTime: 5m
  maxTime: 30m
  maxItemsCount: 0
  prefetching: true
  prefetchExpires: 2h
  prefetchThreshold: 5
  cacheTimeNegative: 30m

# ---------------------------------------------------------------
# Ports & binding
# Bind ONLY to tailnet IP so Blocky isn't exposed on LAN/WAN
# ---------------------------------------------------------------
ports:
  dns: 100.64.0.1:53
  tls: 100.64.0.1:853     # optional DoT for tailnet clients
  http: 127.0.0.1:4000    # metrics / API (local only)

# ---------------------------------------------------------------
# Logging & metrics
# ---------------------------------------------------------------
log:
  level: info
  format: text
  timestamp: true
  privacy: false

queryLog:
  type: csv-client
  target: /logs
  logRetentionDays: 7
  creationAttempts: 3
  creationCooldown: 2s

prometheus:
  enable: false
  path: /metrics

# ---------------------------------------------------------------
# Misc
# ---------------------------------------------------------------
# Block leaks of private-use TLDs to public resolvers
specialUseDomains:
  rfc6762-appendixG: true
```

At a high level:

- **Upstreams over DoT**: Cloudflare and Quad9 as parallel resolvers, using DNS-over-TLS so the traffic coming from Blocky is encrypted.
- **Custom DNS entries**: a few internal hostnames I want to resolve tailnet-wide without touching Headscale's `extra_records` (I'll cover that in Part 4).
- **Blocking**: a mix of general lists and a couple of targeted blocklists I care about. I will revisit these lists, but they seemed like a good starting point.
- **Caching**: enabled, with sensible defaults.
- **Prometheus metrics**: off for now, I don't have a metrics collector right now, will do that in my [new home server]({filename}/software/2026-01-25_self_hosted_home_1.md).

Start it up:

```bash
$ sudo docker compose up -d
$ sudo docker logs -f blocky
```

## Sanity check from the host:

DNS resolves:

```bash
$ dig @100.64.0.1 example.com
; <<>> DiG 9.20.22 <<>> @100.64.0.1 example.com
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 57184
;; flags: qr rd ra ad; QUERY: 1, ANSWER: 2, AUTHORITY: 0, ADDITIONAL: 1

;; OPT PSEUDOSECTION:
; EDNS: version: 0, flags:; udp: 512
;; QUESTION SECTION:
;example.com.                   IN      A

;; ANSWER SECTION:
example.com.            300     IN      A       172.66.147.243
example.com.            300     IN      A       104.20.23.154

;; Query time: 24 msec
;; SERVER: 100.64.0.1#53(100.64.0.1) (UDP)
;; WHEN: Sun May 10 16:30:57 WEST 2026
;; MSG SIZE  rcvd: 72
```

Blocked domain (returns 0.0.0.0):

```
$ dig @100.64.0.1 doubleclick.net
; <<>> DiG 9.20.22 <<>> @100.64.0.1 doubleclick.net
; (1 server found)
;; global options: +cmd
;; Got answer:
;; ->>HEADER<<- opcode: QUERY, status: NOERROR, id: 45469
;; flags: qr rd ra; QUERY: 1, ANSWER: 1, AUTHORITY: 0, ADDITIONAL: 0

;; QUESTION SECTION:
;doubleclick.net.               IN      A

;; ANSWER SECTION:
doubleclick.net.        60      IN      A       0.0.0.0

;; Query time: 1 msec
;; SERVER: 100.64.0.1#53(100.64.0.1) (UDP)
;; WHEN: Sun May 10 16:32:50 WEST 2026
;; MSG SIZE  rcvd: 49
```

Blocky only binds to tailnet IP, no DNS port exposed to the Internet:

```
$ sudo ss -ulnp | grep :53
UNCONN 0      0          100.64.0.1:53         0.0.0.0:*    users:(("blocky",pid=2984612,fd=15))

$ sudo ss -tlnp | grep -E ':53|:853'
LISTEN 0      4096      100.64.0.1:53         0.0.0.0:*    users:(("blocky",pid=2984612,fd=16))
LISTEN 0      4096      100.64.0.1:853        0.0.0.0:*    users:(("blocky",pid=2984612,fd=14))
```

## Changes to Headscale

Now for the Tailscale magic: I tell Headscale to push Blocky's tailnet IP as the global resolver to every client.
Edit `/var/opt/headscale/config/config.yaml`, its `dns` block changes as follows:

```yaml
dns:
  magic_dns: false
  override_local_dns: true          # push our DNS to clients, replacing their system DNS
  base_domain: ts.fidelramos.net
  nameservers:
    global:
      - 100.64.0.1                  # Blocky on the tailnet
  search_domains: []
```

Restart Headscale:

```bash
$ sudo docker compose restart headscale
```

Each client has to pull the new settings:

- **Linux:** `sudo tailscale up --login-server=https://headscale.fidelramos.net --accept-dns=true`
- **Android:** toggle the Tailscale VPN switch off and back on. Also **disable Android's Private DNS** (Settings → Network → Private DNS → Off), since it would conflict.

Verify from a Linux client:

```bash
$ resolvectl status | grep -A2 tailscale0
# Should show 100.64.0.1 as the DNS server on tailscale0

$ dig example.com
# Should resolve via Blocky
```

## Why this is arguably better than device-level DoT

The encryption story ends up equivalent or stronger:

- **Device → Blocky**: plain DNS, but inside a WireGuard tunnel. Your ISP sees a UDP stream to your home server, but nothing else.
- **Blocky → upstream DNS**: encrypted DNS-over-TLS. Your upstream sees the query from your host server, but not which device made it.

And I get things I couldn't get with per-device DoT:

- **Autoconfiguration**, just by connecting through Tailscale.
- **Centralized blocklists**. Change one file, every device benefits.
- **Per-client query logs** in one place. Blocky can log queries by client IP.
- **Internal DNS entries**, I'll use them in Part 4.
- **Works identically on every platform**, no Android Private DNS dance.
- **No need to change router configuration**. My current ISP router doesn't allow me to override the DNS, so this is a neat way of setting DNS on all my devices.

## Encountered pitfalls

### Android "cannot connect" with Private DNS set

Already mentioned in Part 1, but worth repeating because it bites everyone: with Tailscale's DNS active, Android's Private DNS setting must be **Off** or **Automatic**.
Setting it to a strict DoT hostname breaks DNS entirely on the device while Tailscale is connected.

### DNS resolution breaks on the host itself

If your home server uses `127.0.0.53` (systemd-resolved) and you then ask it to use Blocky for everything, and Blocky is in a container that depends on DNS to start... you can paint yourself into a corner.

Two ways out:

1. Leave the host's `/etc/resolv.conf` pointing at an external resolver (e.g. Cloudflare) and only push Blocky to *tailnet clients*. This is what I do — the host itself doesn't use Blocky, only the devices that connect through Tailscale.
2. Or, pin Blocky's image so it's always locally available and let Docker start it before anything else needs DNS.

### Clients don't pick up the new DNS

Headscale pushes DNS config on every map update, but some clients (especially Linux with NetworkManager) need a nudge.
Running `tailscale up` again with `--accept-dns=true` forces a re-sync.
On Android, toggling off then on is usually enough.

### Have to disable MagicDNS

If `magic_dns` had been left enabled in Headscale configuration it would have been in conflict with Blocky DNS, as both would try to use the same port 53.

I decided to disable MagicDNS and keep the `mapping` in Blocky's config of domains and IPs.
It's a manual process, but my tailnet is small and won't change much, so I'm OK with it if it means a simpler setup.

An alternative solution would be to run Headscale MagicDNS in a different port, then have Blocky use it.

## What's next

With Blocky in place, every device on my tailnet gets ad-blocking and filtered DNS, under any Internet connection anywhere in the world.

In Part 3 I'll reconfigure Syncthing to use the tailnet exclusively, disabling all its WAN-oriented discovery and relay features now that they're unnecessary.
