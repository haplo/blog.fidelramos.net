Title: Extensiones de navegador web que uso
Date: 2022-02-23
Modified: 2023-04-20
Lang: es
Category: Software
Tags: firefox,web,extensiones,privacidad,seguridad,criptomoneda
Slug: web-browser-addons

Este artículo enumera las extensiones de navegador web que utilizo y por qué.
Lo mantendré actualizado de vez en cuando.

Este artículo enumera las extensiones de navegador web que utilizo y por qué.
Lo mantendré actualizado de vez en cuando.

Actualmente uso [Brave](https://brave.com/) como mi navegador web principal, y es el que recomiendo a todo el mundo.
Ofrece una gran experiencia por defecto, con características como un bloqueador de anuncios integrado, integración con [Tor](https://en.wikipedia.org/wiki/Tor_(network)) incorporada, pestañas verticales y agrupadas, una cartera de criptomonedas decente, soporte para [IPFS](https://en.wikipedia.org/wiki/InterPlanetary_File_System), [videollamadas](https://talk.brave.com/) integradas.
La experiencia lista para usar es mejor que las alternativas en mi opinión, especialmente para los usuarios habituales que no saben o no quieren trastear con su software.

Anteriormente usaba [Firefox](https://www.mozilla.org/en-US/firefox/new/).
Aprecio que sea el único navegador importante con su propio motor de renderizado (Gecko) que no está basado en el hegemónico WebKit que es la base de prácticamente todos los demás navegadores web.
Como desarrollador web sé lo peligroso que es tener un monocultivo en torno a un único motor de navegador web, que es lo que sufrimos a finales de los 90 y principios de los 2000 con Internet Explorer.

Intento tener cuidado con las extensiones de navegador que instalo, ya que tienen un acceso profundo a los datos del navegador.
Esto significa que un complemento malicioso o comprometido puede convertirse rápidamente en una pesadilla si consigue, por ejemplo, robar las credenciales de mi cuenta de correo electrónico (aunque el 2FA debería mitigar ese riesgo).
Por esta razón sopeso cuidadosamente la utilidad de los complementos frente a ese riesgo.
Los que utilizo suelen ser populares, con miles de usuarios y a menudo seleccionados por los editores.

Sin más dilación, estos son los complementos que estoy usando actualmente en Brave:

- [KeepassXC-Browser](https://keepassxc.org/docs/KeePassXC_GettingStarted.html#_setup_browser_integration):
  Uso [KeepassXC](https://keepassxc.org/) para almacenar mis contraseñas y secretos, esta
  es la extensión oficial para navegadores web, con autocompletado de
  formularios. Funciona bastante bien aunque no tanto como competidores como Lastpass o
  1Password, pero no les confiaría mis datos más íntimos a terceros.

En Firefox solía usar estas extensiones:

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

- 2022-11-19: Reemplacé Metamask por Tally Ho; añadí Sidebery.
- 2023-01-20: Añadí Skip Redirect; eliminé NoScript, ClearURLs, PrivacyBadger, HTTPSEverywhere, DecentralEyes.
- 2023-04-20: Actualicé Tally Ho a Taho, [cambiaron de marca el 21 de febrero de 2023](https://blog.taho.xyz/rename-announcement/).
- 2026-03-31: Ahora uso Brave como mi navegador web principal.
