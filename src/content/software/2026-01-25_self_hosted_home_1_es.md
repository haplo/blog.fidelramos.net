Title: Casa Autoalojada, Parte 1: Diseño y planificación
Date: 2026-01-25
Lang: es
Category: Software
Tags: free-software,linux,self-hosting
Slug: self-hosted-home-1

Quienes hayan estado atentos al blog sabrán que he comprado una casa y he estado planeando su reforma integral.
Como friki de la informática, lo que más me ilusiona es la oportunidad de implementar **la casa inteligente, la red y el servidor doméstico de mis sueños**.

Tengo una idea clara de lo que quiero conseguir: un **homelab de código abierto** que sustituya los **ecosistemas cerrados de la nube** por **servicios locales**.
Domótica, cámaras de seguridad y videoportero, contactos y calendarios, reproductores multimedia, colección de fotos, documentos y más, todo funcionando **en mi propia casa** y **totalmente bajo mi control**.
Hay que tener en cuenta que [ya tengo un homelab]({filename}/software/2023-12-29_homelab.md), donde algunos de estos servicios llevan años funcionando.
Este nuevo proyecto lo sustituirá por completo, ¡será **más grande** y **mejor**!
Os recomiendo leer ese artículo si tenéis la oportunidad, ya que explica las razones que me llevaron a empezar a autoalojar servicios y el contexto histórico de cómo he llegado hasta aquí.

En esta serie de artículos entraré en todos los detalles técnicos, empezando por el diseño al que he llegado tras meses de investigación.

La configuración es completamente personal y subjetiva, adaptada a mis necesidades y gustos particulares, así que no os lo toméis como una recomendación.
¡Espero que sea una lectura entretenida y que aprendáis algo interesante!

Mis objetivos son:

- **Todo local**: La domótica, las cámaras, la multimedia y los datos personales deben funcionar sin ninguna dependencia de la nube. El acceso a Internet podría caerse y todo seguiría funcionando localmente. Además, puedo confiar en que mis datos no saldrán de mi casa.
- **Aislamiento estricto**: Los dispositivos domóticos (*IoT*) y las cámaras se tratan como hostiles: **no tienen salida a Internet** y su acceso a los servicios internos es limitado a lo necesario. La conectividad con la nube debe evitarse siempre que sea posible.
- **Basado en estándares y código abierto**: ONVIF, RTSP, IPv6, WireGuard, ZFS, Proxmox, TrueNAS, IPFire, Home Assistant, Frigate, Nextcloud, Jellyfin, Immich... **evitar las cajas negras cerradas**.
- **Coste**: Aunque el montaje completo no será barato en absoluto, buscaré **hardware de servidor reacondicionado** y daré prioridad a dispositivos de **bajo consumo**. El sistema tendrá muchas responsabilidades, así que necesito hardware fiable y de calidad.
- **Preparado para el futuro**: Hasta 10 GbE mediante cableado Cat6a, servidores con muchos núcleos, espacio para ampliación, IPv6 en todas partes.

[TOC]

Otros artículos de la serie:

1. **Parte 1: Diseño y planificación**
2. Próximamente, ¡[mantente al tanto]({filename}../pages/subscribe_es.md) para no perderte las novedades!

# 1. Visión general

El homelab constará de múltiples componentes montados en un [bastidor (rack) de 42U en 19 pulgadas estándares](https://es.wikipedia.org/wiki/Bastidor_de_19_pulgadas) en una sala dedicada en el sótano de la casa.

- **Red y seguridad principales**
    - Quiero tener el control de la red doméstica: impedir el acceso a Internet de la domótica y las cámaras y limitar el acceso a los servicios internos.
    - Un servidor dedicado con IPFire proporcionará enrutamiento, cortafuegos, IDS (detección de intrusos) y VPN.
    - Switch y puntos de acceso WiFi de UniFi.
    - VLANs para una segmentación estricta del tráfico (LAN, IoT, cámaras, invitados, gestión).
- **Servidor de aplicaciones**
    - Migraré los servicios autoalojados que funcionan en mi [servidor doméstico actual]({filename}2023-12-29_homelab.md), y los ampliaré.
    - Proxmox VE en un servidor tipo Dell PowerEdge.
    - Mezcla de máquinas virtuales y contenedores LXC para los servicios.
- **Almacenamiento**
    - Tengo considerables necesidades de almacenamiento, ya que mantengo una gran colección de fotos y una biblioteca multimedia local.
    - TrueNAS correrá en una máquina virtual en Proxmox, controlando directamente un grupo de discos duros dedicado.
    - ZFS para redundancia, instantáneas y replicación.
- **Cámaras y videoportero**
    - Cámaras y videoportero Dahua con ONVIF/RTSP/IPv6 y audio bidireccional.
    - Switch PoE dedicado.
    - Frigate para grabación tipo NVR y detección de objetos.
    - Coral TPU para inferencia eficiente.
- **Resiliencia energética**
    - Paneles solares y baterías mantendrán en funcionamiento al menos la infraestructura principal.
    - Un SAI proporcionará respaldo crítico para mantener la red y las cámaras en funcionamiento y permitir un apagado controlado del servidor de aplicaciones.

Para los que disfrutan con un pequeño diagrama:

[
![Diagrama del rack]({static}/images/self_hosted_home_1/rack.svg "Haz clic para ver a pantalla completa"){: .align-center}
]({static}/images/self_hosted_home_1/rack.svg "Haz clic para ver a pantalla completa")

## Servicios autoalojados

Entre los servicios que planeo desplegar se encuentran:

- [**TrueNAS**](https://www.truenas.com/), detallado más abajo en la sección de *Almacenamiento*.
- [**Home Assistant**](https://www.home-assistant.io/) para domótica e integración de todas las plataformas y fuentes de datos.
- [**Frigate NVR**](https://frigate.video/) para las cámaras, detección de objetos y comunicación con el timbre (también integrado en Home Assistant).
- [**Nextcloud**](https://nextcloud.com/) como nube personal (contactos, calendario, archivos, notas, etc.).
- [**Immich**](https://immich.app/) como biblioteca de fotos.
- [**Jellyfin**](https://jellyfin.org/) para la reproducción de vídeo.
- [**Music Assistant**](https://www.music-assistant.io/) para la reproducción de música.
- [**Paperless-ngx**](https://docs.paperless-ngx.com/) para gestionar documentos.
- [**AdGuard Home**](https://github.com/AdguardTeam/AdGuardHome) para bloquear anuncios en toda la casa.
- **Servicios auxiliares**: monitorización, comprobaciones de disponibilidad, registros, orquestación de copias de seguridad, NTP...

Mi intención es dar acceso a la mayoría de estos servicios a mi familia.
Eso amortizaría los costes de montaje y mantenimiento, a la vez que les aportaría más privacidad a sus vidas.

# 2. Red

La red es la base de todo lo demás, es clave para el rendimiento, seguridad y comodidad del sistema.

Aprovechando la oportunidad que brinda una reforma integral, voy a instalar **cables Ethernet Cat6a** por toda la casa.
Cada división tendrá **al menos un puerto RJ-45** en una toma de pared, y algunas varias, dependiendo del uso previsto.
Los cables Cat6a garantizan velocidad de **10 GbE**, que en un futuro serían alcanzables simplemente sustituyendo el switch, las tarjetas de red y los puntos de acceso WiFi; el cableado ya estaría listo.
Inicialmente las conexiones serán a 2,5 GbE, con la excepción de dos a 10 GbE para los dos ordenadores de sobremesa.

Todos los cables irán por las paredes hasta la sala de servidores, a [paneles de conexiones](https://es.wikipedia.org/wiki/Panel_de_conexiones) montados en el rack.

Como router y cortafuegos instalaré **IPFire** en un servidor dedicado, que será el núcleo de la instalación.
Un switch **UniFi** y varios puntos de acceso WiFi UniFi agregarán el tráfico y lo delimitarán en VLANs.
Habrá un switch secundario para las cámaras de seguridad, que se tratará en la sección *Cámaras y timbre*.

## Router/cortafuegos IPFire

[IPFire](https://www.ipfire.org/) es un software de router y cortafuegos de código abierto basado en GNU/Linux.
Lo instalaré en un servidor en rack pequeño, de bajo consumo pero robusto, con estos requisitos (ideales):

- Al menos 2 tarjetas de red SFP+ (una para la WAN, otra para la LAN, y opcionalmente otra para gestión dedicada o DMZ).
- CPU suficiente para sostener hasta 10 Gbps de velocidad WAN.
- Dos unidades SSD o NVMe para configurarlas en espejo para mayor redundancia.
- Fuentes de alimentación dobles para redundancia energética.
- El menor consumo posible, especialmente en reposo.

Todavía estoy investigando opciones para este servidor.
IPFire ofrece sus propios [dispositivos](https://store.lightningwirelabs.com/products/groups/firewall-appliances), pero se me hacen carísimos para lo que ofrecen, así que estoy buscando servidores en rack.

Lo mejor que he encontrado hasta ahora es la [Supermicro X10SDV-7TP8F](https://www.supermicro.com/en/products/motherboard/X10SDV-7TP8F), una placa base *system-on-chip* con una CPU Intel Xeon D-1587.
Cumple varios de los requisitos: potencia de cálculo suficiente para una WAN de 10 Gbps; bajo consumo de energía (10W en reposo, 45W TDP); 2 tarjetas de red SFP+ de 10 GbE integradas. Le faltan las dobles fuentes de alimentación y doble disco, pero nada es perfecto.

El equipo con IPFire se conectará directamente al router del proveedor de Internet (en modo puente) o a una [ONT](https://es.wikipedia.org/wiki/Terminal_de_red_%C3%B3ptica) dedicada.

Se encargará de estas responsabilidades:

- Terminar la conexión WAN (PPPoE o DHCP, dependiendo del proveedor).
- Proporcionar un **cortafuegos con estado** (*stateful*) tanto para IPv4 como para IPv6.
- Realizar **DHCP** y **DNS** para las redes internas.
- Gestionar túneles VPN **WireGuard** para el acceso remoto a la red doméstica.
- **Detección de intrusos** (*IDS*)

Quiero que IPv6 sea un ciudadano de primera clase: IPFire obtendrá un prefijo delegado del proveedor y lo dividirá entre las VLAN internas.
Esto, junto con una política de denegación por defecto, facilitará la apertura de servicios al exterior de forma controlada y segura, sin las molestias y el impacto en el rendimiento del NAT de IPv4.

## Switching y WiFi de UniFi

Conectado a IPFire habrá un [switch UniFi Pro HD 24 PoE](https://techspecs.ui.com/unifi/switching/usw-pro-hd-24-poe) que:

- Agregará todos los segmentos cableados (habitaciones, rack, cámaras, puntos de acceso WiFi).
- Proporcionará PoE para los puntos de  acceso y potencialmente otros dispositivos.
- Implementará etiquetado de VLAN y segmentación de cortafuegos a nivel de capa 2/3 en cooperación con IPFire.

Busqué y rebusqué switches para montar en rack, y ningún otro se acercaba en especificaciones a este UniFi por un precio comparable.
Tiene **4 puertos SFP+ de 10 GbE** para conectar los servidores IPFire y de aplicaciones, **2 puertos RJ-45 de 10 GbE** para mis ordenadores de sobremesa y **22 puertos RJ-45 de 2,5 GbE** con PoE.
La mayoría de los otros switches de 24 puertos que encontré solo tienen puertos de 1G, sin 10 GbE.
El tener 2,5 GbE en todas las conexiones va a darle un buen rendimiento a toda la red por mucho tiempo.

[
![Switch UniFi Pro HD 24 PoE]({static}/images/self_hosted_home_1/unifi_switch_pro_hd_24_poe.avif "Haz clic para ver a pantalla completa"){: .align-center}
]({static}/images/self_hosted_home_1/unifi_switch_pro_hd_24_poe.avif "Haz clic para ver a pantalla completa")

Para los puntos de acceso WiFi consideré los [puntos de acceso de Grandstream](https://www.grandstream.com/products/networking-solutions/indoor-wifi-access-points), que según dicen son de buena calidad, pero los descarté porque no disponen de banda de 6 GHz, que es la novedad del estándar WiFi 7.
Finalmente me decidí por los puntos de acceso WiFi de UniFi (muy probablemente el [U7 Pro](https://techspecs.ui.com/unifi/wifi/u7-pro)), porque funcionan con un solo cable Ethernet (2,5 GbE para el U7 Pro, pero en el futuro podría actualizar a un PA con 10 GbE), y se pueden gestionar junto con el switch UniFi.

Los puntos de acceso permitirán un roaming sin interrupciones por toda la casa y tendrán múltiples SSID:

- **SSID principal**: Para dispositivos de confianza (portátiles, móviles y tabletas de la familia).
- **SSID IoT**: Para dispositivos inteligentes inalámbricos, mapeado a la VLAN de IoT.
- **SSID de invitados**: Aislado de los servicios internos, solo con acceso a Internet.

[
![UniFi U7 Pro]({static}/images/self_hosted_home_1/unifi_u7_pro.avif "Haz clic para ver a pantalla completa"){: .align-center}
]({static}/images/self_hosted_home_1/unifi_u7_pro.avif "Haz clic para ver a pantalla completa")

Proxmox ejecutará un [UniFi Network Server](https://help.ui.com/hc/en-us/articles/360012282453-Self-Hosting-a-UniFi-Network-Server) en una máquina virtual, que permitirá la configuración del switch y los puntos de acceso sin conexión a la nube.
Estoy confiando que Ubiquiti no me la líe con futuros cambios que requieran conectividad en la nube, me enfadaría mucho si lo hicieran.
Este riesgo es la razón por la que elegí no usar cámaras UniFi, por ejemplo.
En el peor de los casos, solo tendría que reemplazar el switch y los puntos de acceso, es un riesgo calculado.

## Diseño de VLAN y modelo de confianza

La red se dividirá en **zonas de confianza**:

- **Interna (de confianza)**: Ordenadores, móviles y tablets de la familia.
- **IoT**: Dispositivos de domótica (enchufes, interruptores, electrodomésticos, TV, aire acondicionado...).
- **Cámaras**: Cámaras de seguridad y el videoportero.
- **Invitados**: Para visitas; solo Internet, sin acceso a LAN/IoT/Cámaras.
- **Gestión**: Ordenador personal, Proxmox, switches, router, puntos de acceso, gestión fuera de banda (IPMI, iDRAC).

Una vista de pájaro de las reglas de enrutamiento/cortafuegos:

- **Interna**: Puede acceder a servicios: Home Assistant, Frigate, recursos compartidos del NAS, etc.
- **IoT**: Conexión a Home Assistant; sin acceso directo a Internet, excepto para un puñado de puntos finales en lista blanca si es absolutamente necesario; sin acceso a datos personales.
- **Cámaras**: Conexión a Frigate; sin acceso a Internet en absoluto, no quiero que los datos de mis cámaras se exfiltren; sin acceso a datos personales.
- **Invitados**: Solo acceso a Internet; sin acceso a ningún servicio interno.
- **Gestión**: Solo accesible desde un pequeño conjunto de dispositivos de confianza para administración de sistemas.

Las reglas de cortafuegos y enrutamiento serán aplicadas conjuntamente por IPFire y el switch UniFi, asegurando que **el tráfico de las cámaras y del IoT nunca llegue a Internet**, y que los invitados nunca lleguen a nada interno.

## VPN WireGuard

Para un acceso externo seguro, configuraré [Wireguard](https://www.wireguard.com/) en IPFire:

- Cada dispositivo (portátil, móvil, tableta) dispone de su propio par de claves pública y privada, y una IP virtual.
- Los dispositivos conectados por WireGuard aterrizan en una subred que tiene acceso controlado a la LAN y a la gestión.
- Esto evitará abrir los servicios internos a Internet, y en su lugar sólo es necesaria una única ruta auditable: WireGuard → IPFire → servicios internos.
- WireGuard tiene funciones limitadas, pero por eso mismo su superficie de ataque es mucho menor que la de otras VPN.

Esto debería permitir el control remoto completo de Home Assistant, las cámaras y las tareas de administración sin exponer esos servicios directamente a Internet.

# 3. Servidor de aplicaciones

El núcleo del homelab se ejecutará en [Proxmox VE](https://proxmox.com/en/), instalado en un único equipo de servidor con gestión remota adecuada y redundancia.

Proxmox es un sistema operativo seguro y robusto basado en Linux que simplifica la ejecución de servicios virtualizados o en contenedores.
Esto proporciona una serie de beneficios:

- **Código abierto**: Puede parecer obvio, pero evita la dependencia de un proveedor.
- **Mezcla de VMs y contenedores**: Ambos se pueden gestionar a través de la misma interfaz.
- **Seguridad a través del aislamiento**: Si un servicio se ve comprometido, el atacante no obtendría acceso a todo el sistema, sino solo a los datos y la red a la que tenga acceso.
- **Portabilidad y pruebas**: Podría tener una instancia de Proxmox de preproducción, por ejemplo en mi ordenador de sobremesa, como banco de pruebas para nuevos servicios. Cuando estén listos, se pueden migrar a la instancia de Proxmox de producción.
- **Actualizaciones más seguras**: Hacer una instantánea de las máquinas virtuales es una forma fácil de probar una actualización de software y revertirla si se encuentran problemas.
- **Copias de seguridad**: Además de las instantáneas de ZFS, Proxmox tiene su propio [servidor de copias de seguridad](https://proxmox.com/en/products/proxmox-backup-server/overview) de código abierto, para respaldos incrementales y deduplicados.
- **Disponibilidad y clústeres**: No lo voy a usar, porque lo considero excesivo para mi caso de uso, pero es posible tener redundancia y conmutación por error automática de las instancias de Proxmox.

## Proxmox y consideraciones sobre licencias

[La licencia de Proxmox es **por CPU instalada**](https://proxmox.com/en/products/proxmox-virtual-environment/pricing).
Para reducir los costes recurrentes, estoy buscando servidores de una sola CPU, pero con suficientes núcleos para ejecutar todos los servicios previstos y tener margen para crecer en el futuro.

Las CPU modernas ya alcanzan los cientos de núcleos en un sólo zócalo, lo que es más que suficiente para un homelab.

## Opciones de hardware para el servidor

El formato objetivo es un servidor en rack reacondicionado, con estas características:

- CPU de bajo consumo con al menos 24 núcleos, idealmente 32 o más.
- Al menos 128 GB de RAM ECC. ECC es fundamental en este servidor para evitar la corrupción silenciosa de datos. La RAM DDR5 sería ideal, pero con la [actual escasez de memoria](https://en.wikipedia.org/wiki/2024%E2%80%932026_global_memory_supply_shortage) me conformaré con DDR4.
- Espacio en el chasis para al menos 8 HDD, idealmente 10 o 12 para tener margen de crecimiento si es necesario.
- Soporte para doble almacenamiento NVMe, o como mínimo SSD.
- Al menos una tarjeta de red SFP+ de 10 GbE.
- Fuentes de alimentación dobles redundantes.
- Gestión remota compatible con IPMI.

La serie Dell PowerEdge tiene una amplia gama de modelos y son fáciles de encontrar reacondicionados, así que son mi punto de partida:

- **Basados en Intel**
    - **[R730](https://i.dell.com/sites/doccontent/shared-content/data-sheets/en/Documents/Dell-PowerEdge-R730-Spec-Sheet.pdf)**: Antiguo pero muy común y barato. Doble zócalo para Intel Xeon, hasta 3 TB de DDR4, 10 GbE a través de una NDC (*Network Daughter Card*) opcional, **sin NVMe**, gestión por iDRAC (todos los PowerEdge).
    - **[R740](https://www.dell.com/content/dam/digitalassets/active/en/unauth/data-sheets/products/servers/Dell_EMC_PowerEdge_R740_Spec_Sheet.pdf) / [R750](https://www.delltechnologies.com/asset/en-us/products/servers/technical-support/dell-emc-poweredge-r750-spec-sheet.pdf)**: Generaciones más nuevas con CPUs más eficientes, más núcleos, NVMe, mejor PCIe (Gen 3/4 según el modelo), mejor iDRAC...
- **Basados en AMD**
    - [**R7415**](https://i.dell.com/sites/csdocuments/Shared-Content_data-Sheets_Documents/en/poweredge-r7415-spec-sheet-en.pdf): **AMD EPYC de un solo zócalo (1ª generación)**; excelente densidad de núcleos y ancho de banda de memoria con un menor consumo y coste que los componentes equivalentes de Intel, y diseñados como plataformas de un solo zócalo.
    - [**R7515**](https://i.dell.com/sites/csdocuments/product_docs/en/poweredge-r7515-spec-sheet.pdf): **AMD EPYC de 2ª y 3ª generación** de un solo zócalo, hasta 64 núcleos.
    - **R7525**: Como el R7515 pero con doble zócalo. No es un factor decisivo porque Proxmox solo cobra por zócalo de CPU **en uso**, por lo que puede ser una opción si el precio es justo.

Las plataformas **AMD EPYC de un solo zócalo** parecen particularmente atractivas para Proxmox porque:

- Ofrecen un mayor número de núcleos que Intel y más ancho de banda de memoria en un solo socket, evitando sobrecostes en la licencia.
- Las plataformas EPYC son conocidas por su gran rendimiento en virtualización y su alta densidad de E/S.

[
![Dell PowerEdge R7515]({static}/images/self_hosted_home_1/dell_poweredge_r7515.webp "Haz clic para ver a pantalla completa"){: .align-center}
]({static}/images/self_hosted_home_1/dell_poweredge_r7515.webp "Haz clic para ver a pantalla completa")

Un Dell PowerEdge R7415 o R7515 parece la mejor opción, pero lo compararé con ofertas similares de otros proveedores:

- [Supermicro AS-2014S-TR](https://www.supermicro.com/en/products/system/datasheet/as-2014s-tr): muy similar, pero tiene más líneas PCIe y más bahías de disco con espacio para 12 HDD, por lo que permitiría la expansión del NAS si fuera necesario.
- [HPE ProLiant DL385 Gen10 Plus](https://www.hpe.com/psnow/doc/a00073549enw): Doble socket; hasta 28 unidades de disco. Excesivo.
- [Lenovo ThinkSystem SR665](https://lenovopress.lenovo.com/lp1269-thinksystem-sr665-server): Admite CPUs AMD EPYC de un solo socket con el sufijo "P". Según se informa, son difíciles de encontrar reacondicionados, y los de un solo socket aún más, por lo que no es mi primera opción.

Una cosa que me hace reacio a elegir HPE es que no ofrecen descargas gratuitas de actualizaciones de BIOS o firmware sin un contrato de soporte, que es prohibitivamente caro para un usuario doméstico.
Ya me pasó con mi actual HPE Microserver Gen10, así que probablemente me decante por Dell o Supermicro para el próximo, ya que tienen descargas gratuitas sin contrato.

Mi elección final dependerá de la disponibilidad local y el precio de las unidades reacondicionadas, pero espero conseguir uno de esos fantásticos Dell PowerEdge con un AMD EPYC.

## Redundancia y fiabilidad

El servidor Proxmox se trata como el **nodo de infraestructura principal**, no es un juguete.
Aunque mi casa inteligente está diseñada para que siga funcionando incluso si Home Assistant se cae, dado que todos mis servicios personales se ejecutarán en este hardware, es de suma importancia que se mantenga activo y en buen estado.

Con esto en mente, estos son los pasos que tomaré para garantizar la disponibilidad del servidor de aplicaciones:

- **Fuentes de alimentación dobles**: Conectadas a enchufes separados, para que un fallo en una sola fuente de alimentación o en un circuito eléctrico no tumbe el servidor.
- **SAI**: Conectado al menos a un SAI, para energía de emergencia y apagado controlado. Más detalles en la sección *Electricidad y resiliencia* más abajo.
- **Grupo de arranque / VMs**: **2 unidades NVMe** en un grupo ZFS espejado (coloquialmente llamado "RAID1 en ZFS"). Esto proporciona redundancia para el host de Proxmox, los servicios y la configuración, de modo que si una unidad falla, el sistema seguirá funcionando (y la unidad defectuosa podría intercambiarse en caliente por una nueva y ZFS reconstruiría el grupo automáticamente).
- **Puertos de red dobles**: Usar al menos dos tarjetas de red: una para gestión; otra para el tráfico de las VMs y el almacenamiento. Podría también agregar enlaces de red para tener conexiones redundantes, lo que significaría 2 para gestión y/o 2 para tráfico.
- **Gestión remota**: [IPMI](https://en.wikipedia.org/wiki/Intelligent_Platform_Management_Interface), iDRAC, iLO o equivalente para permitir la gestión fuera de banda, el acceso a la BIOS y el control remoto de la alimentación.
- **Consola física para acceso de emergencia**: tendré una consola barata (monitor y teclado) a mano para conectarme directamente al servidor si fuese necesario.

# 4. Almacenamiento

Tengo grandes necesidades de almacenamiento, así que desde el principio planteo montar un buen [NAS](https://es.wikipedia.org/wiki/Almacenamiento_conectado_en_red), con velocidad, redundancia y fiabilidad.

## ¿Por qué no Synology?

Inicialmente consideré un NAS de [Synology](https://www.synology.com/es-es).
En particular, el [RS1221+](https://www.synology.com/es-es/products/RS1221+]) parecía ser exactamente lo que estaba buscando.

[
![Synology RS1221+]({static}/images/self_hosted_home_1/synology_rs1221+.webp "Haz clic para ver a pantalla completa"){: .align-center}
]({static}/images/self_hosted_home_1/synology_rs1221+.webp "Haz clic para ver a pantalla completa")

Los productos de Synology son populares por una buena razón: son fáciles de gestionar y tienen un ecosistema muy rico.
Sin embargo, sus recientes políticas y decisiones empresariales los han hecho menos atractivos, y para mí en particular son factores decisivos:

- Una postura cada vez más [restrictiva sobre los discos de otras marcas](https://www.theverge.com/news/652364/synology-nas-third-party-hard-drive-restrictions), con modelos que:
    - Advierten, se quejan o degradan la experiencia de usuario cuando se usan discos que no son de Synology.
    - En algunos casos, limitan el soporte o la funcionalidad según el proveedor del disco.
- Cambios progresivos para dificultar el cambiar de proveedor, algo que va en contra de la filosofía **abierta y basada en estándares** de este homelab.

Dadas estas preocupaciones, tomé la decisión de **evitar Synology** y en su lugar usar plataformas abiertas y hardware genérico sobre el que tendría control total.

## TrueNAS

[TrueNAS](https://www.truenas.com/) es probablemente el sistema operativo de código abierto más conocido y especializado para NAS.
Es robusto, que es la característica número uno que uno quiere para su almacenamiento.

Solo funciona con ZFS, que es lo que quiero usar para mi capa de datos, y su interfaz de usuario simplifica la gestión, la monitorización y las alertas.
Por mucho que me guste la tecnología y meterme en fregaos, ya voy a tener bastante trabajo montándolo todo, así que agradezco todo lo que me facilite la vida sin comprometer los principios.

Consideré [openmediavault (OMV)](https://www.openmediavault.org/) porque es un competidor directo, también de código abierto y basado en Linux.
Lo descarté porque es más flexible (por ejemplo ZFS es opcional y no de serie), y está pensado para gente que busca ejecutar aplicaciones en su NAS, pero yo no lo necesito porque tendré un servidor de aplicaciones separado para ese propósito.

Así que empecé a considerar montar un servidor separado para TrueNAS.
Dadas mis necesidades de almacenamiento me haría falta otra máquina potente (al menos 64 GB de RAM, y otra tarjeta de red de 10 GbE).
Como todo en la vida, tiene sus pros y sus contras:

- Pros:
    - Clara separación de responsabilidades: almacenamiento en una máquina, computación en otra.
    - Buen aislamiento de fallos: si el nodo de computación falla, el almacenamiento sigue funcionando.
- Contras:
    - Mayor **coste inicial**: otro chasis de servidor, más fuentes de alimentación, más tarjetas de red.
    - Mayor **consumo eléctrico en el día a día**.
    - Para un homelab familiar parece excesivo.

Había dos alternativas sobre las que había leído:

1. Proxmox tiene soporte para ZFS, por lo que podría hacer también de NAS.
    - Configuración **manual de ZFS**, una cosa más que aprender.
    - **Sin monitorización ni alertas** de serie.
    - Acceso directo al hardware, **sin pérdida de rendimiento por virtualización**.
2. Ejecutar una **máquina virtual de TrueNAS** dentro de Proxmox:
    - TrueNAS se ejecuta como una máquina virtual con **acceso directo al conjunto de discos duros**, pasando directamente el [HBA](https://es.wikipedia.org/wiki/Adaptador_de_host) en PCIe al que estarán conectados.
    - Los discos duros están **dedicados a TrueNAS**; Proxmox no los toca.
    - ZFS se utiliza en la capa de TrueNAS para redundancia, instantáneas y replicación.
    - La pérdida de rendimiento es <5% según comentarios de usuarios.
    - TrueNAS disfrutará de la **alta disponibilidad** del servidor de aplicaciones (doble fuente de alimentación, doble NVMe, redes redundantes...)

Tras analizar las opciones con sus pros y sus contras, mi decisión es optar por TrueNAS como máquina virtual, me parece el mejor compromiso en cuanto a mantenibilidad, reducción del número de equipos, coste inicial, consumo eléctrico y fiabilidad del sistema.
Dejar que Proxmox gestione los discos duros debería funcionar, pero perdería más tiempo y me quedaría sin la monitorización y las alertas integradas de TrueNAS.

## Diseño del almacenamiento

A grandes rasgos:

- **IPFire (rápido)**:
    - Registros de red (accesos al cortafuegos, informes del IDS, conexiones VPN, etc.).
- **Pool de Proxmox (muy rápido, redundante)**:
    - Dos SSD NVMe en espejo ZFS para:
        - El host de Proxmox.
        - Máquinas virtuales y contenedores.
        - Configuración, bases de datos y metadatos.
    - El sistema seguirá funcionando si falla un disco.
- **Pool de TrueNAS (lento, redundante)**:
    - Múltiples discos duros en un pool ZFS.
    - Inicialmente planeo 8 discos duros en RAIDZ2, idealmente con espacio para ampliar hasta 12.
    - Tolerancia al fallo de hasta 2 discos simultáneamente.
    - Almacena:
        - Las fotografías de Immich.
        - Los vídeos de Jellyfin.
        - La música de Music Assistant.
        - Los datos de Nextcloud.
        - Los documentos de Paperless.
        - Las grabaciones de las cámaras.
        - Las copias de seguridad de Proxmox.
- **Instantáneas y replicación**:
    - TrueNAS tomará **instantáneas periódicas de los datos**.
    - Las instantáneas de datos críticos (Nextcloud, Immich, Paperless, algunas grabaciones de Frigate) se replicarán a una **copia de seguridad remota** (fuera de casa).

Esta combinación proporciona tanto **redundancia local** como **copias de seguridad externas**, lo cual es esencial: RAID/ZFS *no* es una copia de seguridad.

# 5. Cámaras y timbre

Las cámaras son una parte integral de este homelab, pero también una importante **preocupación de seguridad y privacidad**.
Quiero tener cámaras tanto fuera como dentro de la casa, pero tengo que asegurarme por completo de que **nadie esté espiando** a través de ellas.
También quiero tener un videotimbre que suene en mi smartphone aunque esté fuera de casa, pero tiene que funcionar sin conexión a la nube.

Primero haré que un instalador pase cables Ethernet por las paredes para las cámaras, de modo que estarán conectadas y alimentadas a través de PoE.
Hay una amplia gama de cámaras y timbres PoE disponibles.

## Plan inicial: ¿UniFi o Reolink?

Al principio dudaba si optar por cámaras UniFi, porque son de buena calidad (aunque caras), su software y aplicaciones son de lo mejor y ya estoy planeando entrar en su ecosistema con el switch y los puntos de acceso.
Sin embargo, Ubiquiti ha intentado en el pasado [obligar a usar una cuenta en su nube para UniFi Protect](https://www.reddit.com/r/Ubiquiti/comments/1cifnut/unifi_protect_now_requires_cloudremote_access_for/), así que no puedo confiar en que sus sistemas sigan funcionando de forma exclusivamente local, que es uno de mis objetivos declarados.

Habiendo descartado las cámaras UniFi, mi otra opción era [Reolink](https://reolink.com/) por su buena relación calidad-precio y su perfecta [integración con Home Assistant](https://www.home-assistant.io/integrations/reolink/).
El [Reolink RLN16-410](https://reolink.com/product/rln16-410/) es un NVR con 16 puertos PoE, por lo que las cámaras se conectarían y grabarían directamente en él.
Eso simplificaría la configuración y se integraría con Home Assistant.

Sin embargo, después de investigar un poco, acabé descubriendo que Reolink **no tiene soporte para IPv6** en absoluto, y no hay planes para añadirlo.
La falta total de soporte para IPv6 es especialmente problemática en una red donde IPv6 es un ciudadano de primera clase.
Con el tiempo, los servicios y los proveedores de internet dependerán más de IPv6, y mantener un ecosistema de cámaras solo con IPv4 crea fricciones y deuda técnica innecesarias.
Sin ningún tipo de promesa de que IPv6 será soportado en el futuro, me arriesgaría a tener que reemplazar todas las cámaras y el NVR en algún momento, así que volví a buscar alternativas.

## Frigate y cámaras Dahua

Mi solución final es dejar de depender de sistemas cerrados y en su lugar tener el excelente [Frigate NVR](https://frigate.video/) gestionando las cámaras directamente.
Frigate se ejecutará como una máquina virtual en el servidor Proxmox.

Buscando un fabricante de cámaras que respete los estándares y tenga soporte para IPv6, encontré [Dahua](https://www.dahuasecurity.com/):

- **Soporte de estándares**:
    - ONVIF para descubrimiento y control básico.
    - RTSP para los flujos de vídeo y audio.
    - Soporte de IPv6.
- Capacidades de **audio bidireccional** que respetan los estándares.
- Un amplio ecosistema y documentación de la comunidad de *self-hosting*.

Instalaré:

- **12 cámaras Dahua**, una mezcla de interiores y exteriores.
- **1 videoportero Dahua** con audio bidireccional.

Todas las cámaras y el timbre estarán conectados mediante cableado **Cat6a con PoE**, asegurando una buena señal y haciendo que sean más difíciles de manipular e interferir.

Frigate almacenará las grabaciones en TrueNAS a través de NFS o SMB, por lo que se beneficiarán automáticamente de la redundancia de sus discos duros, las instantáneas de ZFS y las rutinas de copia de seguridad.

## Diseño de red para las cámaras

Todas las cámaras se conectarán a un switch Ethernet dedicado en el rack de capa 2 con PoE.
Este switch se conectará a un único puerto del switch UniFi, de esa manera éste podrá etiquetar todas las cámaras en una **VLAN dedicada**:

- Recibirán direcciones solo en la **VLAN de cámaras** (tanto IPv4 como IPv6).
- El cortafuegos IPFire **bloqueará cualquier salida a Internet**.
- Solo se podrá acceder a ellas desde:
    - Frigate (para la ingesta de vídeo y la comunicación bidireccional con el videoportero).
    - Un conjunto muy pequeño de sistemas de administración (para configuración).

La principal desventaja de este enfoque es que el switch secundario solo podrá usarse para conectar las cámaras, porque será el router UniFi el que gestione la VLAN, pero debería ser lo suficientemente barato como para que tener algunos puertos sin usar no sea un problema.

## Detección de objetos

Frigate NVR tiene detección de objetos integrada:

- Frigate se ejecuta como una máquina virtual en Proxmox.
- Recibe los flujos RTSP de las cámaras Dahua y el videoportero.
- Realiza **detección de movimiento y de objetos** (personas, coches, etc.).
- Gestiona la grabación basada en eventos, las instantáneas y las políticas de retención.

Para una detección de objetos eficiente, Frigate soporta [aceleración hardware](https://docs.frigate.video/configuration/object_detectors):

- Se conectará un [Coral TPU](https://docs.frigate.video/configuration/object_detectors/#edge-tpu-detector) por USB o PCIe al servidor Proxmox.
- Proxmox pasará el dispositivo a la máquina virtual de Frigate.
- Como dispositivo de hardware especializado, el TPU tiene un bajo consumo de energía pero es capaz de procesar múltiples flujos de vídeo en tiempo real.
- Es mucho más eficiente y rentable que usar una tarjeta gráfica para un despliegue de esta escala.

## Videoportero

El videoportero puede verse como una cámara normal, pero además quiero poder hablar con quien llame a la puerta.
Frigate puede [gestionar el audio bidireccional](https://docs.frigate.video/configuration/live/#two-way-talk) con el timbre Dahua, permitiendo una comunicación exclusivamente local y que preserva la privacidad, sin ninguna nube del fabricante.

Recuerda que todas las cámaras solo serán accesibles a través de la red local, pero cuando esté fuera mis dispositivos se conectarán a través de la VPN de Wireguard y operarían como si estuvieran en casa.

Cuando alguien llame al timbre se activará un evento en Home Assistant, y ahí podré realizar todo tipo de acciones, desde enviar una notificación a nuestros teléfonos, hacer sonar un timbre en casa si estamos presentes, reproducir un mensaje grabado o incluso hacer que una IA converse con el visitante.

# 6. Electricidad y resiliencia

La planificación de la alimentación eléctrica tiene dos partes separadas:

1. Reducir el consumo de energía, tanto en el día a día normal como en caso de emergencia (p. ej. en un apagón).
2. Asegurar los datos y la degradación gradual de los servicios en caso de pérdida de energía.

## Sobre el consumo de energía

La casa tendrá una instalación solar completa:

- Un montón de paneles solares que deberían cubrir las necesidades de la casa la mayoría de los días del año.
- Suficientes baterías para cubrir el consumo de la casa la mayoría de las noches del año.
- La red eléctrica probablemente solo será necesaria en días nublados de invierno o días de consumo excepcional. No planeo ser completamente independiente de la red eléctrica.
- Un circuito de emergencia permitirá que las baterías y los paneles proporcionen electricidad en caso de un apagón de la red.

Con este sistema instalado, el rack debería estar correctamente alimentado en la mayoría de situaciones.
Sin embargo, me puedo imaginar algunos casos en los que podría quedarse corto:

- Varios días nublados en invierno podrían agotar las baterías por completo. No sabré el rendimiento con seguridad hasta que nos mudemos y empiece a recopilar estadísticas. Esto significa que no puedo depender solo de las baterías solares para alimentar el rack.
- Un apagón prolongado de la red (como [el de 2025](https://es.wikipedia.org/wiki/Apag%C3%B3n_en_la_pen%C3%ADnsula_ib%C3%A9rica_de_2025)) podría ser problemático, especialmente en invierno.

Como protección contra estos casos extremos, mi plan es instalar un SAI en el rack y programar los servicios para esa eventualidad.

## Emergencia de alimentación: SAI y estrategia de apagado

Los componentes críticos estarán conectados a un [SAI](https://es.wikipedia.org/wiki/Sistema_de_alimentaci%C3%B3n_ininterrumpida) (Sistema de Alimentación Ininterrumpida):

- El router IPFire.
- El switch principal UniFi.
- El switch PoE de las cámaras.
- El servidor Proxmox.

Tengo dos objetivos:

- Mantener **la red + cámaras + servicios principales** funcionando el mayor tiempo posible durante un corte de luz.
- Asegurar que el **servidor Proxmox se apague limpiamente** antes de que la batería del SAI se agote, para mantener los datos a salvo.

El flujo de apagado sería algo así:

1. El SAI se comunica por USB o SNMP con un agente de monitorización (ya sea en Proxmox o en un pequeño dispositivo auxiliar).
2. Al activarse la batería del SAI (y lo mismo si hay un apagón de la red y el sistema depende de las baterías solares) se activa un modo de ahorro de energía en todos los sistemas y se me notifica.
3. Al alcanzar un umbral de batería baja:
    - Proxmox inicia el apagado ordenado de las VM no críticas por orden de prioridad (p. ej., Jellyfin, Music Assistant, Immich y Nextcloud primero).
4. Al alcanzar un umbral de batería crítico:
    - Proxmox apaga todas las VM para evitar la pérdida de datos.
    - El host de Proxmox se apaga.
5. La red y las cámaras permanecen activas mientras el SAI pueda mantenerlas.

Esto protege la integridad de los datos mientras se mantiene cierto nivel de vigilancia y capacidad de resolución de problemas remota.

# 7. Copias de seguridad y recuperación

La redundancia no es una copia de seguridad.
Tiene que haber una copia externa de los datos críticos en caso catástrofe en la casa:

- Copias de seguridad regulares de las **VM de Proxmox** (configuración + imágenes de disco) al NAS.
- Replicación de las copias de seguridad de Proxmox a una ubicación externa.
- Copia de seguridad de los **conjuntos de datos críticos** del NAS a la ubicación externa:
    - Colección de fotos (Immich), con la base de datos de metadatos.
    - Archivos y datos de Nextcloud (calendario, contactos...), y su base de datos.
    - Documentos de Paperless y su base de datos.
    - Clips de eventos de Frigate (al menos metadatos y grabaciones críticas, p. ej., detecciones de objetos o alertas).

Las **pruebas de restauración** periódicas formarán parte del modelo operativo: una copia de seguridad solo es tan buena como la última prueba de restauración exitosa.
El plan es probar la restauración de al menos una VM y un conjunto de datos periódicamente para asegurar que las herramientas y los procedimientos realmente funcionan.

# 8. Operaciones, monitorización y prácticas de seguridad

La facilidad de mantenimiento es una preocupación clave para mis sistemas.
Disfruto trasteando con todo esto, es un hobby, pero una vez todo esté montado y configurado mi expectativa es que funcione sin problemas durante meses.
Esa es la experiencia con [mi homelab actual]({filename}2023-12-29_homelab.md), y lo que busco con el nuevo.

Las prácticas operativas que planeo para mantener el sistema:

- **Monitorización**:
    - Comprobaciones básicas de disponibilidad para los servicios principales, por ejemplo con [Uptime Kuma](https://uptime.kuma.pet/), con notificaciones en tiempo real.
    - Monitorización de recursos de CPU/RAM/disco/red, con alertas para estar al tanto de posibles cuellos de botella.
    - Alertas de SMART y de *scrub* de ZFS para el almacenamiento.
    - Alertas de intrusión de IPFire.
- **Estrategia de actualización**:
    - Solo versiones estables.
    - Tomar instantáneas de Proxmox y de las VM antes de actualizaciones críticas.
    - Actualizar primero los servicios menos críticos, luego los componentes principales.
- **Seguridad**:
    - Cortafuegos con política de **denegación por defecto**.
    - VLANs para IoT y cámaras **sin salida a Internet**.
    - El menor número posible de servicios expuestos a Internet, y esos con **mínimos permisos y acceso a datos**.
    - **Solo VPN** para el acceso remoto a Home Assistant, Frigate y cualquier otro servicio de la casa que no esté expuesto a Internet.
    - Mínima superficie de ataque en IPFire y Proxmox:
        - **Solo puertos necesarios** abiertos.
        - Administración solo a través de **dispositivos de confianza** (ordenadores de sobremesa y portátiles).
        - **Claves y contraseñas robustas**.
        - **MFA** (autenticación de múltiples factores) donde sea compatible.
        - Software **actualizado**.

# 9. Próximos pasos

Este artículo recoge el **diseño objetivo** al que he llegado después de meses de investigación.
La implementación se llevará a cabo por etapas, que sin duda acabarán solapándose:

1. **Adquirir el servidor para el router/cortafuegos**, instalar IPFire y comenzar la configuración básica de enrutamiento/cortafuegos.
2. **Adquirir el servidor de aplicaciones** e instalar Proxmox VE.
3. **Adquirir e instalar el rack, los paneles de parcheo, los switches** una vez que la sala de servidores dedicada de la casa esté lista.
4. **Instalar los servidores y conectarlo todo**; conectar todos los cables de red; conectar los dispositivos al SAI para la alimentación; arrancar los servidores.
5. **Adquirir e instalar los discos duros** en el servidor de aplicaciones; configurar la **VM de TrueNAS** en Proxmox.
6. **Configurar la monitorización, el registro de eventos y las alertas**.
7. **Poner en marcha Home Assistant**, integrar los dispositivos inteligentes principales y empezar a definir automatizaciones.
8. **Desplegar Frigate** e integrar todas las cámaras Dahua y el timbre.
9. **Desplegar Nextcloud, Immich, Jellyfin, Music Assistant, Paperless**, apuntándolos al almacenamiento de TrueNAS.
10. **Servicios de apoyo** para monitorización, registro de eventos, alertas, etc.
11. **Adquirir y configurar el SAI**.

Cada uno de estos pasos generará su propio conjunto de notas, fragmentos de configuración y reflexiones del tipo "ojalá hubiera sabido esto antes".
Por eso este artículo está etiquetado como "Parte 1", porque tengo la intención de seguir documentando cómo este homelab evoluciona del diseño a la realidad.

[Suscríbete]({filename}../pages/subscribe_es.md) para estar al tanto de los nuevos artículos.

¿Tienes alguna idea, sugerencia o comentario? ¡Déjame un comentario abajo!
