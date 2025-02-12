Title: Comentarios autoalojados
Date: 2025-02-10
Lang: es
Category: Software
Tags: blog,free-software,howto,linux,privacy,self-hosting
Slug: self-hosted-comments

Hace unos días recibí un email de un lector y [compañero bloguero](https://zenodotus280.mataroa.blog/), para hacerme saber que seguía mi blog y también me dio un toque de atención sobre [mi resolución de Año Nuevo de escribir al menos un artículo cada mes de 2025]({filename}../personal/2025-01-04_new_years_resolutions_es.md#blog), y que ya estaba empezando a incumplir.

Me encanta recibir mensajes así, porque si una persona se toma la molestia de enviarme un email seguro que hay otras 99 que lo han pensado pero no lo han hecho.
Por eso tras recibir el email decidí dar prioridad a algo que tenía pendiente desde hacía tiempo: añadir comentarios al blog.
Y ojo, spoiler: **objetivo conseguido**.

Quería que fuese algo rápido, por lo que en vez de buscar la opción perfecta iba a optimizar por la que me tomase menos tiempo para implementarla.
Eso significaba empezar probando con las opciones ya integradas en el tema [Reflex](https://github.com/haplo/reflex) que uso en el blog (heredero de [Flex](https://github.com/alexandrevicenzi/Flex)):

- [Disqus](https://disqus.com/): probablemente la plataforma más popular para comentarios en la web.
Es muy cómoda y potente, pero totalmente cerrada y muy seguramente espía y vende nuestros datos.
- [Isso](https://isso-comments.de/): software autoalojado al estilo Disqus.

Quienes me conocen pensarán que habría saltado de cabeza para Isso, pero sinceramente mi primer intento fue con Disqus, porque habría sido lo más rápido: abrir una cuenta, poner una clave en las opciones de Pelican y a correr.
Bueno pues mi gozo en un pozo porque resulta que ¡[Disqus ya no tiene plan gratuito](https://disqus.com/pricing/)!
No me importa pagar por servicios que merezcan la pena, pero no por los comentarios en este humilde blog, así que me olvidé de Disqus y me puse a mirar los detalles de Isso.

Lo que vi de Isso me gustó:

- Autoalojado en mi propio dominio.
- Programado en Python: instalación sencilla en un virtualenv y me facilitaría colaborar con el proyecto llegado el caso.
- SQLite como base de datos, no hace falta un servidor MariaDB o Postgres.
Esta fue una de las principales razones por la que [elegí Shynet para las analíticas del blog]({filename}2022-05-27_privacy_respecting_self_hosted_web_analytics_es.md).

Lo único que no me gustó de Isso es que el desarrollo parece algo parado, hay varios PRs que llevan meses esperando merge.
Pero no parece ser un proyecto muerto, tengo la esperanza de que siga habiendo nuevas versiones al menos para mantenerlo al día en cuanto a compatibilidad y seguridad.

Por cierto que acabé descubriendo [Remark42](https://github.com/umputun/remark42/) como alternativa, después de haber desplegado Isso en mi servidor.
Pinta muy bien tanto en funcionalidades como en estado de desarrollo, pero personalmente habría seguido eligiendo Isso por estar ya integrado en el tema de mi blog.

## Detalles técnicos

Instalé Isso en el mismo servidor que alberga este blog, un humilde VPS de 2 GB de RAM.
No necesité más que seguir la [documentación oficial](https://isso-comments.de/docs/reference/installation/#init-scripts), pero por si alguien tiene interés dejo aquí el proceso:

1. Instalar *isso* y un servidor WSGI (yo prefiero gunicorn):

        :::shell
        # create new user for isolation
        adduser --disabled-password isso
        
        # install isso
        su - isso
        virtualenv venv
        source venv/bin/activate
        pip install isso gunicorn
        
2. Crear el fichero de configuración de *isso* en */home/isso/isso.cfg*:

        :::ini
        # https://isso-comments.de/docs/reference/server-config/
        
        [general]
        dbpath = /home/isso/comments.db
        host = https://blog.fidelramos.net/
        notify = smtp
        
        [server]
        listen = http://localhost:8081/
        
        [smtp]
        host = localhost
        port = 25
        security = none
        to = <notification_email@example.com>
        from = isso@blog.fidelramos.net
        timeout = 5
        
        [hash]
        salt = Eech7co8Ohloopo9Ol6baimi
        algorithm = pbkdf2:10000:6:sha256
        
        [admin]
        enabled = true
        password = <PASSWORD>
        
3. Configurar el proxy inverso con Caddy añadiendo una sección en */etc/caddy/Caddyfile*:

        :::text
        isso.fidelramos.net {
            reverse_proxy localhost:8081
            encode zstd gzip
        }

4. Añadir una unidad de servicio de *systemd* en */etc/systemd/system/isso.service* para ejecutar *isso* automáticamente. [La documentación de Isso incluye otros sistemas de init](https://isso-comments.de/docs/reference/installation/#init-scripts).

        :::systemd
        [Unit]
        Description=isso commenting system
        Documentation=man:isso(8)
        
        # Require the filesystems containing the following directories to be mounted
        RequiresMountsFor=/home/isso
        
        ConditionPathIsDirectory=/home/isso
        ConditionPathIsReadWrite=/home/isso
        
        ConditionFileIsExecutable=/home/isso/venv/bin/gunicorn
        
        # Start only if there is a conf file
        ConditionPathExistsGlob=/home/isso/isso.cfg
        
        [Service]
        
        Environment=ISSO_SETTINGS="/home/isso/isso.cfg"
        ExecStart=/home/isso/venv/bin/gunicorn -b localhost:8081 -w 4 --preload -n gunicorn-isso --log-file /home/isso/isso.log isso.run
        
        #UMask=0007
        Restart=on-failure
        TimeoutSec=1
        User=isso
        
        LimitNOFILE=16384
        LimitNPROC=16384
        LimitLOCKS=16384
        
        # ensures that the service process and all its children can never gain new
        # privileges.
        NoNewPrivileges=true
        
        [Install]
        WantedBy=multi-user.target
        
5. Añadir registros A y/o AAAA a tu DNS (*isso.fidelramos.net* en mi caso) apuntando al servidor.

6. Activar e iniciar *isso*, y recargar *caddy*:

        shell
        systemctl enable isso
        systemctl start isso
        systemctl reload caddy
        
7. Ahora puedo acceder a [isso.fidelramos.net/admin](https://isso.fidelramos.net/admin).

8. Añadir la configuración necesaria en *pelicanconf.py*:

        :::python
        ISSO_URL = "//isso.fidelramos.net"
        ISSO_OPTIONS = {
            "vote": "false",
        }

9. Desplegar el blog. ¡Ya hay comentarios!

## El futuro

Estoy deseoso de ver cuánto uso tendrán los comentarios.
Seguro que me animan a escribir más.

Me preocupa el spam, porque Isso no tiene ningún sistema automático de filtrado.
No quiero anticiparme a resolver un problema antes de que se manifieste, pero veremos cuánto dura la paz...

¿Llegaste a leer hasta aquí? ¡No puedes irte sin dejar un comentario!
