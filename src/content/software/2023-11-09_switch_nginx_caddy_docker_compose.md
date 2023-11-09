Title: Replacing Nginx with Caddy in Docker Compose
Date: 2023-11-09
Lang: en
Category: Software
Tags: caddy,docker,homelab,nginx
Slug: switch-nginx-caddy-docker-compose

The main server in my homelab runs a bunch of services, but the heart of it is a [Docker Compose](https://docs.docker.com/compose/) configuration, several of them exposed to the Internet via a reverse proxy webserver.

Before I was using three Docker images to run Nginx, proxy traffic to other services and have it generate Letsencrypt certificates for the necessary domains:

1. [nginx](https://hub.docker.com/_/nginx) with the actual Nginx server running.
2. [nginx-proxy](https://github.com/jwilder/nginx-proxy) to generate Nginx configurations.
3. [docker-letsencrypt-nginx-proxy-companion](https://github.com/jwilder/docker-letsencrypt-nginx-proxy-companion): to handle LetsEncrypt certificate provisioning and renewal.

The relevant configuration in *compose.yml* looked like this:

```yaml
services:
  nginx:
    image: nginx
    labels:
        com.github.jrcs.letsencrypt_nginx_proxy_companion.nginx_proxy: "true"
        UFW_MANAGED: "true"
    container_name: ${NGINX_WEB:-nginx}
    restart: always
    ports:
      - "${DOCKER_HTTP:-80}:80"
      - "${DOCKER_HTTPS:-443}:443"
    volumes:
      - ${NGINX_FILES_PATH}/conf.d:/etc/nginx/conf.d
      - ${NGINX_FILES_PATH}/vhost.d:/etc/nginx/vhost.d
      - ${NGINX_FILES_PATH}/html:/usr/share/nginx/html
      - ${NGINX_FILES_PATH}/certs:/etc/nginx/certs:ro
      - ${NGINX_FILES_PATH}/htpasswd:/etc/nginx/htpasswd:ro
    logging:
      driver: ${NGINX_WEB_LOG_DRIVER:-json-file}
      options:
        max-size: ${NGINX_WEB_LOG_MAX_SIZE:-4m}
        max-file: ${NGINX_WEB_LOG_MAX_FILE:-10}

  nginx-gen:
    image: nginxproxy/docker-gen
    command: -notify-sighup ${NGINX_WEB:-nginx} -watch -wait 5s:30s /etc/docker-gen/templates/nginx.tmpl /etc/nginx/conf.d/default.conf
    container_name: ${DOCKER_GEN:-nginx-gen}
    restart: always
    volumes:
      - ${NGINX_FILES_PATH}/conf.d:/etc/nginx/conf.d
      - ${NGINX_FILES_PATH}/vhost.d:/etc/nginx/vhost.d
      - ${NGINX_FILES_PATH}/html:/usr/share/nginx/html
      - ${NGINX_FILES_PATH}/certs:/etc/nginx/certs:ro
      - ${NGINX_FILES_PATH}/htpasswd:/etc/nginx/htpasswd:ro
      - /var/run/docker.sock:/tmp/docker.sock:ro
      - ./nginx.tmpl:/etc/docker-gen/templates/nginx.tmpl:ro
    logging:
      driver: ${NGINX_GEN_LOG_DRIVER:-json-file}
      options:
        max-size: ${NGINX_GEN_LOG_MAX_SIZE:-2m}
        max-file: ${NGINX_GEN_LOG_MAX_FILE:-10}

  nginx-letsencrypt:
    image: nginxproxy/acme-companion
    container_name: ${LETSENCRYPT_CONTAINER:-nginx-letsencrypt}
    restart: always
    volumes:
      - ${NGINX_FILES_PATH}/conf.d:/etc/nginx/conf.d
      - ${NGINX_FILES_PATH}/vhost.d:/etc/nginx/vhost.d
      - ${NGINX_FILES_PATH}/html:/usr/share/nginx/html
      - ${NGINX_FILES_PATH}/certs:/etc/nginx/certs:rw
      - /var/opt/acme.sh:/etc/acme.sh
      - /var/run/docker.sock:/var/run/docker.sock:ro
    environment:
      NGINX_DOCKER_GEN_CONTAINER: ${DOCKER_GEN:-nginx-gen}
      NGINX_PROXY_CONTAINER: ${NGINX_WEB:-nginx}
    logging:
      driver: ${NGINX_LETSENCRYPT_LOG_DRIVER:-json-file}
      options:
        max-size: ${NGINX_LETSENCRYPT_LOG_MAX_SIZE:-2m}
        max-file: ${NGINX_LETSENCRYPT_LOG_MAX_FILE:-10}
```

Other services to proxy defined `VIRTUAL_HOST` and `LETSENCRYPT_HOST` environment variables.
For example this was my Nextcloud service configuration (I will only show the relevant parts):

```yaml
services:
  nextcloud:
    image: nextcloud:latest
    container_name: nextcloud
    environment:
      VIRTUAL_HOST: ${NEXTCLOUD_HOST}
      LETSENCRYPT_HOST: ${NEXTCLOUD_HOST}
      LETSENCRYPT_EMAIL: ${LETSENCRYPT_EMAIL}

```

Besides the Docker compose services configuration, I also required a Nginx configuration template (that's the *nginx.tmpl* that you can see in the configuration), and other per-service tweaks (like increasing the maximum request body size for my Nextcloud instance).

I had already replaced the Nginx webserver that hosts this blog to Caddy, so I wanted to do the same with the home server.
I decided to use [caddy-docker-proxy](https://github.com/lucaslorentz/caddy-docker-proxy) because it was similar to *nginx-proxy*, so it would simplify the migration.
What I didn't expect is how much simpler it would become.

The above configuration was replaced by:

```yaml
services:
  caddy:
    image: lucaslorentz/caddy-docker-proxy:ci-alpine
    restart: unless-stopped
    ports:
      - "${DOCKER_HTTP:-80}:80"
      - "${DOCKER_HTTPS:-443}:443"
    networks:
      - default
      - webproxy
    labels: # Global options
      caddy.email: ${CADDY_EMAIL}
      UFW_MANAGED: "true"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      # this volume is needed to keep the certificates
      # otherwise, new ones will be re-issued upon restart
      - ${CADDY_FILES_PATH}:/data
```

Proxying a service is now a matter of just adding some labels:

```yaml
services:
  nextcloud:
    image: nextcloud:latest
    container_name: nextcloud
    labels:
      caddy: ${NEXTCLOUD_HOST}
      caddy.reverse_proxy: "{{upstreams 80}}"
      caddy.request_body.max_size: ${NEXTCLOUD_MAX_UPLOAD}
```

And that was it!

[Caddy automatically manages the TLS certificates](https://caddyserver.com/docs/automatic-https), so no need for any extra services.
It doesn't get any easier than that.

I was also able to remove the Nginx config files, instead replacing them with a couple labels in the containers that required some special configuration.

Before I close off this article I want to highlight how well *nginx-proxy* and its *acme-companion* had been working for **years** with minimal maintenance.
Their stability and backwards compatibility had been rock solid, kudos and a big thanks to their creator!
