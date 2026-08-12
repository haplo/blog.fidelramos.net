Title: Tailscale autoalojado, Parte 4: Servicios web sólo en Tailscale
Date: 2026-06-04
Lang: es
Category: Software
Tags: howto,linux,seguridad,tailscale,vpn,web
Slug: tailscale-4-web-services
Series: Tailscale autoalojado

Desde hace años tengo un [servidor casero]({filename}/software/2023-12-29_homelab.md) con varios servicios autoalojados (Immich, Jellyfin, Nextcloud...) detrás de una única instancia de Caddy utilizando `caddy-docker-proxy` (documentado [en esta entrada]({filename}/software/2023-11-09_switch_nginx_caddy_docker_compose_es.md)).
Algunos de estos servicios tienen usos públicos útiles, como por ejemplo compartir una carpeta en Nextcloud o un álbum en Immich; o conectarse a Jellyfin a través de un dispositivo externo (como un Smart TV).
No obstante, la mayoría de mis interacciones son a través de dispositivos personales, así que tenerlos expuestos a la Internet pública supone un **riesgo de seguridad** considerable, dado que son puntos de entrada a mis sistemas internos.

Ahora que tengo [Tailscale funcionando]({filename}/software/2026-05-05_tailscale_part_1_es.md), la solución es hacer que el mayor número posible de servicios sean accesibles únicamente a través de la tailnet.
Para lograrlo, ejecutaré **dos instancias de Caddy en paralelo**: una vinculada a la interfaz pública, para los servicios accesibles por Internet; otra vinculada a la interfaz de Tailscale, para los servicios exclusivos de la tailnet.

La solución con `caddy-docker-proxy` no fue obvia, pero tras superar varios escollos conseguí que funcionara sin recurrir a ningún truco sucio.
En esta entrada detallo la configuración y las lecciones aprendidas.

## La arquitectura

Dos instancias independientes de Caddy en Docker, ambas utilizando `caddy-docker-proxy`:

- **`caddy-public`**: vinculada a la IP del servidor en la LAN, accesible desde Internet por el reenvío de puertos del router en los puertos 80 y 443. Gestiona los servicios públicos.
- **`caddy-tailscale`**: vinculado a la IP Tailscale del host (`100.x.y.z`), accesible únicamente desde dispositivos de mi tailnet. Se encarga de los servicios privados.

Cada Caddy supervisa las etiquetas de Docker con un prefijo diferente, por lo que los servicios se incorporan a uno u otro (o a ambos, en raras ocasiones) utilizando el prefijo de etiqueta adecuado y uniéndose a la red de Docker correspondiente.

Los servicios privados utilizan [DNS-01](https://letsencrypt.org/docs/challenge-types/#dns-01-challenge) (mediante Gandi, mi proveedor de alojamiento DNS) para obtener los certificados, dado que no son accesibles por Internet.
Los servicios públicos siguen utilizando certificados individuales normales a través de HTTP-01.

Aquí dejo un pequeño diagrama general:

```
Internet ──► router:443 ──► host:LAN_IP:443 ──► caddy-public    ──► headscale
Tailnet  ──► host:TAILSCALE_IP:443          ──► caddy-tailscale ──► immich, jellyfin, nextcloud, etc.
```

## ¿Por qué dos Caddys y no uno solo con una lista de direcciones IP permitidas?

Lo pensé.
Un único Caddy con un filtro [`remote_ip`](https://caddyserver.com/docs/modules/http.matchers.remote_ip) que restringiera ciertos nombres de dominio a `100.64.0.0/10` también funcionaría.
**Pero**:

- El puerto 443 seguiría siendo accesible desde Internet para esos dominios. Tendría que confiar en el filtrado de capa 7 para mantener en raya a atacantes de servicios que no deberían estar expuestos a la WAN en absoluto.
- Los servicios privados necesitan certificados DNS-01 (porque Let's Encrypt no puede acceder a una dirección `100.x` para HTTP-01), mientras que los servicios públicos no.
- Se te olvida incluir una etiqueta en Docker y de repente un servicio interno queda expuesto a la Internet pública.

Dos Caddys independientes me proporcionan aislamiento a nivel de red: los servicios privados, literalmente, no están a la escucha en un *socket* accesible desde la WAN.
Esa es una garantía mucho más sólida que "recibiendo peticiones pero rechazándolas".

## La configuración de Docker Compose

Esta es la estructura básica (con algunas variables de entorno para mayor claridad):

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

Algunos puntos que vale la pena destacar:

- **Espacios de nombres independientes para las etiquetas.** `CADDY_DOCKER_LABEL_PREFIX=caddy_ts` indica al Caddy de tailnet que lea las etiquetas que empiecen por `caddy_ts`. El Caddy público utiliza el valor predeterminado `caddy`. Los servicios se incorporan a uno u otro Caddy mediante el prefijo, sin posibilidad de contaminación cruzada.

- **`CADDY_INGRESS_NETWORKS`**: Cada Caddy está configurado para detectar únicamente los contenedores conectados a su propia red. Sin esto, cada Caddy intentaría actuar como proxy de todos los contenedores etiquetados que pudiera ver a través del socket de Docker, y entrarían en conflicto.

- **Volúmenes `/data` separados.** Cada Caddy tiene su propio almacenamiento de certificados. Podrían compartir un mismo volumen, pero separarlos es más limpio y elimina un caso extremo.

- **Escucha en IP específicas, no en `0.0.0.0`.** Esto me costó un buen rato depurando (lo explico más abajo).

- **Las guardas `:?` en las variables de entorno.** *Compose* usa silenciosamente `0.0.0.0` si la parte de la IP del host de una especificación de puerto está vacía. La sintaxis `:?` hace que, en cambio, falle de forma evidente y se pueda corregir. Después de tropezar dos veces con la misma piedra, pienso usar estas guardas en cualquier servicio que necesite estar vinculado a una IP específica.

## Imagen de Caddy con el complemento DNS de Gandi

Utilizo Gandi como proveedor de DNS y, por suerte, Caddy cuenta con [un complemento para ello](https://github.com/caddy-dns/gandi).
Sin embargo, la imagen `lucaslorentz/caddy-docker-proxy` no lo incluye, por lo que hay que compilarlos; no es posible añadirlos en tiempo de ejecución.
He creado una pequeña imagen personalizada mediante un archivo `Dockerfile.caddy`:

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

Gracias a `dockerfile: Dockerfile.caddy` en *compose.yml*, con `docker compose build caddy-tailscale` se realiza la compilación de la imagen.

Este patrón es habitual y [está documentado para crear imágenes personalizadas de Caddy](https://hub.docker.com/_/caddy#adding-custom-caddy-modules).

Un detalle clave es el `CMD` final. `caddy-docker-proxy` se ejecuta en un modo diferente al del servidor Caddy normal, y hay que anularlo explícitamente.

En Gandi creé un token de acceso personal con permiso para "Gestionar configuraciones técnicas de dominios".
Lo incluí en `.env` como `GANDI_BEARER_TOKEN`.

## Traslado de servicios a Tailscale Caddy

Ahora que DNS-01 debería funcionar, es el momento de trasladar mis servicios web a Tailscale.

Los cambios son sencillos: basta con ponerlos en la red `caddy_tailscale`, cambiar las etiquetas `caddy` por `caddy_ts` y ajustar los nombres de dominio a `ts.fidelramos.net`.

Por ejemplo, mi servicio Immich (muestro solo las partes relevantes):

```yaml
immich-server:
  labels:
    caddy_ts: immich.ts.fidelramos.net
    caddy_ts.reverse_proxy: "{{upstreams 2283}}"
  networks:
    - caddy_tailscale
    - immich
```

Qué maravilla, ¿no te parece?

## Configuración del DNS

No hay registros DNS públicos.
En su lugar, utilizo la opción `customDNS` de Blocky (véase la [Parte 2]({filename}/software/2026-05-11_tailscale_part_2_es.md)) para crear registros DNS que solo serán visibles para mis dispositivos de la red tailnet.

En la configuración de Blocky:

```yaml
customDNS:
  customTTL: 1h
  filterUnmappedTypes: true
  rewrite:
    ts.fidelramos.net: tail   # permite "X.ts.fidelramos.net" como alias de "X.tail"
  mapping:
    # Nombres descriptivos para los servicios en tailnet
    immich.tail: 100.64.0.1
    jellyfin.tail: 100.64.0.1
    nextcloud.tail: 100.64.0.1
```

Esto me obliga a gestionar manualmente las entradas y las direcciones IP, pero al tratarse de una modesta red doméstica, los servicios cambian con poca frecuencia y es una solución razonable.

## Verificación

Tras ejecutar `docker-compose up -d`, compruebo los registros de los contenedores para asegurarme de que todo va bien.
Las dos instancias de Caddy se inician correctamente.
`caddy-tailscale` emite nuevos certificados mediante el desafío DNS-01.

En el servidor compruebo que cada instancia de Caddy escucha en su IP asignada:

```bash
$ ss -tlnp | grep -E “:80|:443”
LISTEN 0 4096 192.168.1.50:80   0.0.0.0:*
LISTEN 0 4096 192.168.1.50:443  0.0.0.0:*
LISTEN 0 4096 100.64.0.1:80     0.0.0.0:*
LISTEN 0 4096 100.64.0.1:443    0.0.0.0:*
```

El router solo reenvía a la IP de la LAN, por lo que el Caddy de la *tailnet* es invisible para Internet.

Se puede acceder a los servicios públicos en `https://<service>.fidelramos.net` desde cualquier lugar.
Solo se puede acceder a los servicios privados en `https://<service>.ts.fidelramos.net` desde dispositivos de mi tailnet.

## Los problemas con los que me topé para que tú no tengas que hacerlo

Esta es la parte que me hubiera gustado que alguien me hubiera explicado, ya que me llevó bastante tiempo resolverla.

### Compose recurre automáticamente a `0.0.0.0`

Si escribes `${TAILSCALE_IP}:80:80` y `TAILSCALE_IP` está vacío, Docker vincula `0.0.0.0:80`.
Entonces, ambos Caddys compiten por el mismo puerto y uno falla al iniciarse con el mensaje "el puerto ya está asignado".

Utilicé `${TAILSCALE_IP:?...}` para que fallara de forma evidente si la variable de entorno no está definida.

Resolver esto fue bastante rápido, pero luego me topé con el siguiente problema...

### Los contenedores fallidos dejan zombis

Cuando un contenedor no consigue vincular sus puertos, Docker lo deja en un extraño estado intermedio: `NetworkMode` está configurado correctamente, pero el contenedor en realidad no está conectado a ninguna red.
`docker inspect` muestra `"Networks": {}`, y `ip addr` dentro del contenedor solo muestra `lo`.
Un `docker compose up -d` posterior detecta que el contenedor "existe" y simplemente lo inicia sin arreglar nada.
El resultado es un contenedor en ejecución que no tiene conectividad alguna.

La solución fue empezar de cero, con `docker compose down`, y luego `docker compose up -d`.

### La conexión de `0.0.0.0:80` entra en conflicto con `100.x.y.z:80`

Aunque ambas IP sean "válidas", Docker trata `0.0.0.0` como un superconjunto. Tenía `caddy-public` vinculado a `0.0.0.0:80` y `caddy-tailscale` vinculado a `100.64.0.1:80`, y se producían fallos intermitentes en el inicio dependiendo del orden.

La solución es fijar **ambos** a direcciones IP específicas (la IP de LAN para el público y la IP de Tailscale para tailnet).

Sin solapamientos, sin conflictos.


### `caddy-docker-proxy` necesita la red del servicio

Tanto el filtro `CADDY_INGRESS_NETWORKS` de Caddy como el enrutamiento propiamente dicho requieren que el servicio al que se aplica el proxy se encuentre en la misma red de Docker que Caddy.
Un servicio puede estar en redes adicionales (para su propia base de datos, etc.), pero necesita al menos la red de entrada de Caddy, o será invisible.

## ¿Lo volvería a hacer?

Sí.
La configuración inicial fue sorprendentemente complicada porque se acumularon múltiples fallos, pero la arquitectura resultante es limpia y fácil de ampliar.

Cada nuevo servicio que añado pasa por la misma decisión sencillísima:

* Público: etiquetas `caddy.*`, red `caddy_public`, registro DNS en Gandi.
* Privado: etiquetas `caddy_ts.*`, red `caddy_tailscale`, registro DNS en Blocky.

No hay reglas de cortafuegos que mantener sincronizadas, ni middleware de autenticación por servicio, sin ese "solo lo expondré temporalmente" que acaba convirtiéndose en permanente.

La breve lección que se desprende de todo este ejercicio: Tailscale es excelente para hacer que los servicios "solo para mí" sean accesibles desde mis dispositivos, pero integrarlo con un proxy inverso basado en Docker presenta más dificultades que cualquiera de las dos tecnologías por separado.
Vincular los listeners a direcciones IP específicas, generar un error claro cuando faltan variables de entorno y asignar a los contenedores resolutores DNS explícitos son los tres hábitos que me habrían ahorrado la mayor parte de los problemas.

## Mejoras futuras: acceso limitado para otras personas

Con esta configuración, he perdido la posibilidad de compartir un álbum de Immich con mi familia o amigos, o de compartir una carpeta de Nextcloud enviando un enlace.
Se trata de casos de uso realmente útiles que me gustaría recuperar de alguna manera.

En cuanto a mi familia, estudiaré la posibilidad de darles acceso a mi tailnet utilizando listas de control de acceso (ACL) para restringir el acceso de sus dispositivos únicamente a los servicios que necesiten.

Para compartir archivos, estoy investigando opciones como [Filestash](https://www.filestash.app/) o [FileBrowser Quantum](https://filebrowserquantum.com/), que son servicios diseñados específicamente para este caso de uso concreto.
Lo que quiero es que la interfaz de usuario de administración completa solo sea accesible a través de la red de acceso restringido, y que sus puntos finales de uso compartido público sean enrutables por Internet.

Sea cual sea la solución a la que llegue, probablemente escribiré entradas de blog al respecto.
