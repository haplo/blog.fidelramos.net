Title: Descubrimiento de Nextcloud CardDAV y CalDAV con entradas DNS
Date: 2022-02-17
Lang: es
Category: Software
Tags: nextcloud,howto,self-hosting,dns
Slug: nextcloud-caldav-carddav-dns

Tengo una instancia propia de Nextcloud que almacena muchos de mis datos personales,
incluyendo mis contactos y mis calendarios. Recientemente tuve the reinstalar
[DAVx5](https://www.davx5.com) en mi teléfono, y me sorprendió que la cuenta de Nextcloud
daba error al intentar añadirla.

Los registros de error de DAVx5 mostraban que estaba haciendo peticiones HTTP a las URL
`/.well-known/caldav` y `/.well-known/carddav`, como describe el [RFC
6764](https://datatracker.ietf.org/doc/html/rfc6764#section-5). Nextcloud devolvía
respuestas correctas HTTP 301 redirigiendo a la dirección real para los servicios DAV de
la instancia Nextcloud, pero por alguna razón DAVx5 no estaba procesando las redirecciones
correctamente.

Leyendo la [documentación de DAVx5 sobre descubrimiento de
servicios](https://www.davx5.com/manual/accounts_collections.html#how-does-service-discovery-work)
mencionan que el standard DAV también permite definir entradas DNS de tipo SRV y TXT que
apunten a los servicios exactos a ser usados para CardDAV y CalDAV, así que decido probar
suerte porque parecía más sencillo que debuggear DAVx5 or ponerme a mirar en la
configuración de Nextcloud y/o del servidor web.

Añado estas entradas DNS a `fidelramos.net`:

``` text
_caldavs._tcp 10800 IN SRV 0 1 443 cloud.fidelramos.net.
_caldavs._tcp 10800 IN TXT "path=/remote.php/dav/"
_carddavs._tcp 10800 IN SRV 0 1 443 cloud.fidelramos.net.
_carddavs._tcp 10800 IN TXT "path=/remote.php/dav/"
```

`path` lo encuentro simplemente mirando a dónde redirigen `/.well-known/caldav` y
`/.well-known/carddav` en mi instancia de Nextcloud.

DAVx5 conectó con éxito una vez creadas las entradas DNS, pero tuve que usar
`fidelramos.net` como URL base, en vez de `cloud.fidelramos.net` como usaba antes.
