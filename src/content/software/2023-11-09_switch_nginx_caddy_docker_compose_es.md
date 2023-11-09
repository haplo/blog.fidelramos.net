Title: Reemplazando Nginx con Caddy en Docker Compose
Date: 2023-11-09
Lang: es
Category: Software
Tags: caddy,docker,homelab,nginx
Slug: switch-nginx-caddy-docker-compose

El servidor principal de mi homelab ejecuta varios servicios, pero el corazón de todo es una configuración de [Docker Compose](https://docs.docker.com/compose/).
Varios servicios están expuestos a Internet a través de un servidor web de proxy inverso.

Antes estaba usando tres imágenes de Docker para ejecutar Nginx, dirigir el tráfico a otros servicios y generar certificados Letsencrypt para los dominios necesarios:

1. [nginx](https://hub.docker.com/_/nginx) con el servidor Nginx real en funcionamiento.
2. [nginx-proxy](https://github.com/jwilder/nginx-proxy) para generar configuraciones de Nginx.
3. [docker-letsencrypt-nginx-proxy-companion](https://github.com/jwilder/docker-letsencrypt-nginx-proxy-companion): para automatizar la provisión y renovación de certificados LetsEncrypt.

La parte relevante de la configuración en *compose.yml* lucía así:

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

Para dirigir tráfico a un servicio sólo necesitaba definir las variables de entorno `VIRTUAL_HOST` y `LETSENCRYPT_HOST`.
Por ejemplo, esta era la configuración de mi servicio de Nextcloud (solo mostraré las partes relevantes):

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

Además de la configuración de servicios en Docker Compose, también necesitaba una plantilla de configuración de Nginx (ese es el *nginx.tmpl* que puedes ver en la configuración), y otros ficheros con ajustes específicos para algunos servicios (como por ejemplo aumentar el tamaño máximo de las peticiones HTTP para mi instancia de Nextcloud).

Ya había reemplazado el servidor web Nginx que aloja este blog por Caddy, así que quería hacer lo mismo con el servidor casero.
Decidí usar [caddy-docker-proxy](https://github.com/lucaslorentz/caddy-docker-proxy) porque era similar a *nginx-proxy*, por lo que simplificaría la migración.
Lo que no me esperaba es cuán más simple se iba a volver.

La configuración anterior fue reemplazada por:

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
    labels: # Opciones globales
      caddy.email: ${CADDY_EMAIL}
      UFW_MANAGED: "true"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      # este volumen es necesario para mantener los certificados
      # de lo contrario, se emitirán nuevos al reiniciar
      - ${CADDY_FILES_PATH}:/data
```

Redirigir a un servicio ahora es solo cuestión de agregar algunas etiquetas:

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

¡Y listo!

[Caddy gestiona automáticamente los certificados TLS](https://caddyserver.com/docs/automatic-https), así que no es necesario ningún servicio adicional.
No puede ser más fácil.

También pude eliminar los archivos de configuración de Nginx, en su lugar los reemplacé con un par de etiquetas en los contenedores que requerían alguna configuración especial.

Antes de terminar este artículo, quiero destacar lo bien que *nginx-proxy* y su *acme-companion* habían estado funcionando durante **años** con un mantenimiento mínimo.
Su estabilidad y compatibilidad hacia atrás fueron increíblemente sólidas, ¡mis felicidades y agradecimientos a su creador!
