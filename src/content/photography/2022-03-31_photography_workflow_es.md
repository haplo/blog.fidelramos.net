Title: Mi proceso fotográfico con software libre
Date: 2022-03-31
Modified: 2022-04-05
Lang: es
Category: Photography
Tags: fotografía,software-libre
Slug: photography-workflow

En este artículo presento una guía paso a paso de mi proceso fotográfico. No voy a meterme
en todos los detalles de todos los programas que menciono, dado que ya tienen su propia
documentación y manuales, me limitaré a resaltar las operaciones que realizo.

Mis objetivos principales son:

1. Control total sobre todos mis datos, sin servicios externos.
2. Uso exclusivo de software libre.
3. Rapidez en las operaciones habituales: descarga de nuevas fotos, edición, post-procesado.
4. Organizar la colección con metadatos.
5. Sincronización y backup automáticos.
6. (A futuro) Acceso y compartición transparente de las fotos.

[TOC]

## 1. Descargar fotos con Digikam

Uso el fantástico programa [Digikam](https://www.digikam.org/) para organizar mi colección
de fotos (181708 fotos y 3127 vídeos en 2198 álbumes a fecha de marzo 2022). Descargo las
fotos de mis cámaras con Digikam porque tiene un filtro muy útil "Sólo elementos nuevos"
(_Only new items_), de forma que cuando conecto la cámara sólo veo los nuevos contenidos.

Tengo dos colecciones de fotos en Digikam: _Fotos_ y _Fotos por ordenar_. La primera son
las fotos que ya están procesadas y organizadas, y se sincroniza con mi servidor casero;
la segunda es donde descargo las nuevas fotos para procesarlas y organizarlas, y luego las
muevo a _Fotos_ cuando están listas.

La mayoría de mis fotos están clasificadas en álbumes por fecha, y Digikam también es de
ayuda para esto porque se pueden seleccionar las fotos a descargar por fecha, haciendo
click en el título de sección, luego uso la opción "Descargar seleccionadas" (_Download
Selected_).

[
![Importar desde cámara en Digikam]({static}/images/photography_workflow/digikam_import.jpg "Click para ver a pantalla completa"){: .align-center}
]({static}/images/photography_workflow/digikam_import.jpg "Click para ver a pantalla completa")

Digikam entonces pregunta dónde descargarlas, y ahí directamente puedo crear un nuevo álbum:

[
![Crear nuevo álbum en Digikam durante la importación]({static}/images/photography_workflow/digikam_import_create_new_album.png "Click para ver a pantalla completa"){: .align-center}
]({static}/images/photography_workflow/digikam_import_create_new_album.png "Click para ver a pantalla completa")

Le pongo la categoría, descripción y fecha al álbum directamente, para que no se me olvide hacerlo después:

[
![Ventana de nuevo álbum en Digikam]({static}/images/photography_workflow/digikam_new_album.png "Click para ver a pantalla completa"){: .align-center}
]({static}/images/photography_workflow/digikam_new_album.png "Click para ver a pantalla completa")

## 2. Revisar con Geeqie

Cuando se han descargado todas las fotos cambio a [Geeqie](https://www.geeqie.org/) para
verlas y borrar las malas (desenfocadas, borrosas, sobreexpuestas o subexpuestas, etc.) Lo
llevo usando desde que se llamaba GqView, hay muchos otros visores de imágenes pero ya
estoy acostumbrado a éste.

En este punto necesito mencionar que en mis cámaras uso el modo JPEG+RAW, aunque siempre
postprocese el RAW y borre los JPEG creados por la cámara. La razón es que me gusta poder
hacer zoom al 100% para ver los detalles de las fotos y borrar las malas lo antes posible,
y las imágenes RAW normalmente tienen las previsualizaciones a tamaño reducido (por
ejemplo los ficheros RAW creados por mi Sony A7 III tienen una previsualización de
1616x1080 píxeles, lo que es pequeño para una pantalla 4K).

Hay dos características imprescindibles para mí en esta fase:

1. Agrupar los ficheros para ver sólo los JPEG, pero borrar todos los ficheros de un grupo.
2. Mantener el zoom y la posición de la vista cuando se cambia de imagen.

El agrupado de ficheros significa que por defecto Geeqie sólo muestra el fichero JPEG,
mientras que los ficheros RAW y potencialmente otros (por ejemplo _sidecars_ como XMP o
PP3) se ocultan, pero pueden verse expandiendo el grupo con un click. De esta forma cuando
se borra un grupo se borran todos los ficheros, no sólo el JPEG. Geeqie reconoce la
mayoría de ficheros _sidecar_, pero si es necesario se puede configurar en las
_Preferencias_:

[
![Configuración del agrupado de sidecar en Geeqie]({static}/images/photography_workflow/geeqie_sidecar_grouping.jpg "Click para ver a pantalla completa"){: .align-center}
]({static}/images/photography_workflow/geeqie_sidecar_grouping.jpg "Click para ver a pantalla completa")

La otra característica que necesito es el poder hacer zoom al 100% en una foto, cambiar a
la foto siguiente o anterior para compararlas, y que la vista se mantenga en la misma
posición, es decir que no se resetee a la esquina superior izquierda o algo así como hacen
otros visores. Geeqie tiene este comportamiento por defecto, combinado con sus atajos de
teclado (_Z_ para zoom 100%, _X_ para zoom ajustado a la ventana, _AvPág_ y _RePág_ para
cambiar de imagen) me funciona muy bien.

Quiero mencionar que soy consciente de que Digikam tiene una funcionalidad para ver las
fotos y compararlas por parejas (_Lightroom_ en inglés): se ve una imagen a la izquierda,
la siguiente en la derecha, y cuando se cambia el zoom o se mueve la vista ambos paneles
se mantienen en sincronía. Pinta perfecto pero tiene un gran inconveniente para mí: cuando
borro una foto no borra el fichero RAW asociado, lo deja huérfano. No he encontrado una
forma de resolver esto en Digikam, lo que puedo hacer es ejecutar un comando para borrar
todos los ficheros huérfanos, o echar las fotos sólo en formato RAW (pero entonces
perdería resolución de previsualización). Por esta razón sigo usando Geeqie.

[
![Digikam Lightroom]({static}/images/photography_workflow/digikam_lightroom.jpg "Click para ver a pantalla completa"){: .align-center}
]({static}/images/photography_workflow/digikam_lightroom.jpg "Click para ver a pantalla completa")

## 3. Procesado de RAW con RawTherapee

Actualmente proceso la mayoría de mis fotos con [RawTherapee](https://rawtherapee.com/),
un fabuloso software libre que es a la vez fácil de usar y produce fotos de muy alta
calidad. En el pasado he usado también [Darktable](https://www.darktable.org/), pero
aunque tiene más funcionalidades me costaba más tiempo y esfuerzo lograr los resultados
que suelo buscar, sobre todo porque la reducción de ruido de RawTherapee funciona mucho
mejor.

En cualquier caso, abro el directorio con el álbum en RawTherapee, aplico un [perfil
base](https://rawpedia.rawtherapee.com/Creating_processing_profiles_for_general_use) a
todas las fotos y luego aplico perfiles parcialmente para aclarar (_sharpen_) imágenes con
bajo ruido, aplicar una leve reducción de ruido a las imágenes con ISO intermedio y
reducción de ruido agresiva para aquellas con ISOs elevados. Uso el filtrado para primero
seleccionar sólo los ficheros RAW y luego aplico subfiltros por ISO.

[
![Filtrado en RawTherapee]({static}/images/photography_workflow/rawtherapee_filter.jpg "Click para ver a pantalla completa"){: .align-center}
]({static}/images/photography_workflow/rawtherapee_filter.jpg "Click para ver a pantalla completa")

[
![Perfiles de procesado en RawTherapee]({static}/images/photography_workflow/rawtherapee_profiles.png "Click para ver a pantalla completa"){: .align-center}
]({static}/images/photography_workflow/rawtherapee_profiles.png "Click para ver a pantalla completa")

Después aplico corrección a la distorsión de lente a todas las fotos. La detección
automática de lente me falla por alguna razón que desconozco, así que uso el proceso en
grupo (_Batch Edit_), selecciono todas las fotos en el álbum y selecciono manualmente la
cámara y lente.

[
![Correción de distorsión de lente en RawTherapee]({static}/images/photography_workflow/rawtherapee_batch_edit.png "Click para ver a pantalla completa"){: .align-center}
]({static}/images/photography_workflow/rawtherapee_batch_edit.png "Click para ver a pantalla completa")

Lo siguiente es revisar las fotos una por una, haciendo ajustes: exposición, balance de
blancos, recorte, etc. No voy a entrar en detalles porque es edición normal con
RawTherapee. Si te interesa saber más no dudes en enviarme un mensaje y consideraré hacer
un artículo o vídeo al respecto.

Cuando todo está listo pongo las fotos en la cola (_Queue_) y las exporto al mismo
directorio donde están los ficheros RAW (`%p1/%f` como la plantilla en _Output
Location_). Cuando necesito retocar alguna foto después del revelado (normalmente en GIMP)
entonces uso formato TIFF, dado que JPEG es un formato con pérdida y perdería calidad si
se vuelve a modificar.

[
![Cola en RawTherapee]({static}/images/photography_workflow/rawtherapee_queue.jpg "Click para ver a pantalla completa"){: .align-center}
]({static}/images/photography_workflow/rawtherapee_queue.jpg "Click para ver a pantalla completa")

## 4. Organizar en Digikam

Cuando RawTherapee ha terminado de guardar las fotos borro los JPEG generados por la
cámara, luego vuelvo a Digikam y refresco (_Refresh_) el álbum para ver los nuevos
ficheros.

Lo siguiente es agrupar las fotos por nombre, para ver sólo los JPEG y no los RAW. En el
álbum selecciono todos los ficheros (CTRL+A) y luego con un click derecho en cualquier
imagen *Agrupar* &rarr; *Agrupar seleccionados por nombre de fichero*.

[
![Agrupar ficheros en Digikam: antes y después]({static}/images/photography_workflow/digikam_group.jpg "Click para ver a pantalla completa"){: .align-center}
]({static}/images/photography_workflow/digikam_group.jpg "Click para ver a pantalla completa")

A continuación uso la [detección de
caras](https://docs.kde.org/trunk5/en/digikam-doc/digikam/using-digikam.html#using-mainwindow-peopleview)
para que Digikam reconozca las caras de las personas en las fotos. Selecciono todas las
fotos (CTRL+A), click derecho y *Escanear caras* (_Scan for Faces_). Cuando el proceso
termina voy a la pestaña de *Personas* (_People_) en la izquierda para revisar los
resultados, aceptar los buenos y corregir los malos.

Después reviso las etiquetas. La organización por etiquetas es algo personal, pero yo
aprovecho que las etiquetas en Digikam tienen una estructura jerárquica, de forma que por
ejemplo uso etiquetas para la localización como `place` &rarr; `Colombia` &rarr;
`Zapatoca`. En este punto también me aseguro que todas las personas estén etiquetadas,
dado que el reconocimiento facial falla a veces, y me gusta tener etiquetado a todo el
mundo para poder filtrar más adelante de forma efectiva.

[
![Etiquetas en Digikam]({static}/images/photography_workflow/digikam_tags.png){: .align-center}
]({static}/images/photography_workflow/digikam_tags.png)

Para acelerar el etiquetado le asigno atajos de teclado a las etiquetas que uso más
habitualmente. Es sólo cuestión de editar las propiedades de una tag con un click derecho
y luego asignarle el atajo deseado:

[
![Editar etiqueta en Digikam]({static}/images/photography_workflow/digikam_edit_tag.png){: .align-center}
]({static}/images/photography_workflow/digikam_edit_tag.png)

El último paso es puntuar las fotos con 1 a 5 estrellas. Hago doble click en la primera
foto del álbum, uso los atajos de teclado para asignarle la puntuación deseada (de CTRL+1
a CTRL+5, esos son atajos por defecto) y las teclas de cursor atrás y adelante para
cambiar de foto. El significado de las puntuaciones es también algo personal, pero esta es
la lógica que uso yo para mi colección:

- *1 estrella*: Mala calidad o duplicado. No merece la pena verse salvo que busque algo
  específico. Si le estuviese mostrando el álbum a alguien probablemente excluiría esta
  foto.
- *2 estrellas*: Mi puntuación por defecto en caso de duda. No tiene mala calidad y puede
  ser interesante, pero tampoco es fundamental para el álbum.
- *3 estrellas*: Una foto representativa del álbum en el que se encuentra, es decir que si
  le mostrase a alguien sólo las fotos de 3 o más estrellas vería lo mejor del álbum sin
  tener que aguantar demasiadas fotos.
- *4 estrellas*: Buena foto: enfocada, buena iluminación y composición. Si me puede
  interesar buscar una foto como independiente de su álbum eso significa que es de 4
  estrellas.
- *5 estrellas*: Gran foto, o bien por sus características artísticas y técnicas o porque
  tiene un significado especial para mí (buena foto de mi hija, por ejemplo). Foto de la
  que me siento orgulloso.

Esta organización me permite luego filtrar mi colección para encontrar lo que quiera, por
ejemplo todas las fotos con todos los miembros de mi familia con 4 estrellas o más, y
quizá filtrar por fecha también.

Cuando termino de organizar el álbum lo muevo de mi colección _Fotos por organizar_ a
_Fotos_ sólo arrastrándola en Digikam. Una vez movidas se replicarán automáticamente a mi
servidor casero.

## 5. Replicación con Syncthing

Uso [Syncthing](https://syncthing.net/) para replicar mis datos entre mis diferentes
dispositivos (ordenador, servidor, teléfono móvil). Funciona a la perfección, lo
recomiendo encarecidamente.

Especificamente para mi proceso fotográfico sincronizo dos directorios entre mi ordenador
y mi servidor casero:

- El directorio con las fotos ya organizadas.
- El directorio con las bases de datos de Digikam en formato SQLite. Lo tengo separado de
  la colección de fotos por motivos históricos, porque antes tenía las fotos en un disco
  duro magnético mientras que mi disco principal era un NVMe, de forma que el rendimiento
  era mucho mejor si las bases de datos estaban en este último.

Configuro ambos directorioes como "sólo enviar" (_send-only_) en el ordenador, y "sólo
recibir" (_read-only_) en el servidor:

[
![Configuración de directorio en Syncthing]({static}/images/photography_workflow/syncthing_send_only.png "Click para ver a pantalla completa"){: .align-center}
]({static}/images/photography_workflow/syncthing_send_only.png)

También configuro el control de versiones en el servidor, para tener facilidad de
recuperación en caso de borrados o alteraciones erróneas:

[
![Versionado de ficheros en Syncthing]({static}/images/photography_workflow/syncthing_file_versioning.png "Click para ver a pantalla completa"){: .align-center}
]({static}/images/photography_workflow/syncthing_file_versioning.png)

Mi servidor casero tiene 4 discos duros, uno de los cuales está configurado como paridad
usando [SnapRAID](https://www.snapraid.it/) para tolerancia a errores. No voy a entrar en
detalles sobre la configuración de mi servidor casero, eso merecería un artículo aparte.

## 6. Copia de seguridad con restic

Mi servidor casero hace una copia de seguridad incremental cada semana a
[Wasabi](https://wasabi.com/) usando
[restic](https://restic.readthedocs.io/en/stable/). La copia de seguridad incluye mi
colección de fotos completa, además de cualquier otro dato personal que no sería
recuperable en caso de catástrofe. Puedes ver [mi _script_ de backup con
restic](https://gist.github.com/haplo/db12fc973122366ab1e8cb0d17afbd0c) y ajustarlo a tus
necesidades. Uso [Ansible](https://www.ansible.com/) para generar las listas de ficheros
incluidos y excluidos. El _script_ es ejecutado por cron cada semana, de noche.

¿Por qué restic? Cuando estaba investigando las opciones disponibles leí muy buenas
opiniones que decían que hacía las cosas bien, y la verdad es que me ha funcionado sin
demasiados problemas. Si tuviese que implementarlo todo otra vez me gustaría investigar
[Borg](https://www.borgbackup.org/) como alternativa, pero es posible que volviese a
elegir restic.

¿Por qué Wasabi? Tiene una API compatible con S3 y de los precios más baratos que pude
encontrar, más que Backblaze, sobre todo contando conque no tiene costes para el envío o
recepción de datos.

Por supuesto la [copia de seguridad va
cifrada](https://restic.readthedocs.io/en/stable/070_encryption.html).

## Epílogo

Este proceso es la evolución de 20 años de fotografía digital. Espero que hayas podido
aprender algo nuevo que puedas aplicar a tu propio proceso fotográfico. Actualizaré este
artículo a medida que haga cambios a las herramientas que uso.

Quizá te estés preguntando sobre el último de los objetivos que mencioné al principio del
artículo: _"acceso y compartición transparente de las fotos"_. Estoy trabajando en la
creación de un software de galería web que dé acceso a mi colección fotográfica completa y
que permita navegar utilizando los metadatos de Digikam. El software se ejecutaría en mi
servidor casero, donde ya se alojan las fotos y se sincronizan todas las nuevas. Esto
significa que tras organizar las fotos en Digikam estarían disponibles para su acceso
desde cualquier dispositivo de mi elección manteniendo el control sobre mis datos y sin
tener que subirlos a ningún otro servicio. Pienso liberar el software con licencia libre
cuando sus funcionalidades básicas funcionen, sigue el blog por RSS o sígueme en redes
sociales si te interesa estar al tanto de su lanzamiento.

Si tienes cualquier comentario o sugerencia me encantaría oírlo, no dudes en mencionarme o
enviarme un mensaje por redes sociales, o un email. Puedes ver mis datos de contacto en
[mi página web]( https://fidelramos.net/).

## Actualizaciones

- 2022-04-05: Corregido el nombre de RawTherapee. Gracias por los [desternillantes
  comentarios, Hacker News](https://news.ycombinator.com/item?id=30918149).
