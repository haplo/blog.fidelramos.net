Title: Tailscale autoalojado, Parte 1: Headscale y clientes
Date: 2026-05-05
Lang: es
Category: Software
Tags: howto,linux,seguridad,tailscale,vpn
Slug: tailscale-1-headscale-and-clients
Series: Tailscale autoalojado

Hace bastante que oigo a mucha gente hablar maravillas de [Tailscale](https://tailscale.com/) como solución para interconectar dispositivos, o en otras palabras, para crear tu propia VPN en malla (*mesh*). Sobre el papel pinta fenomenal: fácil de configurar, rápido y ligero, basado en un protocolo abierto ([WireGuard](https://www.wireguard.com/)), funciona en todas partes, resuelve el problema de NAT... Sin embargo, me echaba para atrás el entregar mis datos a una empresa, aunque solo fueran metadatos, y que requirieran información personal para registrarse. ¿No hay una solución soberana? ¡Pues sí, la hay! Y te contaré paso a paso cómo configurarla.

El artículo oficial sobre [cómo funciona Tailscale](https://tailscale.com/blog/how-tailscale-works) me pareció muy bien explicado y aclaratorio. Si no conoces conceptos como plano de datos, plano de control, las diferencias entre redes *hub-and-spoke* y de malla, o NAT traversal, te recomiendo que le eches un vistazo. Después de todo, nuestro objetivo será autoalojar nuestro propio plano de control.

Esta es la primera entrada de una serie sobre cómo configurar una VPN de malla compatible con Tailscale autoalojada en mi servidor doméstico, sin dependencias en la nube y sin ninguna cuenta en servicios de terceros.

[TOC]

## Objetivos

1. Establecer una **VPN de malla** entre mis dispositivos (teléfono, tableta, portátil, ordenador de escritorio, servidor doméstico) para poder acceder a cualquiera de elos desde cualquier otro desde cualquier lugar de forma segura.
2. **Sin necesitar cuenta de terceros** para iniciar sesión. Nada de Google, Apple, GitHub o Microsoft.
3. **Sin servidores de terceros** involucrados en la coordinación. Mis dispositivos hablan con mi servidor, y punto.
4. Funciona en Linux y Android (las plataformas que uso), utilizando clientes de código abierto. Vale la pena señalar que otros clientes son de código cerrado, pero no me importa porque no uso esas plataformas.
5. Fácil de mantener actualizado, tanto clientes como servidor.

## ¿Por qué no usar simplemente el servicio alojado de Tailscale?

Tailscale es un gran producto y quiero ser justo al respecto: el plano de datos está cifrado de extremo a extremo con [WireGuard](https://www.wireguard.com/), por lo que Tailscale Inc. no ve el contenido del tráfico.

Pero:

- **Sí ven metadatos.** Cada cliente contacta con el plano de control para obtener el mapa de red. Eso significa que Tailscale vería la IP pública de cada dispositivo que poseo, cada vez que se conectara, desde dondequiera que estuviera. Eso es un montón de historial de ubicaciones en los registros de una empresa que preferiría evitar si puedo. Y sí que puedo, así que lo haré.
- **La identidad depende de un tercero.** La versión gratuita de Tailscale requiere iniciar sesión con Google, GitHub, Microsoft, Apple o un proveedor OIDC similar. Si alguno de ellos suspende mi cuenta, perdería el acceso a mi propia red. Amén de la pérdida de privacidad al saber que uso el servicio.
- **Es un servicio fuera de mi control.** Si Tailscale sufre una caída, cambia los precios, modifica su producto o es adquirido, mi instalación se vería afectada.

## Arquitectura

El núcleo de la arquitectura se basa en [Headscale](https://headscale.net/), una reimplementación de código abierto del servidor de coordinación de Tailscale.
Elimina las tres preocupaciones anteriores.
Los clientes oficiales de Tailscale funcionan con él sin cambios.

[ ![Arquitectura de una Tailnet con un Headscale autoalojado]({static}/images/tailscale_part_1/architecture.svg "Haz clic para ver en pantalla completa"){: .align-center} ]({static}/images/tailscale_part_1/architecture.svg "Haz clic para ver en pantalla completa")

- **Headscale** se ejecuta en Docker Compose en mi servidor doméstico, detrás de Caddy para HTTPS.
- Los **clientes de Tailscale** se ejecutan en cada dispositivo, configurados para usar mi instancia de Headscale como servidor de control. Cada cliente informa al servidor sobre su situación de red y, a cambio, obtiene conexiones a los otros nodos.
- **DNS** en esta primera parte utiliza Cloudflare. En la segunda parte lo reemplazaré por un servidor DNS Blocky autoalojado con bloqueo de anuncios y rastreadores que usarán automáticamente todos los clientes de mi Tailnet.
- Los clientes establecen túneles WireGuard directos entre pares; los [relés DERP](https://tailscale.com/docs/reference/derp-servers) públicos de Tailscale se utilizan solo como respaldo.

## Requisitos previos

- Un dominio bajo mi control (`fidelramos.net`).
- Una forma de que mi servidor doméstico sea accesible desde Internet en los puertos 80 y 443. Utilizo DNS dinámico porque mi ISP me da una IP pública dinámica. Mi servidor actualiza periódicamente un registro A que apunta `headscale.fidelramos.net` a mi IP actual. Si tienes una IP estática, pues mejor que mejor.
- El router reenvía los puertos TCP 80 y 443, y el puerto UDP 41641 a mi servidor doméstico. Mi servidor está en la DMZ del router, así que esto es automático.
- Mi servidor, ejecutando Debian con Docker y Docker Compose instalados y configurados.
- Caddy con caddy-docker-proxy como proxy inverso. Ya escribí sobre esa configuración [en esta entrada anterior]({filename}/software/2023-11-09_switch_nginx_caddy_docker_compose_es.md). Es la forma más sencilla que he encontrado para tener un proxy inverso habilitado para HTTPS. Realmente me encanta.

## Headscale en Docker Compose

Tengo un proyecto *compose* con otros servicios, incluido un servicio `caddy` con `caddy-docker-proxy` como se describe en la entrada ya mencionada.

Añadí un servicio `headscale` a `compose.yml`:

```yaml
services:
  headscale:
    image: headscale/headscale:stable
    container_name: headscale
    restart: unless-stopped
    command: serve
    volumes:
      - ${HEADSCALE_ROOT}/config:/etc/headscale
      - ${HEADSCALE_ROOT}/data:/var/lib/headscale
    networks:
      - caddy
    labels:
      caddy: headscale.fidelramos.net
      caddy.reverse_proxy: "{{upstreams 8080}}"
```

Algunos puntos a destacar:

- `image: headscale/headscale:stable` sigue la última versión estable. Lo combino con [WUD](https://getwud.github.io/wud/) para actualizaciones controladas (escribiré una futura entrada al respecto). Por supuesto, puedes hacer un `docker compose pull` manual.
- No hay sección `ports:`. Headscale solo se alcanza internamente a través de Caddy.
- Establezco mi `HEADSCALE_ROOT` en `/var/opt/headscale`, pero puedes usar el directorio que tenga sentido para ti.
- Las dos etiquetas son todo lo que `caddy-docker-proxy` necesita para enrutar `headscale.fidelramos.net` al puerto 8080 del contenedor.

## Configuración de Headscale

Lo puse en `/var/opt/headscale/config/config.yaml`, pero puedes ponerlo donde te funcione, solo ajusta el mapeo de volumen en la configuración de compose.

```yaml
server_url: https://headscale.fidelramos.net
listen_addr: 0.0.0.0:8080
metrics_listen_addr: 0.0.0.0:9090
grpc_listen_addr: 0.0.0.0:50443
grpc_allow_insecure: false

noise:
  private_key_path: /var/lib/headscale/noise_private.key

prefixes:
  v4: 100.64.0.0/10
  v6: fd7a:115c:a1e0::/48
  allocation: sequential

derp:
  server:
    enabled: false
  urls:
    - https://controlplane.tailscale.com/derpmap/default
  auto_update_enabled: true
  update_frequency: 24h

disable_check_updates: true
ephemeral_node_inactivity_timeout: 30m

database:
  type: sqlite
  sqlite:
    path: /var/lib/headscale/db.sqlite

log:
  level: info
  format: text

dns:
  magic_dns: true
  override_local_dns: true
  base_domain: ts.fidelramos.net
  nameservers:
    global:
      - 1.1.1.1
      - 1.0.0.1
  search_domains: []

unix_socket: /var/run/headscale/headscale.sock
unix_socket_permission: "0770"

policy:
  mode: file
  path: ""
```

Estos son los puntos más importantes:

- `server_url` es la URL HTTPS pública para el plano de control. Debe ser accesible por los clientes.
- `base_domain` es el sufijo utilizado por MagicDNS para los nombres de host de tailnet (por ejemplo, `homeserver.ts.fidelramos.net`). **No debe ser igual ni padre de** el dominio `server_url`, si no los clientes se confunden.
- `dns.nameservers.global` son los servidores DNS que se envían a cada cliente. En esta configuración uso Cloudflare; en la Parte 2 lo cambiaré para usar una instancia de Blocky.
- DERP está deshabilitado para el servidor y utiliza el mapa DERP público de Tailscale como relés de respaldo para los clientes. Usar sus DERP no filtra tráfico (es WireGuard retransmitido, siempre cifrado de extremo a extremo) pero es la única pieza no autoalojada, es un compromiso razonable para mi caso.

## Registros DNS

Solo uno: un registro A para `headscale.fidelramos.net` que apunta a la IP pública de mi servidor doméstico (a través de DDNS).
Ahí se conectan los clientes y es el dominio que Let's Encrypt verificará con HTTP-01 a través de Caddy.

`ts.fidelramos.net` (el `base_domain`) **no** obtiene un registro DNS público.
Se resuelve completamente dentro de la tailnet por MagicDNS de Tailscale.
Esto significa que solo mis clientes de Tailscale podrán acceder a estos dominios, y no se publicarán en ningún lugar.

## Primera ejecución

En el proyecto Docker compose:

```bash
sudo docker compose up -d
sudo docker logs -f headscale
```

Una vez que los registros muestren que la API está escuchando y Caddy ha obtenido un certificado, confirmo que el plano de control es accesible:

```bash
curl https://headscale.fidelramos.net/health
```

Debería devolver `{"status":"pass"}`.

## Creación de un usuario y claves de preautenticación

Headscale utiliza **usuarios** como espacios de nombres que poseen dispositivos.
Creo uno para mí:

```bash
sudo docker compose exec headscale headscale users create fidel
```

Luego genero una clave de preautenticación cada vez que necesito registrar un nuevo dispositivo:

```bash
sudo docker compose exec headscale headscale preauthkeys create --user 1 --expiration 1h
```

La clave solo es válida por una hora.
Suficiente para registrar un dispositivo y no tener que preocuparme por si se filtra.

## Tailscale en Linux

Debian:

```bash
CODENAME=$(lsb_release --codename --short)
curl -fsSL https://pkgs.tailscale.com/stable/debian/$CODENAME.noarmor.gpg | \
  sudo tee /usr/share/keyrings/tailscale-archive-keyring.gpg >/dev/null
curl -fsSL https://pkgs.tailscale.com/stable/debian/$CODENAME.tailscale-keyring.list | \
  sudo tee /etc/apt/sources.list.d/tailscale.list
sudo apt update
sudo apt install -y tailscale
sudo systemctl enable --now tailscaled
```

Fedora:

```bash
sudo dnf config-manager addrepo --from-repofile=https://pkgs.tailscale.com/stable/fedora/tailscale.repo
sudo dnf install tailscale
sudo systemctl enable --now tailscaled
```

Arch Linux y derivados:

```bash
pacman -S tailscale
sudo systemctl enable --now tailscaled
```

Para todos los sistemas, una vez que Tailscale esté habilitado, registro el dispositivo con Headscale usando una clave de preautenticación:

```bash
sudo tailscale up \
  --login-server=https://headscale.fidelramos.net \
  --auth-key=<preauth-key> \
  --hostname=$(hostname)
```

Para verificar:

```bash
# on client
tailscale status
# on server
sudo docker compose exec headscale headscale nodes list
```

El nodo debería aparecer en ambas listas, con una dirección `100.64.0.x`.

## Tailscale en Android

La aplicación de Android se comunica con Tailscale público por defecto y no hay una configuración obvia para cambiarlo.
Considero esta ofuscación un patrón oscuro, pero comprensible ya que quieren tener un negocio exitoso.
Aún así fue exasperante tener que buscar cómo hacerlo a pesar de saber que la opción estaba ahí escondida en algún lugar.

El truco es la opción de **servidor alternativo**, que está oculta:

1. Instala la aplicación Tailscale desde F-Droid, la Play Store o, mi forma elegida, a través de [Obtanium](https://obtainium.imranr.dev/) usando [https://pkgs.tailscale.com/stable/tailscale-android-universal-latest.apk](https://pkgs.tailscale.com/stable/tailscale-android-universal-latest.apk) como fuente.
2. Inicia la aplicación y cancela el intento de iniciar sesión en Tailscale.
3. Una vez que llegues a la pantalla con el botón Conectar, toca el engranaje para el menú de configuración, y después dale a **Cuentas**.
4. En el menú superior derecho de esa pantalla, elige **Usar un servidor alternativo**.
5. Introduce tu servidor Headscale (en mi caso `https://headscale.fidelramos.net`).
6. Inicia sesión. Se abrirá una página en el navegador con instrucciones sobre qué ejecutar en el servidor Headscale para registrar este cliente.
7. Como se indica, ejecuta el comando en el servidor headscale:

```bash
sudo docker compose exec headscale headscale nodes register \ --user 1 \ --key nodekey:abcdef...
```

Si quieres una guía visual, encontré este vídeo con instrucciones paso a paso:

<div class="youtube" align="center">
<iframe width="800" height="500" src="https://www.youtube.com/embed/ofVyohBLuPg?si=h4qve8iXcedCvquO&amp;start=1161" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>
</div>

Después del registro, activa el interruptor de conexión en la aplicación.
`tailscale status` en un dispositivo Linux en la tailnet debería mostrar el teléfono, y debería aparecer en la lista de nodos de Headscale como se mencionó en la sección del cliente Linux.

Mencionaré una cosa específica de Android: Tailscale se añade como un servicio VPN, y al menos en mis dispositivos se marcó como *siempre activo* y también el *bloquear conexiones sin VPN*.
Recomiendo dejar *siempre activo* habilitado, pero **deshabilitar el bloqueo de conexiones sin VPN**.
Como Tailscale es una VPN solo entre tus dispositivos, si se cae no pierdes anonimato como con una VPN de reenvío de tráfico, simplemente pierdes el acceso a los pares de la VPN.

[
![Configuración de VPN de Android]({static}/images/tailscale_part_1/android_vpn_settings.png "Haz clic para ver en pantalla completa"){: .align-center} ]({static}/images/tailscale_part_1/android_vpn_settings.png "Haz clic para ver en pantalla completa")

## Otros clientes

Solo uso Linux y Android, así que eso es lo que he cubierto y probado.
Para otras plataformas, los clientes de Tailscale funcionan de la misma manera, simplemente apúntalos al servidor alternativo y regístrate.
El proyecto Headscale mantiene [instrucciones actualizadas para macOS, iOS y Windows](https://headscale.net/stable/usage/connect/) que no duplicaré aquí.

## Dificultades encontradas

Recopilo aquí algunos problemas que encontré en el camino, por si le puedo ahorrar sufrimiento a alguien.

### Clave incorrecta

Si pasas la clave incorrecta a `headscale nodes register`, obtendrías el siguiente error:

`Cannot register node: node not found in registration cache`

El valor esperado es la cadena `nodekey:...` de la URL del navegador del cliente, **no** una clave de preautenticación.
Las claves de preautenticación se utilizan en el lado del cliente con `tailscale up --auth-key=...`, no en el servidor.

La caché de registro está en memoria y caduca después de ~15 minutos, así que si te tomas un descanso para comer entre el inicio de sesión del cliente y el comando del servidor, vuelve a activar el inicio de sesión en el cliente para generar una nueva.

### El dispositivo Android aparece con nombre `invalid-...` en headscale

Headscale rechaza los nombres que no son etiquetas DNS válidas (espacios, caracteres *unicode*, etc.).
Android envía el nombre de dispositivo legible por humanos, lo que a menudo falla esta verificación (por ejemplo, "Pixel 8 Pro" en mi caso).
Headscale renombra el nodo automáticamente a `invalid-<hash>`.

Puedes renombrarlo en el servidor Headscale después del registro:

```bash sudo docker compose exec headscale headscale nodes rename -i <node-id> pixel8pro ```

Puramente cosmético, pero MagicDNS no funcionará para el nombre original hasta que hagas esto.

### Android "No conectado" sin error

Si la aplicación muestra la cuenta de Headscale pero se queda en "No conectado" cuando activas la conexión, algunas cosas que debes verificar en orden:

1. Comprueba `sudo docker compose logs -f headscale` mientras activas. Deberías ver al cliente accediendo a `/ts2021`. Si no aparece nada, no está llegando al servidor. Podría ser un problema de TLS (comprueba los registros de caddy), DNS, firewall...
2. Desde el navegador del teléfono, `https://headscale.fidelramos.net/health` debe tener éxito.
3. Comprueba que DERP se cargó: `sudo docker compose exec headscale headscale debug derp` debería listar las regiones. Si está vacío, el contenedor no puede alcanzar `controlplane.tailscale.com` para el mapa, primero corrige el DNS del contenedor o su salida a Internet.
4. **DNS privado de Android**: esto merece una sección propia.

### El DNS privado de Android interfiere con el arranque de Tailscale

Estaba usando AdGuard DNS como DNS privado personalizado, pero se rompió cuando Tailscale se conectó, dejándome sin una configuración DNS válida, por lo que la mayoría de las conexiones a Internet no funcionaban.

Vi dos errores:

- En la configuración de red de Android, *DNS privado* decía *no se pudo conectar*.
- Poco después de configurar el DNS privado personalizado, saltaba una notificación: *La red no tiene acceso a Internet. No se puede acceder al servidor DNS privado.*

Afortunadamente, pude sortear este problema autoalojando mi propio DNS de bloqueo de anuncios y haciendo que todos mis clientes de Tailscale lo usaran.
Esto acabó siendo una bendición, ya que ganaba control total sobre el DNS y ya no tendría que pagar por AdGuard DNS.

Esta solución se presentará en la próxima Parte 2 de esta serie de artículos.

### MagicDNS no resuelve en un dispositivo específico

Después de cambiar la configuración de DNS de Headscale, los clientes necesitan obtener nuevas configuraciones.

En Linux, `sudo tailscale up --login-server=... --accept-dns=true` resincroniza.

En Android, activa y desactiva el interruptor de la VPN.

### Desfase horario

El intercambio de ruido de Tailscale falla silenciosamente si hay una deriva de reloj significativa.
Si nada más explica un problema de conexión, comprueba que NTP (sincronización de tiempo) esté funcionando en ambos extremos.

En Linux configura *systemd-timesyncd*, *ntpd*, *chrony* o similar.

En Android, pon la configuración de fecha/hora en "automático" en la configuración del sistema.

## Siguientes pasos

Esta configuración ya es funcional: mis dispositivos pueden comunicarse entre sí a través de mi propio servidor de control, sin Tailscale ni cuentas o servicios de terceros.
Puedo acceder desde cualquier parte a aplicaciones que antes solo eran accesibles a través de la LAN.

En la Parte 2, cambiaré el DNS de Cloudflare configurado actualmente por una instancia de Blocky autoalojada para obtener bloqueo de anuncios y rastreadores y conseguir resolución de nombres internos en cada cliente de la tailnet.
