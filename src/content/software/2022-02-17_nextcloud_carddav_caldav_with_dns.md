Title: Nextcloud CardDAV and CalDAV discovery with DNS records
Date: 2022-02-17
Lang: en
Category: Software
Tags: nextcloud,howto,self-hosting,dns
Slug: nextcloud-caldav-carddav-dns

I use a self-hosted Nextcloud instance to hold a lot of my personal data, and that
includes my contacts and calendars. Recently I had to reinstall
[DAVx5](https://www.davx5.com) on my phone, and I was surprised that the Nextcloud account
was failing to be added.

The DAVx5 error logs showed that it was making requests to the `/.well-known/caldav` and
`/.well-known/carddav` URLs, as described in [RFC
6764](https://datatracker.ietf.org/doc/html/rfc6764#section-5). Nextcloud was returning
proper 301 HTTP responses, checked in a web browser, that redirected to the actual WebDAV
endpoint, so it looks like the problem was that DAVx5 wasn't properly following them.

Browsing the [DAVx5 documentation on service
discovery](https://www.davx5.com/manual/accounts_collections.html#how-does-service-discovery-work)
they mention that the DAV standard also supports using SRV and TXT DNS records pointing to
the endpoints to be used for CardDAV and CalDAV, and I decide to give it a go as it
sounded easier than further debugging DAVx5 or digging into Nextcloud's and/or the
webserver's configuration.

I added the following DNS records to `fidelramos.net`:

``` text
_caldavs._tcp 10800 IN SRV 0 1 443 cloud.fidelramos.net.
_caldavs._tcp 10800 IN TXT "path=/remote.php/dav/"
_carddavs._tcp 10800 IN SRV 0 1 443 cloud.fidelramos.net.
_carddavs._tcp 10800 IN TXT "path=/remote.php/dav/"
```

The `path` I find by following `/.well-known/caldav` and `/.well-known/carddav` URLs in my
Nextcloud instance.

Once the DNS records were in place DAVx5 connected successfully, but I had to use
`fidelramos.net` as the base URL, instead of `cloud.fidelramos.net` as before.
