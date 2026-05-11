Title: Tailscale autoalojado, Parte 2: DNS con bloqueo de publicidad
Date: 2026-05-11
Lang: es
Category: Software
Tags: dns,howto,linux,security,tailscale,vpn
Slug: tailscale-2-ad-blocking-dns
Series: Tailscale autoalojado

En la [Parte 1]({filename}/software/2026-05-05_tailscale_part_1_es.md) configuré Headscale e hice que todos los clientes de *tailnet* usaran Cloudflare DNS.
Funcionó, pero podía ser mejor: cada dispositivo que se conecta a mi *tailnet* obtiene los servidores DNS que yo configure, así que bien podría ejecutar mi propio servidor DNS dentro de la red privada y conseguir bloqueo de anuncios, bloqueo de rastreadores y resolución de nombres interna esté donde esté, de forma transparente y cifrada.

En este artículo cambiaré Cloudflare por [Blocky](https://0xerr0r.github.io/blocky/), un proxy DNS ligero con soporte incorporado para listas de bloqueo.

Elegí Blocky en lugar de [Pi-hole](https://pi-hole.net/) o [AdGuard Home](https://github.com/AdguardTeam/Adguardhome) porque es más simple, se configura en un único archivo YAML.
No intenta ser un producto web completo, solo un servidor DNS que hace su trabajo y no molesta.

Podrías reemplazar fácilmente Blocky con algún otro servidor o proxy DNS de tu elección manteniendo las partes de Headscale y Tailscale.

[TOC]

## Objetivos

1. Bloquear anuncios y rastreadores a nivel de DNS en cada dispositivo con Tailscale.
2. Usar DNS cifrado hacia los DNS globales (*DoT* ascendente), aunque el tráfico entre mis dispositivos y Blocky ya esté protegido por WireGuard. Eso evitará el espionaje de mi ISP.
3. Tener resolución de nombres interna, que, por ejemplo, `homeserver.ts.fidelramos.net`  siga funcionando.
4. Sin configuración de DNS a nivel de dispositivo. Headscale envía la configuración y los clientes la usan automáticamente.

## ¿Por qué no usar solo el DNS privado de Android?

Android tiene una función incorporada de "DNS privado" que hace [DoT](https://es.wikipedia.org/wiki/DNS_mediante_TLS) a cualquier servicio de resolución público.
Anteriormente estaba usando un servidor DNS privado de AdGuard (`xxxxxxxx.d.adguard-dns.com`).
Intenté usarlo junto con Tailscale, pero no funciona: tan pronto como Tailscale envía cualquier configuración de DNS al cliente, Android enruta el DNS a través del túnel a través del resolvedor interno de Tailscale (`100.100.100.100`), que no habla DoT.
La sonda de DNS privado de Android falla con "no se puede conectar" y la resolución de DNS se rompe en todo el dispositivo.

Puedes deshabilitar "Usar DNS de Tailscale" en la aplicación para recuperar el DNS privado, pero entonces pierdes *MagicDNS*.

Forzado a elegir, fui por el otro camino: ejecutar mi propio DNS en la *tailnet* y hacer que Headscale lo envíe a todos los clientes.

## Arquitectura

```
  Dispositivo en la tailnet
        │
        │ DNS sin cifrar (dentro de túnel WireGuard)
        ▼
  Blocky  ──▶  listas de bloqueo (local)
        │
        │ DNS-over-TLS (DoT) a DNS global
        ▼
  Cloudflare / Quad9 / Google DNS / etc.
```

- Los clientes se comunican por DNS sin cifrar con la IP de *tailnet* de Blocky. No hace falta cifrado porque la ruta completa va por un túnel WireGuard.
- Blocky realiza el filtrado contra las listas de bloqueo que mantiene localmente.
- Todo lo que no está bloqueado se resuelve por servicios DNS globales que Blocky contacta a través de *DoT*.
- Blocky asociará algunos dominios locales de la *tailnet* a IPs internas.

## Blocky en Docker Compose

Ejecuto Blocky en el mismo proyecto *Docker Compose* donde están todos los otros servicios de mi servidor doméstico.

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

Puntos a destacar:

- **network_mode: host.** Esto es un poco perezoso por mi parte, pero abrir el puerto Docker solo a la IP de *tailnet* es más complicado de lo que parece. Blocky se configurará en la siguiente sección para que solo escuche en la interfaz de Tailscale, por lo que no creo que sea un gran riesgo de seguridad. Confío en que Blocky no vaya a escuchar en otras interfaces o puertos del sistema.
- **El archivo de configuración es de solo lectura** dentro del contenedor. Es más seguro y me recuerda que el origen es mi configuración versionada en disco, y no lo que está en el contenedor.
- Tuve que hacer `chown 100 /var/log/blocky`, ya que ese es el UID que usa el contenedor de blocky. Antes de hacerlo los registros de Docker de Blocky mostraban errores de permiso de escritura.

## Configuración de Blocky

Esta es mi configuración con los nombres internos redactados. Consulta la [documentación de Blocky](https://0xerr0r.github.io/blocky/latest/) para todos los detalles.

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

A grandes rasgos:

- **DNS global sobre DoT**: Cloudflare y Quad9 como servicios de resolución global, en paralelo, usando DNS-over-TLS para que el tráfico proveniente de Blocky esté cifrado.
- **Entradas DNS personalizadas**: algunos nombres internos que quiero resolver en toda la *tailnet* sin tocar los `extra_records` de Headscale (esto lo cubriré en la Parte 4).
- **Bloqueo**: una mezcla de listas generales y algunas listas de bloqueo específicas que me interesan. Iré ajustándolas, pero por ahora son un buen punto de partida.
- **Caché**: habilitado, con valores predeterminados sensatos.
- **Métricas de Prometheus**: desactivadas por ahora, no tengo un recolector de métricas en este momento, lo haré en mi [nuevo servidor doméstico]({filename}/software/2026-01-25_self_hosted_home_1_es.md).

Arrancarlo:

```bash
$ sudo docker compose up -d
$ sudo docker logs -f blocky
```

## Verificación desde el host:

La resolución por DNS funciona:

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

Dominio bloqueado (devuelve 0.0.0.0):
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

Blocky solo se enlaza a la IP de *tailnet*, no hay puerto DNS expuesto a Internet:

```
$ sudo ss -ulnp | grep :53
UNCONN 0      0          100.64.0.1:53         0.0.0.0:*    users:(("blocky",pid=2984612,fd=15))

$ sudo ss -tlnp | grep -E ':53|:853'
LISTEN 0      4096      100.64.0.1:53         0.0.0.0:*    users:(("blocky",pid=2984612,fd=16))
LISTEN 0      4096      100.64.0.1:853        0.0.0.0:*    users:(("blocky",pid=2984612,fd=14))
```

## Cambios en Headscale

Ahora, la magia de Tailscale: le digo a Headscale que envíe la IP de *tailnet* de Blocky como DNS global a cada cliente.
Edita `/var/opt/headscale/config/config.yaml`, su bloque `dns` cambia de la siguiente manera:

```yaml
dns:
  magic_dns: false
  override_local_dns: true        # que los clientes usen nuestro DNS, reemplazando su DNS del sistema
  base_domain: ts.fidelramos.net
  nameservers:
    global:
      - 100.64.0.1                # Blocky en la tailnet
  search_domains: []
```

Reinicia Headscale:

```bash
sudo docker compose restart headscale
```

Cada cliente tiene que obtener la nueva configuración:

- **Linux:**
```
sudo tailscale up --login-server=https://headscale.fidelramos.net --accept-dns=true
```
- **Android:** desconecta y vuelve a conectar Tailscale. También **deshabilita el DNS privado de Android** (Ajustes → Red → DNS privado → Desactivado), ya que entraría en conflicto.

Verifica desde un cliente Linux:

```bash
$ resolvectl status | grep -A2 tailscale0
# Debería mostrar 100.64.0.1 como el servidor DNS en tailscale0

$ dig example.com
# Debería resolver a través de Blocky
```

## Por qué es mejor que DoT en cada dispositivo

El cifrado es o igual o mejor:

- **Dispositivo → Blocky**: DNS sin cifrar, pero dentro de un túnel WireGuard. El ISP ve un flujo UDP al servidor doméstico, pero nada más.
- **Blocky → DNS global**: *DNS-over-TLS* cifrado. El DNS global ve la consulta del servidor, pero no qué dispositivo original la hizo.

Y hay beneficios que no tendría con sólo *DoT* en cada dispositivo:

- **Autoconfiguración**, sólo con conectarse por Tailscale.
- **Listas de bloqueo centralizadas**. Cambio un archivo y todos los dispositivos se benefician.
- **Registros de consultas por cliente** en un solo lugar. Blocky puede registrar consultas por IP de cliente.
- **Entradas DNS internas**, las usaré en la Parte 4.
- **Funciona idénticamente en todas las plataformas**, sin el baile del DNS privado de Android.
- **No es necesario cambiar la configuración del router**. Mi router actual no me permite cambiar los DNS, así que esta es una forma ingeniosa de configurar el DNS en todos mis dispositivos sin tener que ir uno por uno.

## Inconvenientes encontrados

### Android "no se puede conectar" con el DNS privado configurado

Ya lo mencioné en la Parte 1, pero vale la pena repetirlo: con el DNS de Tailscale activo, la configuración de DNS privado de Android debe estar **Desactivada** o **Automática**. Configurar un nombre de host DoT estricto rompe el DNS por completo en el dispositivo mientras Tailscale está conectado.

### La resolución de DNS se rompe en el servidor

Si el servidor usa `127.0.0.53` (*systemd-resolved*) y luego le pides que use Blocky para todo, y Blocky está en un contenedor que depende de DNS para iniciarse... puedes meterte en un callejón sin salida.

Al menos dos formas de evitarlo:

1. Deja el `/etc/resolv.conf` del host apuntando a un servicio de resolución externo (por ejemplo, Cloudflare) y solo envía Blocky a los *clientes de tailnet*. Esto es lo que yo hago: el propio host no usa Blocky, solo los dispositivos que se conectan a través de Tailscale.
2. O, fija la imagen de Blocky para que siempre esté disponible localmente y deja que Docker la inicie antes de que cualquier otra cosa necesite DNS.

### Los clientes no usan el nuevo DNS

Headscale envía la configuración de DNS en cada actualización del mapa, pero algunos clientes (especialmente Linux con NetworkManager) necesitan un empujón.
Ejecutar `tailscale up` de nuevo con `--accept-dns=true` fuerza una resincronización.
En Android, apagar y encender suele ser suficiente.

### Hay que deshabilitar MagicDNS

Si `magic_dns` se hubiera dejado habilitado en la configuración de Headscale, habría entrado en conflicto con Blocky DNS, ya que ambos intentarían usar el mismo puerto 53.

Decidí deshabilitar MagicDNS y mantener `mapping` en la configuración de Blocky de dominios e IPs.
Es un proceso manual, pero mi *tailnet* es pequeña y no cambiará mucho, así que no me importa si eso implica una configuración más sencilla.

Una solución alternativa sería ejecutar el *MagicDNS* de Headscale en un puerto diferente y luego hacer que Blocky lo use.

## Qué sigue

Con Blocky así configurado, cada dispositivo en mi *tailnet* tiene bloqueo de anuncios y DNS filtrado, a través de cualquier conexión a Internet en cualquier parte del mundo.

En la Parte 3 reconfiguraré Syncthing para usar exclusivamente la *tailnet*, deshabilitando todas sus funciones de descubrimiento y retransmisión orientadas a la WAN ahora que son innecesarias.
