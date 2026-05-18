Title: Tailscale autoalojado, Parte 3: Syncthing sobre Tailscale
Date: 2026-05-18
Lang: es
Category: Software
Tags: howto,linux,security,syncthing,tailscale,vpn
Slug: tailscale-3-syncthing
Series: Tailscale autoalojado

Llevo años usando [Syncthing](https://syncthing.net/) para sincronizar archivos entre mi portátil, ordenador de sobremesa, teléfono, tablet y servidor. Es un programa fabuloso y ha sido muy fiable, con solo algún conflicto ocasional, pero nunca he perdido ningún dato.
Al contrario, el control de versiones de Syncthing me ha salvado el pellejo más de una vez.

Syncthing tiene sus propias soluciones para [descubrimiento](https://docs.syncthing.net/specs/globaldisco-v3.html) y [NAT traversal](https://docs.syncthing.net/specs/relay-v1.html), para que los dispositivos que están detrás de un cortafuegos puedan verse entre sí y seguir conectándose.
Sin embargo, eso depende de servidores externos para gestionar las conexiones, y podrían guardar metadatos. Incluso si no lo hacen, pueden degradar el rendimiento.

Ahora que tengo una [tailnet interconectando todos mis dispositivos]({filename}/software/2026-05-05_tailscale_part_1_es.md), no hay razón para seguir lidiando con nada de eso.
Cada dispositivo ya tiene una dirección estable accesible desde cualquier otro dispositivo.
Syncthing puede simplemente usarla, solo necesita algo de configuración.

Este artículo explica la reconfiguración de Syncthing para que use la tailnet en exclusiva, desactivando toda la maquinaria que ya no necesita.

[TOC]

## Objetivos

1. Los pares de Syncthing se comunican entre sí exclusivamente a través de la tailnet.
2. No depender de los servidores de descubrimiento global de Syncthing.
3. No depender de la red de retransmisión de Syncthing.
4. No hay necesidad de NAT traversal, lo gestiona Tailscale.
5. No hay puertos abiertos en el router, no hay necesidad de UPnP.
6. Todo sigue funcionando igual cuando estoy fuera de casa.

## Por qué hacer esto

Hay varias pequeñas victorias que van sumando:

- **Privacidad.** El descubrimiento global de Syncthing se comunica con un servidor central para anunciar `(ID de dispositivo → IP pública)`. Con la tailnet, esa difusión es inútil y se puede desactivar.
- **Fiabilidad.** Los relés son lentos y ocasionalmente inestables. Las conexiones directas a la tailnet son rápidas y consistentes, y el DERP de Tailscale ya proporciona un respaldo en la capa de red si no se puede establecer una ruta directa.
- **Simplicidad.** La dirección de cada par se convierte en una IP de tailnet fija (o nombre MagicDNS). Dejo de ver problemas de conexión entre dispositivos.
- **Seguridad.** Syncthing escucha en TCP/UDP 22000 y UDP 21027 por defecto. Si esos puertos están expuestos en la WAN, son un servicio expuesto a Internet. Desactivar todo excepto la ruta de la tailnet cierra esa puerta, reduciendo la superficie de ataque.

## Reconfiguración de Syncthing

Syncthing viene con un montón de características para que funcione a través de Internet sin configuración:

| Configuración | Predeterminado | Propósito | En tailnet |
|---|---|---|---|
| Sync Protocol Listen Addresses | `default` | Dónde aceptar conexiones entrantes | La IP tailnet del dispositivo |
| Permitir NAT traversal | Habilitado | UPnP / NAT-PMP to open ports in router | **Deshabilitado** |
| Descubrimiento global | Habilitado | Announce device ID → IP on public discovery servers | **Deshabilitado** |
| Descubrimiento local | Habilitado | LAN multicast to find peers | **Deshabilitado** |
| Habilitar retransmisión | Habilitado | Fallback traffic via public relay servers | **Deshabilitado** |

El descubrimiento global y local, el NAT traversal y la retransmisión son innecesarios entre pares que están ya conectados por Tailscale.

Cambié la configuración en cada ordenador a través de la interfaz web de Syncthing (**Acciones → Configuración → Conexiones**):

[ ![Configuración web de Syncthing]({static}/images/tailscale_part_3/syncthing_settings_web.png "Haz clic para ver en pantalla completa"){: .align-center} ]({static}/images/tailscale_part_3/syncthing_settings_web.png "Haz clic para ver en pantalla completa")

Y en los dispositivos Android en la configuración de la aplicación Syncthing (dentro de **Opciones de Syncthing**):

[ ![Configuración de Syncthing en Android]({static}/images/tailscale_part_3/syncthing_settings_android.png "Haz clic para ver en pantalla completa"){: .align-center} ]({static}/images/tailscale_part_3/syncthing_settings_android.png "Haz clic para ver en pantalla completa")

Es posible que necesites reiniciar Syncthing después de guardar.

### Acerca de las direcciones de escucha

Lamentablemente, Syncthing no admite vincularse a una interfaz específica, es decir, esto no funcionará:

``` tcp://%tailscale0:22000, quic://%tailscale0:22000 ```

Hay que vincular a la IP de la tailnet:

``` tcp://100.64.0.1:22000, quic://100.64.0.1:22000 ```

Si el dispositivo se vuelve a registrar en la tailnet y cambia su IP se romperá esta configuración, pero eso será lo suficientemente raro en mi caso como para que sea un compromiso razonable.

Una alternativa menos segura sería dejar esta configuración como `default`, lo que se vinculará a todas las interfaces, y luego confiar en el cortafuegos del dispositivo para bloquear las conexiones que no sean a través de la tailnet.

### Configurar pares por dirección de tailnet

Con el descubrimiento global desactivado, los pares ya no pueden encontrarse automáticamente.
La solución es actualizar la configuración de cada dispositivo para que apunte explícitamente a la dirección de tailnet del par:

**Dispositivo → Editar → Direcciones:**

``` tcp://homeserver.ts.fidelramos.net:22000 ```

Los nombres de host de MagicDNS funcionan bien aquí porque Syncthing resuelve la dirección en cada intento de conexión, no solo al inicio (a diferencia de las direcciones de escucha).
Si MagicDNS es inestable en un cliente en particular, se puede usar su IP de tailnet (p.ej. `tcp://100.64.0.1:22000`).

Hago este cambio entre cada par de dispositivos, en ambas direcciones.

### Cortafuegos

Dado que Syncthing solo debe ser accesible a través de la tailnet, elimino las reglas existentes que permitían las conexiones de Syncthing en mi red pública.

En mi caso, uso firewalld, eliminé las reglas de las zonas `public` y `home` y dejé que `trusted` (que está asociada a la interfaz `tailscale0`) aceptara todo automáticamente:

```bash
# Cerrar los puertos de Syncthing previamente permitidos
$ sudo firewall-cmd --permanent --zone=public --remove-port=22000/tcp
$ sudo firewall-cmd --permanent --zone=public --remove-port=22000/udp
$ sudo firewall-cmd --permanent --zone=public --remove-port=21027/udp
$ sudo firewall-cmd --permanent --zone=home --remove-port=22000/tcp
$ sudo firewall-cmd --permanent --zone=home --remove-port=22000/udp
$ sudo firewall-cmd --permanent --zone=home --remove-port=21027/udp
$ sudo firewall-cmd --reload
```

Para comprobar:

```bash
sudo firewall-cmd --zone=public --list-all sudo firewall-cmd --zone=home --list-all
```

Ninguna zona debería listar el puerto 22000 en ningún lugar.

La zona `trusted` no necesita nada listado porque es permisiva por defecto.

Para las implementaciones de Syncthing basadas en Docker, vale la pena mencionar que una configuración como `ports: ["22000:22000"]` se salta firewalld.
O bien se vincula a la IP de la tailnet (`ports: ["100.64.0.1:22000:22000/tcp"]`) o se utiliza la red del host.
En este caso las instalaciones nativas son más sencillas.

### Router

Solía tener el puerto TCP/UDP 22000 reenviado de mi router a mi servidor doméstico, y otros puertos para otros dispositivos en mi red doméstica. Ya no hace falta:

- Elimino el puerto 22000 (TCP y UDP) de las reglas de reenvío de puertos del router.
- Elimino reglas de cortafuegos en el router.

Menos puertos expuestos a Internet es **bien**.

## Verificación

La interfaz web de Syncthing es mi primera comprobación. En cada dispositivo:

- El par se muestra como **Conectado**.
- El detalle de la conexión muestra algo como `tcp://100.64.0.2:22000`, es decir, una dirección de tailnet, no una pública.
- Sin indicador de "relé".

Desde la línea de comandos en el servidor doméstico:

```bash
$ ss -tulpn | grep -E '22000|21027'
udp   UNCONN 0      0               100.64.0.4:22000      0.0.0.0:*    users:(("syncthing",pid=1526,fd=113))
tcp   LISTEN 0      4096            100.64.0.4:22000      0.0.0.0:*    users:(("syncthing",pid=1526,fd=110))
```

Syncthing sigue escuchando en el puerto 22000, pero en la IP de la tailnet.

Así está bien, firewalld asegura que solo la tailnet pueda alcanzarlo.

```bash
# La conexión a la IP pública falla
$ nc -zv 83.241.182.82 22000
nc: connect to 83.241.182.82 port 22000 (tcp) failed: Connection refused

# La conexión a la IP de la LAN falla
$ nc -zv 192.168.1.10 22000
nc: connect to 83.241.182.82 port 22000 (tcp) failed: Connection refused

# La conexión a la IP de la tailnet funciona
$ nc -zv 100.64.0.1 22000
Connection to 100.64.0.1 22000 port [tcp/snapenetio] succeeded!
```

Con Tailscale de nuevo activado, la misma comprobación a través de la dirección de tailnet debería tener éxito.

## Dificultades encontradas

### Sintaxis de la dirección de escucha `%tailscale0`

Como mencionaba anteriormente, no intentes vincular Syncthing a un nombre de interfaz.
Usa la IP de la tailnet del dispositivo, o déjalo como `default` (pero configura bien el cortafuegos).

### Los pares no se encuentran después de deshabilitar el descubrimiento

Obvio en retrospectiva, pero me pilló una vez: si la dirección de un par todavía está configurada como `dynamic` con todo el descubrimiento desactivado, no tiene forma de encontrar a nadie.
Establece direcciones explícitas para cada par.

### MagicDNS falla al inicio en un cliente lento

Si Syncthing intenta alcanzar, por ejemplo, `homeserver.ts.fidelramos.net` antes de que Tailscale esté activo en un dispositivo (por ejemplo, en un teléfono que se reinició), la conexión falla con un error de DNS. Lo intenta de nuevo unos segundos más tarde y tiene éxito. No hay nada que arreglar, es solo ruido en los registros.

Usar direcciones IP en lugar de nombres MagicDNS evita el reintento pero pierde la legibilidad y la resiliencia si un dispositivo se vuelve a registrar en Headscale.

### Syncthing usando contenedores

Si ejecutas Syncthing en Docker, la sección `ports:` de tu archivo compose no debe exponer el puerto 22000 a la WAN. Mi recomendación: ejecútalo en el host en su lugar, o usa `network_mode: host`, o vincúlalo explícitamente a la IP de la tailnet. La publicación de puertos de Docker por defecto es `0.0.0.0` y omite firewalld.

### Caché de anuncios de descubrimiento

Después de desactivar el descubrimiento global, otros usuarios de Syncthing que habían descubierto previamente mi dispositivo a través del servidor de descubrimiento público seguirían teniendo la IP pública obsoleta en caché durante un tiempo. Esto no es una fuga, es solo que intentarían conectarse a la IP antigua y fallarían. Puramente cosmético, y desaparece por sí solo en uno o dos días. No hay nada que hacer a menos que estés compartiendo carpetas con personas fuera de tu tailnet (y en ese caso, no deberías haber desactivado el descubrimiento global en primer lugar).

## Siguientes pasos

Syncthing ahora se ejecuta completamente dentro de la tailnet, sin exposición a la WAN y sin depender de la infraestructura pública de Syncthing.
He notado que los dispositivos se conectan más rápido, pero no he realizado ninguna prueba de rendimiento en las velocidades de transferencia.

En la Parte 4 haré lo mismo con mis servicios web: moveré la mayoría de mis aplicaciones de un dominio público `<app>.fidelramos.net` a `<app>.ts.fidelramos.net` solo para tailnet, utilizando una solución con doble `caddy-docker-proxy` de forma que sigan funcionando sus certificados automáticos.
