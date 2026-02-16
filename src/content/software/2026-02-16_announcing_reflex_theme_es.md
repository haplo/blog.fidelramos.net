Title: Anunciando Reflex, un tema para Pelican
Date: 2026-02-16
Lang: es
Category: Software
Tags: free-software,pelican
Slug: announce-reflex-theme

Me complace anunciar la disponibilidad pública de mi tema para Pelican: [Reflex](https://github.com/haplo/python-theme-reflex).
Está [publicado en PyPI](https://pypi.org/project/pelican-reflex/), esa deber'ia ser la mejor forma de instalarlo para la mayoría de los usuarios.

Cuando empecé este blog, me decidí por [Pelican](https://getpelican.com/) porque tenía mucha experiencia con Python, así que me resultaría más fácil involucrarme y contribuir.
Luego eché un vistazo a todos los [temas de Pelican](http://www.pelicanthemes.com/) y me decanté por el [tema Flex de Alexandre Vizenzi](https://github.com/alexandrevicenzi/Flex) porque cumplía todos mis requisitos:

- Minimalista y bonito.
- Diseño flexible para distintas pantallas (*responsive*).
- Soporte para archivos, categorías y etiquetas.
- Soporte de Pygments para resaltado de código.
- Soporte para modos claro/oscuro.

Como era inevitable, al final me topé con algunas funciones que echaba en falta y pequeños retoques que quería implementar.
Esa es la belleza del software libre, y empecé a [contribuir en Flex](https://github.com/alexandrevicenzi/Flex/pulls?q=is%3Apr+author%3Ahaplo+).
Sin embargo, algunos de los cambios que quería hacer eran demasiado profundos y no encajaban en Flex, ya que el proyecto estaba en modo de mantenimiento.
Después de pensarlo un poco, decidí hacer un *fork* del tema para introducir mis cambios más rompedores, y así es como nació Reflex.

Las **principales diferencias con Flex** por ahora son:

- Estilo para la tabla de contenidos creada por la extensión de Markdown *toc*.
- Estilos para los elementos HTML `figure` y `figcaption`.
- Soporte para analíticas de tráfico con Shynet (ver [mi artículo sobre comentarios autoalojados]({filename}2025-02-10_self_hosted_comments_es.md)).
- Documentación en el propio repositorio en lugar de en la wiki de Github.
- Visualización de banderas de idioma para los idiomas alternativos del artículo.
- Icono de la red social X.
- Mejoras en la experiencia de desarrollo: soporte para `gulp watch` para ver cambios al instante, *AGENTS.md* para el desarrollo con IA, flujos de trabajo con GitHub Actions renovados.
- Estilos de Pygments y FontAwesome actualizados.

No tengo grandes planes para Reflex, principalmente implementaré los cambios que me parezcan útiles para este blog.
Estoy abierto a nuevas integraciones e ideas, ¡así que bienvenidos sean los colaboradores!

Para ver los errores conocidos y las funcionalidades planeadas, echa un vistazo a las [incidencias abiertas](https://github.com/haplo/pelican-theme-reflex/issues).
Para cualquier pregunta, no dudes en abrir un [hilo de discusión](https://github.com/haplo/pelican-theme-reflex/discussions).

Si usas Reflex, anímate a añadir tu sitio a la [lista de usuarios de Reflex](https://github.com/haplo/pelican-theme-reflex?tab=readme-ov-file#sites-using-reflex), ¡me encantaría saber de ti!
