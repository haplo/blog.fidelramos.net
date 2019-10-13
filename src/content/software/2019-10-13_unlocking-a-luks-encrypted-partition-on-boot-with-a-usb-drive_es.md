Title: Desbloqueando en el arranque una partición cifrada con LUKS con una memoria USB
Date: 2019-10-13
Lang: es
Category: Software
Tags: linux,seguridad,cifrado,howto
Slug: unlock-luks-usb-drive
Save_as: software/desbloqueando-luks-memoria-usb.html
Url: software/desbloqueando-luks-memoria-usb

El caso de uso que quería resolver era: tengo un servidor sin monitor
con un disco duro cifrado por software usando LUKS, y quiero ser capaz
de reiniciarlo sin tener que escribir la contraseña en un teclado. La
solución que implementé fue crear un fichero con una clave LUKS en una
memoria USB, de forma que si se conecta al iniciar el sistema el
fichero se usará para desbloquear la partición LUKS en vez de la
contraseña.

Antes de empezar quiero mencionar someramente las implicaciones de
seguridad de esta solución:

* Quienquiera obtenga acceso al dispositivo USB será capaz de
  descifrar el dispositivo objetivo. Considera los requisitos de
  seguridad de la memoria USB: guardarla en una caja fuerte,
  esconderla, llevarla siempre contigo...

* Idealmente la memoria USB se usaría exclusivamente para este
  propósito, dado que si se conecta a otros sistemas estos podrían
  leer y filtrar la clave de cifrado.

* Estamos obviamente reduciendo la seguridad del sistema a cambio de
  ganar usabilidad. A veces este es el equilibrio que buscamos, otras
  veces no tanto. Solo tú puedes juzgar el valor de lo que estás
  protegiendo, las potenciales formas de ataque y qué medidas de
  seguridad son apropiadas.

Bien, manos a la obra. Asumiremos que tienes una memoria USB ya
formateada y montada (p.ej en `/mnt`) en el ordenador con el
dispositivo LUKS que quieres desbloquear en el arranque. El primer
paso será crear un fichero con información aleatoria:

``` text
# dd if=/dev/urandom of=/mnt/key bs=4096 count=1
```

A continuación añadimos la clave generada a LUKS, para que pueda ser
utilizada para desbloquear la partición raíz:

``` text
# cryptsetup luksAddKey /dev/sda3 /mnt/key
```

`/dev/sda3` es un ejemplo, debes mirar cuál es la partición raíz en tu
sistema.

El siguiente paso será actualizar `/etc/crypttab`, que define los
volúmenes cifrados que son gestionados por LUKS. Tu fichero `crypttab`
debería tener una entrada similar a esta:

``` text
cryptroot UUID=452ac6ac-8bbb-484f-b508-a11a5585e031 none luks
```

Tenemos que actualizar esta línea para usar el *script* `passdev` que
viene proporcionado de serie por `cryptsetup`. `passdev` se encarga de
esperar a que un dispositivo determinado aparezca como disponible,
entonces lo monta y lee la clave de un fichero. Es buena idea
referirse a la memoria USB utilizando un dispositivo que no vaya a
cambiar de forma inesperada. Yo uso `/dev/disk/by-label/<LABEL>`, que
es un enlace simbólico al dispositivo basado en la etiqueta de la
partición. Tras actualizar la línea en `/etc/crypttab` debería lucir
así:

``` text
cryptroot UUID=452ac6ac-8bbb-484f-b508-a11a5585e031 /dev/disk/by-label/FIDELRAMOS.NET:/key:20 luks,keyscript=/lib/cryptsetup/scripts/passdev
```

Deja el nombre de mapeado original (`cryptroot` en este ejemplo) y el
mismo UUID, de otra forma se romperá el arranque dado que estos datos
se referencian en `/etc/fstab`. Solo cambia `none` y añade el
`keyscript`.

El último paso es regenerar la imagen de initramfs para que incluya el
*script* `passdev`, si no fallará el arranque.

``` text
# update-initramfs -k all -u
```

¡Y ya está! Al reiniciar el sistema debería detectar la memoria USB,
montarla automáticamente y usar el fichero clave para desbloquear la
partición raíz. Si la memoria USB no se detecta por cualquier razón en
20 segundos debería pasarse a leer la clave por teclado.
