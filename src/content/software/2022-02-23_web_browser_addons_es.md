Title: Extensiones de navegador web que uso
Date: 2022-02-23
Modified: 2023-04-20
Lang: es
Category: Software
Tags: firefox,web,extensiones,privacidad,seguridad,criptomoneda
Slug: web-browser-addons

Este artículo recopila las extensiones de navegador web que uso, y por qué. Lo actualizaré
de vez en cuando.

Uso [Firefox](https://www.mozilla.org/en-US/firefox/new/) como mi navegador web de
cabecera, porque pese a sus limitaciones sigue siendo la mejor opción disponible para mí,
por razones que darían para otro artículo. Algunas de estas extensiones están disponibles
para otros navegadores. Cuando sea apropiado enlazaré a la web principal del proyecto.

Procuro ser cuidadoso con las extensiones que instalo, dado que tienen acceso a casi todos
los datos del navegador, así que si fuese comprometida se podría convertir en una
pesadilla si por ejemplo consiguiese robar las credenciales de mi cuenta de correo
electrónico (aunque la A2F debería reducir ese riesgo). Por esta razón no uso muchas
extensiones que son potencialmente útiles pero que tampoco es que me hagan falta. Las que
uso suelen ser muy populares, con miles de usuarios y seleccionadas por los editores.

Sin más dilación, estas son las extensiones que uso actualmente en Firefox, en orden
alfabético:

- [uBlock Origin](https://ublockorigin.com/): el mejor bloqueador de anuncios que existe
  (que yo sepa, si conoces alguno mejor por favor házmelo saber). Usa poco procesador y
  memoria, normalmente ahorra más que consume, dado que las páginas web cargan más rápido
  sin toda la mierda que suelen incluir (anuncios, rastreadores, etc.). Especialmente en
  móvil se puede notar mucho. Solía instalar otro puñado de extensiones para mejorar la
  privacidad (NoScript, ClearURLs, PrivacyBadger, HTTPSEverywhere y DecentralEyes), pero
  tras leer [este artículo en
  Arkenfox](https://github.com/arkenfox/user.js/wiki/4.1-Extensions) aprendí que son
  superfluas si se configura bien uBlock Origin. Y déjame decirte una cosa más: mi Firefox
  *vuela* después de eliminar esas extensiones.
- [KeepassXC-Browser](https://keepassxc.org/docs/KeePassXC_GettingStarted.html#_setup_browser_integration):
  Uso [KeepassXC](https://keepassxc.org/) para almacenar mis contraseñas y secretos, esta
  es la extensión oficial para navegadores web, con autocompletado de
  formularios. Funciona bastante bien aunque no tanto como competidores como Lastpass o
  1Password, pero no les confiaría mis datos más íntimos a terceros.
- [Taho](https://taho.xyz/): una billetera de criptomonedas de código abierto,
  abre la puerta a la Web 3.0, Dapps, NFTs, ICOs, tokens ERC20... Para mi ha reemplazado a
  Metamask, que es la opción más popular pero es de código privativo. A noviembre de 2022
  soporta [Ethereum](https://ethereum.org/en/), [Polygon](https://polygon.technology/),
  [Optimism](https://www.optimism.io/) y [Arbitrum](https://arbitrum.io/), y añaden
  soporte para otras cadenas de bloques con frecuencia.
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
- [Sidebery](https://addons.mozilla.org/en-US/firefox/addon/sidebery/): un gestor de
  pestañas para Firefox. Si eres como yo y tienes no ya docenas, sino cientos de pestañas
  abiertas, esta extensión lo cambia todo. Tener tantas pestañas abiertas se convierte en
  una ventaja en vez de un inconveniente. Las pestañas se organizan jerárquicamente como
  un árbol; se pueden agrupar las pestañas de diferentes formas (grupos y paneles); hacer
  que las pestañas se abran en un panel determinado según el contenedor en el que se abren
  (mira la extensión Firefox Multi-Account Container que menciono más arriba); descargar
  de la memoria pestañas o paneles completos. Es configurable hasta el hartazgo, y esto lo
  dice alguien que es un loco de configurarlo todo al detalle. Sigo descubriendo nuevas
  características útiles que mejoran mi uso y disfrute del navegador web.
- [Skip Redirect](https://addons.mozilla.org/en-US/firefox/addon/skip-redirect/): detecta
  redirecciones en ciertas páginas y se las salta, para evitar rastreos innecesarios. Por
  ejemplo si te fijas al buscar algo en Google, cuando vas a un resultado la dirección es
  la web destino, sino que apunta a Google, y luego te redirecciona al destino. Esta
  extensión extrae el destino para evitar que Google (o muchos otros servicios) sepa qué
  resultados visitas.

Actualizaciones:

- 2022-11-19: Reemplazado Metamask con Tally Ho; añadido Sidebery.
- 2023-01-20: Añadido Skip Redirect; eliminados NoScript, ClearURLs, PrivacyBadger, HTTPSEverywhere, DecentralEyes.
- 2023-04-20: Tally Ho actualizado a Taho, [cambiaron el nombre de la marca el 21 de febrero de 2023](https://blog.taho.xyz/rename-announcement/).
