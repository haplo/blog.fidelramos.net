Title: Omarchy y el punto óptimo de seguridad
Date: 2026-09-01
Lang: es
Category: Software
Tags: linux,personal,privacidad,seguridad,software-libre
Slug: omarchy-security-sweet-spot

[Omarchy](https://omarchy.org/), la distribución Linux
[omakase](https://en.wikipedia.org/wiki/Omakase) creada por [David Heinemeier
Hansson](https://x.com/dhh) (el creador de Ruby on Rails), está ahora mismo en boca de
la comunidad del software libre. [Algunos la
aman](https://x.com/bonkcity_/status/2094225788987961854?s=20), [otros la
odian](https://x.com/jpschroeder/status/2094494281129918592?s=20).

Yo lo digo claro: me declaro fan de Omarchy. Hay muchas cosas que me encantan a primera
vista: el optimismo; la actitud de "sí se puede" ([*we can fix
everything*](https://x.com/dhh/status/2094501042306113598?s=20)); [unir a la
gente](https://x.com/dhh/status/2092129715662242179?s=20); [volver a hacer divertidos a
los ordenadores](https://x.com/dhh/status/1963822469829329203?s=20); [distanciarse de la
política](https://x.com/dhh/status/2093681834265567463?s=20); [enfocarse en el
rendimiento](https://x.com/dhh/status/2092479124807852504?s=20)... Vamos, si es que
hasta **me encanta la experiencia por defecto**: el gestor de ventanas *tiling* moderno;
el acceder a todo con el teclado; hasta la estética. Yo estoy entre la audiencia a la
que va dirigida Omarchy, sería un usuario feliz haciendo muy pocos cambios.

Este artículo, sin embargo, se centra en las razones técnicas por las que **todavía no
voy a instalar Omarchy**. Se resume en lo que llamo el **punto óptimo de la seguridad**.

## El punto óptimo de la seguridad

Me tomo en serio la seguridad y la privacidad, porque creo que nuestras vidas digitales
pesan cada vez más. Quiero proteger mis datos, ser consciente de dónde se alojan, quién
tiene acceso a qué, y no dárselos a terceros cuando puedo evitarlo. Para eso invierto
muchas horas a mis prácticas de seguridad y privacidad: leer, aprender, planificar e
implementar cambios. Pero aparte de ese tiempo las decisiones que tomo añaden fricción y
complicaciones a mi día a día, porque definen el cómo interactúo con mis
dispositivos. Encontrar el **punto óptimo adecuado** de seguridad y privacidad **para
mí** es algo a lo que le llevo dando vueltas muchos años.

Me gusta pensar en la intersección de mis datos y mis dispositivos como círculos, donde
los de más confianza tienen acceso a los datos más íntimos.

[
![Zonas de confianza de los datos]({static}/images/omarchy_security_sweet_spot/data_trust_zones_es.webp "Clic para pantalla completa"){:.align-center}
]({static}/images/omarchy_security_sweet_spot/data_trust_zones_es.webp "Clic para pantalla completa"){:target="_blank"}

Según este diagrama, tengo que confiar más en la integridad de mi ordenador que en la de
mis dispositivos móviles (móvil, tablet). Eso hace que no solo la elección del SO, sino
cómo lo configuro y lo uso, sea una decisión clave.

# La evolución de mi punto óptimo

Para entender cómo ha ido cambiando mi particular punto óptimo de seguridad, voy a repasar
la historia de mis sistemas operativos de cabecera:

<div align="center">
ZX Spectrum (finales de los 80)<br/>
↓<br/>
MS-DOS (principios de los 90)<br/>
↓<br/>
Windows (finales de los 90)<br/>
↓<br/>
Debian (los 2000)<br/>
↓<br/>
Kubuntu (principios de los 10)<br/>
↓<br/>
Qubes OS (finales de los 10)<br/>
↓<br/>
Arch Linux (los 20 hasta ahora)<br/>
</div>

Empecé con la informática en un ZX Spectrum+ en 1988; eran solo juegos y un poco de
[BASIC](https://en.wikipedia.org/wiki/BASIC). Unos años después pasé a un IBM PC con
[MS-DOS](https://en.wikipedia.org/wiki/MS-DOS), y eventualmente Windows 3.11. Sin
Internet en casa, y prácticamente sin datos personales en los dispositivos (solo algún
trabajo del cole), nadie pensaba en la privacidad; o más bien se daba por sentada.

Luego, con Windows 95, llegó Internet primero a través de módem, y más tarde por
ADSL. Empecé a participar en comunidades online, a bajarme música, vídeos y
software. Era un adolescente, pero por suerte lo bastante sensato como para usar un
apodo y no publicar nombres ni direcciones en público.

El salto de Windows a Debian (después de trastear con otras distros de Linux) fue casi
inevitable tras leer [la filosofía del software
libre](https://www.gnu.org/philosophy/). Me di cuenta de que no podía fiarme del
software de código cerrado, y cada vez me sentía más incómodo con Windows. Cuando cambié
sobre todo eché de menos mis juegos (solo unos pocos conseguí hacer funcionar con
[Wine](https://www.winehq.org/)), pero decidí pasarme a las consolas para quitarme el
gusanillo. Mi soberanía digital era más importante.

Debian es una distro increíble, y sigue siendo mi elección para servidores a día de hoy.
No obstante sus versiones tables se quedan anticuadas para su uso en escritorio, ese
siempre ha sido un punto en contra para los que buscamos software reciente. Sí, usaba
[backports](https://backports.debian.org/), y acabé corriendo
[sid](https://www.debian.org/releases/sid/), pero eso significaba más inestabilidad y
roturas de vez en cuando. Por eso acabé cambiando a Ubuntu (al final me quedé con su
sabor [Kubuntu](https://kubuntu.org/)), y me fue bien por bastantes años.

En 2016 un amigo me presentó [Qubes OS](https://www.qubes-os.org/), y me flipó sus
mejoras de seguridad. Si no conoces Qubes OS, quizá quieras [leer su
introducción](https://doc.qubes-os.org/en/latest/introduction/intro.html) para darte
cuenta de lo distinto que puede ser un SO de escritorio. Si te da pereza, el resumen es
este: en un SO tradicional todo el software que corre tiene acceso completo al
ordenador, a todos sus archivos y dispositivos; en Qubes OS, en cambio, hay un
componente del SO (lo que llaman *Dom0*) con un mínimo de software de confianza, y luego
todo, absolutamente todo lo demás, corre en **máquinas virtuales independientes y
aisladas**. Eso significa que si alguna vez ejecutas software malicioso (virus,
troyanos, spyware, ransomware, ataques de cadena de suministro...), no tomaría
automáticamente el control del ordenador y todos sus datos. Romper las barreras de una
máquina virtual no es imposible, pero es bastante más difícil que otras opciones de
aislamiento. Por eso se consideran el estándar de oro de la seguridad del software,
amén de ejecutar en otro hardware independiente, claro.

Al final me pillé un portátil nuevo en 2017 e instalé Qubes OS. Lo usé con éxito varios
años. Me sentía empoderado, con confianza para ejecutar cualquier software con la
tranquilidad de que no podía joder el ordenador ni acceder a datos que no debiera. Sin
embargo, el día a día se hizo pesado y acabó siendo demasiado para mí. La lentitud,
incluso con VMs aceleradas por hardware, hacía penosas todas las tareas diarias: navegar
por la web, abrir imágenes o PDFs, y sobre todo mi [trabajo
fotográfico]({filename}/photography/2022-03-31_photography_workflow_es.md) se resintió
mucho. Después de unos años decidí que tanta seguridad no estaba justificada para mis
necesidades personales, y que había inclinado demasiado la balanza en esa dirección.

Eso me llevó a mi última transición. Me pillé un ordenador de sobremesa nuevo y me quedé
con [Arch Linux](https://archlinux.org/) por su amplitud de software al día y su
maleabilidad para configurarlo como quisiese. Implementé algunas prácticas de seguridad
que me acercarían a mi punto óptimo de seguridad, privacidad y UX, como [Secure Boot de
extremo a extremo basado en UKI](https://github.com/max-baz/arch-secure-boot) y
[sandboxing ligero de software](https://github.com/netblue30/firejail/). Uso
[KDE](https://kde.org/) porque me resulta familiar y es muy configurable, pero los
gestores de ventanas *tiling* modernos me tiran mucho; simplemente ahora mismo no puedo
justificar el tiempo de montar uno.

## Qué voy a buscar en mi futuro SO de escritorio

Ahora mismo estoy a gusto, con un ecosistema personal cómodo y lo bastante seguro para
lo que necesito. Pero la mente del *hacker* no para, y siempre estoy pensando en cómo se
podría mejorar.

Esta es mi lista de deseos de lo que me gustaría ver en mi próximo SO de escritorio:

1. **Buen UX de serie**. Rápido. Fluido. Agradable en el día a día. Todo con el
   teclado. Bonito. Omarchy ya cumple este punto para mí, eso fue lo que me motivó a
   escribir este artículo.
2. **Software en sandbox**. La mayoría de los programas deberían ejecutarse en un
   sandbox por defecto, de una forma abstraída del usuario para que la UX no se
   resienta. No me importa que me pregunte por permisos; la mayoría sólo serían una vez
   por cada programa, me parecen un compromiso aceptable para la seguridad. Habría una
   interfaz cómoda para gestionar los permisos, incluyendo a qué archivos o directorios
   tiene acceso cada programa (lectura y/o escritura).
3. **Actualizaciones auditadas**. Después de [implementar revisión con IA para la
   actualización de mis paquetes de
   Emacs]({filename}/software/2026-08-08_emacs_straight_ai_review_es.md) he estado
   pensando cuánto me gustaría tener lo mismo pero para todo el SO. Quiero alguna
   garantía de que el software se ha auditado antes de aterrizar en mi máquina. No es
   una proposición sencilla, hay muchos retos que superar, porque es mucho software y
   sería muy costoso, pero creo que podría haber soluciones vía crowdfunding. Me parece
   que podría ser una *killer app* para Linux, porque un SO de código cerrado no podría
   competir en este terreno: tienes inevitablemente que fiarte de un tercero y no puedes
   fiarte solamente del código. Estoy planeando un artículo para desarrollar esta idea,
   y quizá trabaje en ello como proyecto futuro si nadie más lo hace primero.
4. **Configuración declarativa**. La verdad es que me arrepiento un poco de no haberme
   subido al carro de [NixOS](https://nixos.org/) en vez de decidirme por Arch Linux. La
   reproducibilidad, la capacidad de compartir configuraciones complejas y de deshacer
   errores es algo muy potente. Además, los agentes de IA simplifican hacer cambios. Lo
   cual me lleva al siguiente punto.
5. **AI integrada**. Como ya saben los lectores de mi blog, ya he abrazado la IA y la
   uso a saco. Estoy plenamente convencido de que ha venido para quedarse y que hay que
   integrarla y construir sistemas nuevos a su alrededor para que nos sirvan mejor. La
   uso para programar, investigar, depurar, aprender, crear... Sin embargo [constreñir a
   las IAs]({filename}/software/2026-05-14_how_i_sandbox_ai_agents_es.md) para
   satisfacer mis objetivos de seguridad y privacidad no ha sido tan sencillo como me
   gustaría. Quiero que mis agentes tengan acceso restringido solo a lo que necesitan
   para hacer el trabajo. Quiero ver un plan de ejecución que pueda revisar y
   aprobar. No voy a fiarle a una IA mis datos más personales a menos que corra en mis
   propias instalaciones. Mi SO ideal integraría la IA, pero debidamente en sandbox para
   cubrir estos y probablemente otros casos de uso. **Omarchy ya integra IA**, es
   puntero en ese aspecto, pero le pediría que estuviese mejor aislada.

Ahora mismo estoy liado con otros proyectos que demandan mi atención, incluida una
reforma gorda de la casa y poner en marcha mi [nuevo
homelab]({filename}/software/2026-01-25_self_hosted_home_1_es.md). Estas movidas me van
a entretener varios meses, durante los cuales preferiría no distraerme cambiando mi
ordenador principal a otro SO. Sin embargo, cuando la casa y el homelab estén en marcha
pienso revisitar mi elección de SO de escritorio. Cuando llegue el momento regresaré a
esta lista de deseos y veré cómo está el panorama de las distros Linux.

Omarchy está mejorando a un ritmo alucinante, su base de usuarios y el número de
contribuidores crecen por miles. La mayoría de las mejoras que leo parecen centrarse en
el escritorio y la UX, pero ojalá esta humilde lista dé que pensar sobre la arquitectura
del SO en términos de seguridad y privacidad.

Sea como sea les deseo el mejor de los éxitos al proyecto y la comunidad Omarchy, su
positividad es algo muy necesario en estos tiempos que corren.

¿Tienes ideas o comentarios? Déjame uno aquí abajo, o puedes [mencionarme en
X](https://x.com/ampajaro).
