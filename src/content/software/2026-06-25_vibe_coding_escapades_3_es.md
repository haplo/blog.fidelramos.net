Title: Vibe Coding Escapades: Venice.ai KDE widget
Date: 2026-06-25
Lang: es
Category: Software
Tags: ai,kde,programming
Slug: vibe-coding-escapades-venice-kde-widget
Series: Aventuras en vibe coding

## El problema

Vengo usando Venice.ai ([enlace con referencia si te interesa apuntarte](https://venice.ai/chat?ref=XPrCO2)) desde hace tiempo para todas mis necesidades de inteligencia artificial.
Me encanta porque a diferencia de la mayoría de plataformas de IA, es **privado**:

- Cuando usas modelos propios de Venice (modelos libres que ejecutan en sus propios servidores) no guardan registro de los *prompts*, o sea que es un uso privado. La mayoría de proveedores guarda registros de todo, y peor aún son los que te identifican de forma personal, digamos con tu cuenta de Google, entonces pueden asociar todas tus conversaciones para hacer perfiles con un nivel de detalle muy peligroso.
- Al usar modelos externos (GPT, Claude, Gemini, etc.) Venice actúa como proxy anonimizador, o sea que el modelo final no sabe quién está realizando la petición. Obviamente reciben el *prompt* completo y lo registrarán, pero mientras no dés información personal en él pues no deberían poder identificarte.

Otra cosa que me gusta es que tienen un sistema de [tokens](https://venice.ai/token) con el que disfruto de cuenta Pro (con 100 VVV), y también tengo créditos a gastar cada día (1 DIEM da $1 en créditos cada día, para siempre).

El problema entonces era que a veces estaba programando en Opencode y de repente veía el mensaje de que me había quedado sin créditos.
Quería un *widget* en mi escritorio ([KDE](https://kde.org/)) para saber de un vistazo cuánto me queda por gastar en el día.
En otro tiempo habría sido un proyecto enterrado en el baúl de los recuerdos, pero tras descubrir [whatcable-linux](https://github.com/Zetaphor/whatcable-linux) cobré conciencia de que crear estos *widgets* estaba al alcance de mi mano.

![Venice.ai KDE widget sobre un sol retro]({static}/images/vibe_coding_escapades_3/retrosun.webp){: .align-center}

## Ejecución

Empecé un proyecto nuevo con Deepseek V4 Pro en Opencode.
Como ya comenté en [el artículo anterior]({filename}2026-05-26_vibe_coding_escapades_2_es.md) había salido hace poco y prometía resultados similares a Claude Opus a una fracción de precio, así que quería probarlo con proyectos reales.

Lo primero fue generar un [*AGENTS.md*](https://github.com/haplo/venice-kde-widget/blob/main/AGENTS.md) con el objetivo y estructura del proyecto.
Después le pedí documentar la [API de Venice que íbamos a usar](https://docs.venice.ai/api-reference/endpoint/billing/balance).
Hasta ahí todo bien.

Lo siguiente era generar un *widget* estático que mostrase la información que necesitaba, pero sin interactuar con ninguna API por el momento.
Aquí Deepseek falló estrepitosamente: los ficheros [QML](https://en.wikipedia.org/wiki/QML) (el lenguaje propio de la librería Qt que utiliza KDE) que generaba ni siquiera compilaban, el *widget* no llegaba a cargar.
Tras varios intentos tuve que desistir y cambiar a Claude Opus 4.7.

Opus descubrió que el problema era que **el *widget* estaba siendo *cacheado*** por KDE, de forma que aunque instalase una versión nueva seguía cargándose el antiguo.
Probablemente Deepseek había arreglado el problema pero yo seguía viendo la versión antigua *cacheada*.

Opus encontró la forma de reiniciar Plasma para que cargase la nueva versión del *widget*, y con eso ya compilaba y se visualizaba.
A partir de ahí el proceso fue mucho más iterativo.

Siguiente paso: conectar con la API real.
Para simplificar pedí que leyese el *token* de una variable de entorno, Opus [lo consiguió a la primera](https://github.com/haplo/venice-kde-widget/commit/e489c9831acf427d432aff5b6c0f722be348786e).
¡Ya veía mis datos reales!
Como proyecto personal podía haber parado aquí, ya era útil y cubría lo que necesitaba, pero quería pulirlo un poco y publirlo por si otros quisieran usarlo.

Lo siguiente fue almacenar el *token* de forma segura, que no estuviese en texto plano en ninguna parte.
Le pedí a Opus que explorase opciones:

1. [kwallet](https://github.com/KDE/kwallet)
2. [secret-tool](https://man.archlinux.org/man/core/libsecret/secret-tool.1.en)
3. [pass](https://www.passwordstore.org/)

Decidí avanzar con *secret-tool* porque aunque KWallet sea el sistema nativo de KDE,
hace tiempo que se integra con libsecret (y por tanto con secret-tool).
Opus lo tuvo [en un intento](https://github.com/haplo/venice-kde-widget/commit/7bf3fe4d8c584282afde0b1bb14d615e683db0dc) (más [un bug al arrancar](https://github.com/haplo/venice-kde-widget/commit/c289380250685326ce2f3171f7009ed339ac487d)).

El resto fue iterar en la interfaz de usuario, ajustando colores y posiciones un poco, e introducir algunas opciones de configuración, nada importante que destacar.

## Resultado

Tras un fin de semana entero jugueteando, el resultado fue
[venice-kde-widget](https://github.com/haplo/venice-kde-widget/).

![Venice.ai KDE widget]({static}/images/vibe_coding_escapades_3/screenshot.webp){: .align-center}

Lo uso todos los días y ha estado funcionando a las mil maravillas. :)

## Lecciones

El problema inicial de que el *widget* era *cacheado* por KDE Plasma me hizo darme cuenta de que muchos modelos necesitan instrucciones más específicas que otros, son menos creativos.
Si les hubiese pedido que pensasen opciones alternativas a por qué seguía fallando quizá lo habrían encontrado, pero yo mismo no pensé en la posibilidad de que estuviese *cacheado*.
Opus fue el único suficientemente proactivo como para pensar "vamos a confirmar si el código que se está realmente ejecutando es el que tenemos en el repositorio".
Fue más listo que yo, en definitivas cuentas.

Esa proactividad es algo sobre lo que [Simon Willison escribía al respecto de Fable 5](https://simonw.substack.com/p/claude-fable-is-relentlessly-proactive).
Esta experiencia es indicativa que es algo que aplica a otros modelos, o sea Claude Opus 4.7 fue más proactivo que Deepseek V4 Pro.
Me entra curiosidad de pensar si **la proactividad puede ser algo medible entre modelos**, y si hay estudios al respecto.

Otra lección es que para un proyecto con una tecnología tan minoritaria (*widgets* de KDE en QML) la mayoría de modelos no van a dar grandes resultados, les debe **faltar entrenamiento**.
Quizás los resultados habrían sido mejores si les hubiese indicado que mirasen el código de otros *widgets* para que les sirviese de **referencia**.
Opus acabó haciendo eso para algunos problemas que no conseguía resolver: miró al resto de widgets instalados en el sistema para analizar su código.
Probablemente habría sido una buena idea haber **buscado widgets similares** y haber pedido un **análisis antes de implementar**.
O mejor aún afinar un modelo programador con muchos ejemplos de *widgets* KDE, pero eso obviamente sería exagerado para un proyecto como este.

Los resultados en este proyecto, más los de [pelican-copy-code en el artículo anterior]({filename}2026-05-26_vibe_coding_escapades_2_es.md), me han llevado a **reducir el uso de Deepseek V4 Pro**; es más barato pero no me compensa si me lleva a callejones sin salida con código que no funciona y hay que arreglar.

Seguí usando **Kimi 2.6** como modelo por defecto, sobre todo por ser privado en Venice.ai.
Eso cambió con **GLM 5.2**, pero esa será otra historia.
