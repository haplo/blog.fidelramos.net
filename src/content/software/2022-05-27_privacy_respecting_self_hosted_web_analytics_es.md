Title: Analítica web en tu servidor y respetuosa con la privacidad
Date: 2022-05-27
Lang: es
Category: Software
Tags: privacy,web,analytics,selfhost
Slug: privacy-respecting-self-hosted-web-analytics

Todo empezó con un anhelo: quería tener algunas analíticas básicas de este blog para saber
qué tal va, qué artículos son populares y de dónde viene el tráfico (los
*referrers*). Pero hete aquí mi problema: soy un obseso de la privacidad, me preocupa
mucho el rastreo online masivo (sólo echa un vistazo a las [extensiones de navegador web
que utilizo]({filename}2022-02-23_web_browser_addons_es.md)), así que me negaba en rotundo
a utilizar un servicio que recopilase la información de mis visitantes.

Sabía que había sistemas de analítica web de software libre. Conocía Piwik, que lleva
muchos años funcionando, pero nunca había tenido el tiempo ni la necesidad de mirarlos en
detalle. Hasta ahora.

Ojo que este artículo no presenta en absoluto una lista completa, hay muchísimas más
opciones disponibles, recopiladas en [esta enorme
lista](https://github.com/newTendermint/awesome-analytics). Cada programa tiene sus pros y
sus contras, pero espero que este artículo te ayude a elegir y dar el salto hacia
analíticas más respetuosas con la privacidad de los internautas, o al menos a abandonar
Google Analytics y elegir una opción en la nube basada en software libre.

[TOC]

# Mis requisitos

Mi búsqueda tenía unos parámetros específicos para cada proyecto:

1. Debe ser software libre y con posibilidad de alojarse en un servidor propio.

2. Despliegue sencillo, cuantos menos componentes mejor. SQLite si es posible, para no
  necesitar servidor de BD. A evitar Redis o Memcached. Estaría bien tener opción de
  despliegue sin Docker.

3. Uso razonable de recursos. Mis páginas no suelen recibir mucho tráfico, así que pienso
   reutilizar el servidor virtual de 2 GB de memoria que hospeda este blog.

4. Tecnología que pueda entender, manipular y colaborar. Yo prefiero proyectos en Python,
   pero eso ya depende de las capacidades de cada uno.

5. Ligero y no demasiado intrusivo. Sólo necesito saber qué artículos son vistos y cuándo,
   además de saber de qué otras páginas vienen los usuarios. No necesito analíticas
   avanzadas.

6. Mantenido activamente.

# Matomo (anteriormente Piwik)

[Página de inicio](https://matomo.org/)

1. GPLv3. Servicio en la nube (SAAS) con [opción auto-hospedada gratuita y
   libre](https://matomo.org/matomo-on-premise/).

2. [Documentación de instalación](https://matomo.org/faq/on-premise/installing-matomo/).
    - Necesita un servidor web (Apache, Nginx, etc.)
    - Necesita MySQL.
    - La configuración de Matomo se realiza en la propia aplicación.

3. De los [requisitos para alojar
   Matomo](https://matomo.org/faq/on-premise/matomo-requirements/):
    - <100k páginas/mes: un servidor para aplicación y BD. 2 CPU, 2 GB RAM, 50GB disco
      SSD.
    - ~1M páginas/mes: un servidor para aplicación y BD. 4 CPU, 8 GB RAM, 250GB disco SSD.
    - ~10M páginas/mes: dos servidores para aplicación y BD. 8 CPUs, 16 GB RAM, 400GB
      disco SSD
    - ~100M páginas/mes: tres o más servidores para aplicación, BD y balanceador de
      carga. 16 CPUs, 32 GB RAM, 1 TB disco SSD.

4. *Backend* en PHP. *Frontend* en VueJS y TypeScript. [Repositorio
   código](https://github.com/matomo-org/matomo) y [guía para
   desarrolladores](https://developer.matomo.org/guides/contributing-to-piwik-core).

5. Amplia gama de [métricas recopiladas](https://matomo.org/feature-overview/). Dispone de
   [plugin para Wordpress](https://matomo.org/installing-matomo-for-wordpress/).

6. Unos 10 commits por semana, múltiples [contribuidores](https://matomo.org/team/).

# Plausible

[Página de inicio](https://plausible.io/open-source-website-analytics)

1. AGPLv3. Servicio en la nube (SAAS) con [opción auto-hospedada gratuita y
   libre](https://plausible.io/self-hosted-web-analytics), pero esta última va con retraso
   en nuevas características (2 nuevas versiones cada año).

2. [Documentación oficial de
   instalación](https://plausible.io/docs/self-hosting#up-and-running). En resumen:
   necesita *docker-compose*, PostgreSQL y Clickhouse.

3. De la [documentación de requisitos de
   Plausible](https://plausible.io/docs/self-hosting#requirements):

    > The server must have a CPU with x86_64 architecture and support for SSE 4.2
    > instructions. We recommend using a minimum of 4GB of RAM but the requirements will
    > depend on your site traffic.

4. *Backend* en Elixir/Phoenix. *Frontend* en React y Tailwind. [Repositorio de
   código](https://github.com/plausible/analytics) y [guía para
   desarrolladores](https://github.com/plausible/analytics/blob/master/CONTRIBUTING.md).

5. Script de rastreo de menos de 1 KiB. Sin cookies. No pude encontrar una lista concreta
   de métricas, pero parece menos completo que Matomo u OWA.

6. Actividad semanal, normalmente condensada en *pull requests* largos.

# Shynet

[Página de inicio](https://github.com/milesmcc/shynet)

1. Apache License Version 2.0. Sólo permite hospedaje propio.

2. Despliegue sencillo con Docker o *docker-compose*, de otra forma sería un despliegue
   manual indocumentado. Soporta cualquier BD que soporte Django, incluyendo
   SQLite. Servidor de caché opcional.

3. Bajo consumo de recursos, en su forma más básica con SQLite sólo un proceso Python
   ejecutando Django, unos 100 MiB de RAM.

4. *Backend* en Python/Django. Usa su propio [plugin de
   TailwindCSS](https://github.com/milesmcc/a17t) para *frontend*. Fácil de recrear desde
   el código fuente usando Docker. [Repositorio de
   código](https://github.com/milesmcc/shynet) y [guía para
   desarrolladores](https://github.com/milesmcc/shynet/blob/master/CONTRIBUTING.md).

5. Script de rastreo de menos de 1 KiB. Sin cookies. Rastreo con pixel de 1x1 si
   javascript está desactivado. Lista bien definida de [métricas
   capturadas](https://github.com/milesmcc/shynet#metrics), todo bastante básico.

6. No tiene un fuerte desarrollo de nuevas características, pero las dependencias se
   mantienen actualizadas y el desarrollador principal responde rápido a los problemas y
   *pull requests* (lee las conclusiones para más detalles).

# Open Web Analytics (OWA)

[Página de inicio](https://www.openwebanalytics.com/)

1. GPLv2. Sólo permite hospedaje propio.

2. De la [documentación de instalación de
   OWA](https://github.com/Open-Web-Analytics/Open-Web-Analytics/wiki/Installation) y los
   [requisitos
   técnicos](https://github.com/Open-Web-Analytics/Open-Web-Analytics/wiki/Technical-Requirements):
    - Sólo soporta proyectos PHP.
    - Sistema de instalación en la propia aplicación.
    - [Sólo soporta oficialmente Apache
      2.x](https://github.com/Open-Web-Analytics/Open-Web-Analytics/wiki/Technical-Requirements#web-server). Nginx
      supuestamente funciona pero necesita configuración manual sin documentar.
    - Necesita [MySQL *con strict mode
      desactivado*](https://github.com/Open-Web-Analytics/Open-Web-Analytics/wiki/Technical-Requirements#databases=).

3. Sus requisitos exactos no están claros.

4. *Backend* en PHP. Webpack para *frontend*. Múltiples repositorios: [repositorio
   base](https://github.com/Open-Web-Analytics/Open-Web-Analytics/wiki/Installation),
   [repositorio del plugin de
   Wordpress](https://github.com/Open-Web-Analytics/owa-wordpress-plugin), [repositorio
   del SDK para PHP](https://github.com/Open-Web-Analytics/owa-php-sdk).

5. Tracking muy detallado, incluyendo mapas de calor y grabación de sesiones
   *Domstream*, pero sólo para aplicaciones PHP. Dispone de [plugins de integración
   dedicados](https://github.com/Open-Web-Analytics/Open-Web-Analytics/wiki/Integration-Plugins)
   para WordPress y MediaWiki.

6. Activamente mantenido, pero aparentemente por un único desarrollador.

# Conclusiones y mi elección

Teniendo en cuenta mi lista de requisitos la elección para este humilde blog estaba clara:
Shynet gana de calle, es justo lo que buscaba. Para páginas más grandes tanto Plausible
como Matomo parecen ser buenas opciones. Yo diría que el primero tiene mejor tecnología
fundacional (se liberó en 2019) pero Matomo lleva más tiempo funcionando (2007), está más
curtido y parece recopilar más datos. Plausible tiene [una página comparándolo con
Matomo](https://plausible.io/vs-matomo). OWA podría ser buena opción para páginas en PHP o
Wordpress.

El poder trastear con Shynet, el punto 4 en mi lista de requisitos, me vino bien en cuanto
empecé a configurarlo en mi servidor porque [el soporte de SQLite estaba
roto](https://github.com/milesmcc/shynet/issues/208). Afortunadamente [pude
arreglarlo](https://github.com/milesmcc/shynet/pull/210) y desplegarlo en el servidor en
el que estás leyendo este artículo. Por esto es que me encanta el software libre.

Otro problema con el despliegue fue que el servidor no tenía Docker instalado, y quería
mantenerlo así, por lo que aproveché la oportunidad para aprender sobre
[Podman](https://podman.io/). Me encantó su capacidad para ejecutar contenedores sin usar
*root* (*rootless containers*), eso mejora muchísimo la seguridad. El único problema que
tuve era que necesitaba cambiar los permisos del volumen de datos, porque de otra forma el
proceso Django de Shynet no era capaz de escribir la base de datos SQLite porque los
ficheros del volumen pertenecían a *root* dentro del contenedor. [Este
artículo](https://www.tutorialworks.com/podman-rootless-volumes/) lo explica muy bien,
básicamente sólo hace falta usar `podman unshare`.

Para terminar, he aquí una captura de pantalla de los datos de Shynet para este blog (¿no
es fabuloso poder compartir esto sabiendo que no se vulnera la privacidad de nadie?):

[
![blog.fidelramos.net en mi instancia de Shynet]({static}/images/privacy_respecting_self_hosted_web_analytics/shynet.png "Click to see full size"){: .align-center}
]({static}/images/privacy_respecting_self_hosted_web_analytics/shynet.png" "Click para ver a pantalla completa")
