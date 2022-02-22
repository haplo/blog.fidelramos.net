Title: Las extensiones de navegador web que uso
Date: 2022-02-23
Lang: es
Category: Software
Tags: firefox,web,extensiones,privacidad,seguridad,criptomoneda
Slug: web-browser-addons

Este artículo recopila las extensiones de navegador web que uso, y por qué. Lo actualizaré
de vez en cuando.

Uso [Firefox](https://www.mozilla.org/en-US/firefox/new/) como mi navegador web de
cabecera, porque pese a sus limitaciones sigue siendo la mejor opción disponible para mí,
por razones que darían para otro artículo. La mayoría de estas extensiones están
disponibles para otros navegadores. Cuando sea apropiado enlazaré a la web principal del
proyecto.

Procuro ser muy cuidadoso con las extensiones que instalo, dado que tienen acceso a casi
todos los datos del navegador, así que si fuese comprometida se podría convertir en una
pesadilla si por ejemplo consiguiese robar las credenciales de mi cuenta de correo
electrónico (aunque la A2F debería reducir ese riesgo). Por esta razón no uso muchas
extensiones que son potencialmente útiles pero que tampoco es que me hagan falta. Las que
uso suelen ser muy populares, con miles de usuarios y seleccionadas por los editores.

Sin más dilación, estas son las extensiones que uso actualmente en Firefox, en orden
alfabético:

- [ClearURLs](https://addons.mozilla.org/firefox/addon/clearurls/): elimina parámetros
  innecesarios de las URL, como los ubicuos `utm_*` or las largas URL que genera Amazon y
  que pueden ser recortadas sin pérdida de funcionalidad.
- [Decentraleyes](https://decentraleyes.org/): muchas páginas web usan recursos de CDN
  públicas (p.ej. [Google da acceso a muchas librerías
  Javascript](https://developers.google.com/speed/libraries/)) para ahorrar ancho de banda
  y/o para servir los recursos más rápidamente. La pega es que el proveedor de la CDN
  puede ver quién accede a qué página, y eso reduce nuestra privacidad. _Decentraleyes_
  almacena una copia local de esos recursos de forma que no es necesario hacer peticiones
  a esas CDN, mejorando así la privacidad.
- [HTTPS Everywhere](https://www.eff.org/https-everywhere): Un proyecto de la
  [EFF](https://www.eff.org/) que utiliza conexiones HTTPS siempre que sea posible, y por
  tanto seguras contra ataques de intercepción (_eavesdropping_) o de intermediario
  (_middleman_). Es automático y no debería romper ninguna página, así que es recomendable
  para cualquier usuario.
- [KeepassXC-Browser](https://keepassxc.org/docs/KeePassXC_GettingStarted.html#_setup_browser_integration):
  Uso [KeepassXC](https://keepassxc.org/) para almacenar mis contraseñas y secretos, esta
  es la extensión oficial para navegadores web, con autocompletado de
  formularios. Funciona bastante bien aunque no tanto como competidores como Lastpass o
  1Password, pero no les confiaría mis datos más íntimos a terceros.
- [Metamask](https://metamask.io/): una billetera (_wallet_) de
  [Ethereum](https://ethereum.org/en/) muy completa, abre la puerta a la Web 3.0, Dapps,
  NFTs, ICOs, tokens ERC20...
- [Firefox Multi-Account
  Container](https://addons.mozilla.org/en-US/firefox/addon/multi-account-containers/):
  Firefox tiene soporte de serie para contenedores, esta extensión es necesaria para
  gestionarlos. Es oficial del propio equipo de Firefox, así que tiene mi plena
  confianza. ¿Qué son los contenedores? Son una forma de categorizar pestañas, para aislar
  la información a la que pueden acceder. Por ejemplo, configuro la web de mi banco para
  abrirse siempre en el contenedor _Banking_, de forma que un potencial atacante que
  consiga ejecutar código que aproveche un agujero de seguridad en otra pestaña no debería
  tener acceso salvo que también hubiese sido abierta en el mismo contenedor
  _Banking_. También uso contenedores para aislar el rastreo cuando inicio sesión en
  ciertos servicios, por ejemplo tengo un contenedor _Google_ donde inicio sesión en
  Google, pero en todos los demás contenedores estoy desconectado. Tengo un puñado de
  contenedores: _Gov_ para páginas del gobierno, _Personal_ para las aplicaciones web
  alojadas en mis propios servidores, _Shopping_ siempre que compro algo...
- [NoScript](https://noscript.net/): Una extensión muy potente que bloquea la ejecución de
  _scripts_ en cualquier página, y que permite activarlos selectivamente. Por defecto
  bloquea todos los _scripts_, y encontrar cuáles son necesarios para que ciertas webs
  funcionen bien puede llegar a ser pesado, pero creo que merece la pena por la protección
  que otorga. También incluye guardas contra ataques web como
  [XSS](https://en.wikipedia.org/wiki/Xss),
  [Clickjacking](https://en.wikipedia.org/wiki/Clickjacking) o internet-a-intranet.
- [Privacy Badger](https://privacybadger.org/): otra extensión de la EFF que aprende
  automáticamente a bloquear rastreadores (_trackers_) invisibles. No necesita apenas
  mantenimiento, razón por la que la instalo junto con NoScript y uBlock Origin, aunque se
  solape en gran parte con éstas. Al igual que HTTPS Everywhere no debería romper ninguna
  página, así que es recomendable para todos los usuarios.
- [uBlock Origin](https://ublockorigin.com/): el mejor bloqueador de anuncios que existe
  (que yo sepa, si conoces alguno mejor por favor házmelo saber). Usa poco procesador y
  memoria, normalmente ahorra más que consume, dado que las páginas web cargan más rápido
  sin toda la mierda que suelen incluir (anuncios, rastreadores, etc.). Especialmente en
  móvil se puede notar mucho.
