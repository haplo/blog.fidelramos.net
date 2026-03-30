Title: DNI electrónico en Firefox en Linux
Date: 2026-03-30
Modified: 2026-03-30
Lang: es
Category: Software
Tags: free-software,firefox,howto,linux,web
Slug: dnie-firefox-linux

Hace muchos años que tengo el DNI electrónico (o DNIe) en mi cartera, y no pocas veces he intentado hacerlo funcionar en Linux para autenticarme en las páginas de la administración pública.
Siempre me encontraba con algún problema que me hacía desistir.

Hace poco me tocó renovarlo y pensé en probar otra vez, a ver si caía la breva.
¡Y sí que cayó!
Al fin lo pude hacer funcionar sin paquetes extraños ni complicaciones, con un lector de tarjetas baratito.

Voy a dejar los pasos que he seguido para configurarlo en **Arch Linux**.
Dejaré comentarios sobre los paquetes equivalentes en **Debian/Ubuntu** y **Fedora**, porque el resto de la configuración debería ser la misma para todos.

[TOC]

## Qué necesitas

- Un **lector de tarjetas inteligentes** compatible con el estándar CCID (la mayoría lo son). Por 10€ hay muchos para elegir.
- Tu **DNIe** con los certificados activos. Si no los has activado o han caducado, debes renovarlos en un Punto de Actualización del DNIe (PAD) en una comisaría de policía.
- El **PIN** de tu DNIe, que configuraste al obtenerlo o renovar los certificados. Cuando lo renuevas te dan un papel con el PIN.
- **Firefox** instalado de forma nativa. Si usas Flatpak o Snap probablemente tengas problemas porque limitan el acceso a los dispositivos y ficheros del resto del sistema. Lo comento más abajo en la sección de *Solución de problemas*.

Aprovecho para comentar que Chrome y derivados (Chromium, Brave...) también funcionan con los mismos paquetes, pero la forma de configurarlos es diferente, no tienen interfaz gráfica como la de Firefox.
Vamos eso a mí no me asusta, simplemente uso Firefox para las páginas del gobierno por su extensión [Multi-Account Containers](https://addons.mozilla.org/en-US/firefox/addon/multi-account-containers/) que da un buen aislamiento entre sesiones.

En [este artículo](https://bandaancha.eu/foros/dnie-debian-ubuntu-mint-chromium-chrome-1747958) hay instrucciones para configurar Chrome/Chromium/Brave.

## Paso 1: Instalar los paquetes necesarios

Necesitamos:

- **pcscd / pcsc-lite**: el demonio que gestiona la comunicación con lectores de tarjetas.
- **ccid**: el driver genérico para lectores [CCID](https://es.wikipedia.org/wiki/CCID_(protocolo)).
- **opensc**: el middleware PKCS#11 que permite a las aplicaciones acceder a los certificados guardados en la tarjeta. Soporta el DNIe de forma nativa.
- **pcsc-tools**: utilidades de diagnóstico como `pcsc_scan`.

### Arch Linux

```bash
sudo pacman -S ccid opensc pcsc-tools
```

### Debian / Ubuntu

```bash
sudo apt update
sudo apt install pcscd pcsc-tools opensc libccid
```

### Fedora

```bash
sudo dnf install pcsc-lite pcsc-tools opensc ccid
```

## Paso 2: Activar el servicio pcscd

```bash
sudo systemctl enable pcscd.service
sudo systemctl start pcscd.service
```

Opcionalmente se puede habilitar la activación bajo demanda mediante el socket, para que se inicie cuando haga falta:

```bash
sudo systemctl enable pcscd.socket
sudo systemctl start pcscd.socket
```

## Paso 3: Comprobar que el lector y la tarjeta se detectan

Lo primero es comprobar que el lector de tarjetas es reconocido por **pcscd**.

Conecta el lector USB e inserta el DNIe.
Luego ejecuta:

```bash
pcsc_scan
```

Deberías ver una salida similar a:

```
Scanning present readers...
0: ACS ACR38U-CCID 00 00

Reader 0: ACS ACR38U-CCID 00 00
  Event number: 0
  Card state: Card inserted,
  ATR: 3B 7F 96 00 00 ...
```

Si en su lugar ves **"Waiting for the first reader..."**, el sistema no detecta el lector. En ese caso:

1. Comprueba que el lector aparece en la salida de `lsusb`.
2. Inspecciona los mensajes del kernel con `dmesg | tail -30` tras conectar el lector.
3. Asegúrate de que el servicio `pcscd` está corriendo con `systemctl status pcscd.service`.
4. Prueba otro puerto USB.

### Verificar que OpenSC reconoce el DNIe

```bash
opensc-tool -n
```

Debería devolver `DNIe` o `DNIE`. A continuación, comprueba que los certificados son legibles:

```bash
pkcs11-tool --module /usr/lib/opensc-pkcs11.so -O
```

Este comando listará los objetos almacenados en la tarjeta: certificados de autenticación y firma, y sus claves asociadas.
Si te pide el PIN, introdúcelo.

Para un volcado más detallado:

```bash
pkcs15-tool -D
```

## Paso 4: Configurar Firefox

1. Abre Firefox.
2. Ve a **Ajustes** → **Privacidad & Seguridad**.
3. Baja hasta la sección **Certificados** y haz clic en **Administrar dispositivos de seguridad...**.
4. Haz clic en **Cargar**.
5. Rellena los campos:
   - **Nombre del módulo**: `OpenSC PKCS#11`
   - **Nombre del archivo del módulo**: `/usr/lib/opensc-pkcs11.so`
6. Haz clic en **Aceptar**.

[
![Administrador de dispositivos de seguridad en Firefox]({static}/images/dnie_firefox_linux/security_device_manager.png "Click para ver a pantalla completa"){: .align-center}
]({static}/images/dnie_firefox_linux/security_device_manager.png "Click para ver a pantalla completa")

> **Nota sobre la ruta en sistemas de 64 bits**: en la mayoría de distribuciones actuales la ruta es `/usr/lib/opensc-pkcs11.so`. En algunas instalaciones de Fedora o Debian puede estar en `/usr/lib64/opensc-pkcs11.so` o `/usr/lib/x86_64-linux-gnu/opensc-pkcs11.so`. Puedes encontrar la ruta exacta con:
>
> ```bash
> find /usr/ -name "opensc-pkcs11.so" 2>/dev/null
> ```

## Paso 5: Probar el acceso

Visita cualquier sede electrónica que ofrezca identificación con certificado, como por ejemplo:

- Agencia Tributaria: <https://sede.agenciatributaria.gob.es>{:target="_blank"}
- Seguridad Social: <https://sede.seg-social.gob.es>{:target="_blank"}
- DGT: <https://sede.dgt.gob.es>{:target="_blank"}

El navegador te pedirá seleccionar un certificado y a continuación el PIN del DNIe.
Tras introducirlo, deberías acceder autenticado.

## Solución de problemas

### Firefox dice "No se puede añadir el módulo"

Verifica que la librería existe y que todas sus dependencias están satisfechas:

```bash
ls -la /usr/lib/opensc-pkcs11.so
ldd /usr/lib/opensc-pkcs11.so | grep "not found"
```

Si `ldd` muestra alguna dependencia como **"not found"**, instala el paquete que la proporciona.

### Los certificados no aparecen aunque la tarjeta se detecta

- **Certificados caducados**: los certificados del DNIe tienen una validez limitada. Si han caducado debes renovarlos en un PAD en una comisaría de policía.
- **Reinicia Firefox**: cierra completamente Firefox, inserta el DNIe y vuelve a abrirlo. A veces no detecta una tarjeta insertada después de cargar el módulo.
- **Reinicia pcscd**: desconecta el lector de tarjetas, reinicia con `sudo systemctl restart pcscd.service` y vuelve a conectarlo.

### El PIN se bloquea

Tras **tres intentos fallidos** el DNIe se bloquea permanentemente.
Para desbloquearlo es necesario acudir a una comisaría de policía.
Asegúrate de recordar el PIN antes de intentar usarlo.

### Firefox instalado con Flatpak o Snap

Las versiones Flatpak y Snap de Firefox corren en un entorno limitado (*sandbox*) que impide el acceso a los dispositivos del sistema y al socket de `pcscd`.
La solución más sencilla (aunque no la más segura) es instalar Firefox desde los repositorios nativos de la distribución:

- **Arch Linux**: `sudo pacman -S firefox`
- **Debian/Ubuntu**: `sudo apt install firefox` (o `firefox-esr`)
- **Fedora**: `sudo dnf install firefox`

Si tienes Firefox instalado a través de **Snap** puedes probar a conectarlo a *pcscd* con:

```shell
sudo snap connect firefox:pcscd
```

A algunas personas parece que les funciona, pero otros tienen problemas, como el acceso a la librería */usr/lib/opensc-pkcs11.so*. Hay un [bug abierto en Mozilla desde 2021](https://bugzilla.mozilla.org/show_bug.cgi?id=1734371) que documenta que cargar módulos PKCS#11 del sistema host no funciona de forma fiable con Snap.

**Flatpak** sí ofrece más herramientas para resolver la situación:

```shell
# Acceso al socket de pcscd
flatpak override --user --filesystem=/run/pcscd org.mozilla.firefox

# Acceso a la librería de OpenSC
flatpak override --user --filesystem=/usr/lib/opensc-pkcs11.so:ro org.mozilla.firefox

# Acceso a dispositivos (lector USB)
flatpak override --user --device=all org.mozilla.firefox
```

## ¿Y qué hay de las firmas?

Esta configuración permite **autenticarse** en una página web, pero los navegadores no gestionan el firmado de documentos digitales.
Para eso hace falta instalar y configurar [AutoFirma](https://firmaelectronica.gob.es/ciudadanos/descargas){:target="_blank"}.

Lo bueno es que la parte de *pcscd* y *opensc* es común, así que una vez funcionando no debería ser difícil.
Pero no lo he probado aún, lo dejo como ejercicio para el lector. :o)

## Resumen

La configuración se reduce a tres cosas: instalar `opensc`, `ccid` y `pcscd`; arrancar el servicio; y cargar `/usr/lib/opensc-pkcs11.so` como módulo de seguridad en Firefox.
No se necesita software propietario ni paquetes específico del DNIe.
