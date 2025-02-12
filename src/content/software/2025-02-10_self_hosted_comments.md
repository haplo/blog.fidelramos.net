Title: Now with self-hosted comments
Date: 2025-02-10
Lang: en
Category: Software
Tags: blog,free-software,howto,linux,privacy,self-hosting
Slug: self-hosted-comments

A few days ago I received an email from a reader and [fellow blogger](https://zenodotus280.mataroa.blog/), to let me know that he was following my blog and also gave me a shout out about [my New Year's resolution to write at least one article every month of 2025]({filename}../personal/2025-01-04_new_years_resolutions.md#blog), and that I was already running behind.

I love getting messages like that, because if one person takes the trouble to email me I'm sure there are 99 others who have thought about it but haven't done so.
That's why after receiving the email I decided to give priority to something I had been planning for a long time: adding comments to the blog.
Spoiler alert: **goal achieved**.

I wanted it to be something fast, so instead of looking for the perfect option I was going to optimize for the one that would take me the least time to implement.
That meant starting by trying out the options already built into the [Reflex](https://github.com/haplo/reflex) theme I use on the blog (fork of [Flex](https://github.com/alexandrevicenzi/Flex)):

- [Disqus](https://disqus.com/): probably the most popular commenting platform on the web.
It is very convenient and powerful, but totally closed and most likely spies and sells our data.
- [Isso](https://isso-comments.de/): self-hosted Disqus-style software.

Those who know me will think that I would have jumped head first for Isso, but honestly my first attempt was with Disqus, because it would have been the quickest thing to do: open an account, put a password in the Pelican options and go.
Well, my plan quickly run into a wall because it turns out that [Disqus no longer has a free plan](https://disqus.com/pricing/)!
I don't mind paying for worthwhile services, but not for comments on this humble blog, so I forgot about Disqus and started looking at the details of Isso.

I liked what I saw about Isso:

- Self-hosted on my own domain.
- Programmed in Python: easy installation in a virtualenv and it would be particularly easy for me to collaborate with the project if needed.
- SQLite as database, no need for a MariaDB or Postgres server.
This was one of the main reasons why [I chose Shynet for blog analytics]({filename}2022-05-27_privacy_respecting_self_hosted_web_analytics.md).

The only thing I didn't like about Isso is that development seems a bit stalled, there are several PRs that have been waiting for months for merge.
But it doesn't seem to be a dead project, I'm hopeful that there will continue to be new versions at least to keep it up to date in terms of compatibility and security.

By the way, I ended up discovering [Remark42](https://github.com/umputun/remark42/) as an alternative, after having deployed Isso on my server.
It looks very good both in terms of features and development status, but personally I would have continued to choose Isso because it is already integrated into my blog theme.

## Technical details

I installed Isso on the same server that hosts this blog, a humble VPS with 2 GB of RAM.
I didn't need but to follow the [official documentation](https://isso-comments.de/docs/reference/installation/#init-scripts), but in case anyone is interested this was my process:

1. Install *isso* and a WSGI server (I favor gunicorn):

        :::shell
        # create new user for isolation
        adduser --disabled-password isso
        
        # install isso
        su - isso
        virtualenv venv
        source venv/bin/activate
        pip install isso gunicorn   

1. Create server configuration file in */home/isso/isso.cfg*:

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
    
3. Set up reverse proxy through Caddy by adding to */etc/caddy/Caddyfile*:

        :::text
        isso.fidelramos.net {
            reverse_proxy localhost:8081
            encode zstd gzip
        }    

4. Add a systemd service unit at */etc/systemd/system/isso.service* to run isso. [Isso documentation includes other init systems](https://isso-comments.de/docs/reference/installation/#init-scripts).

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

5. Add A and/or AAAA records to your DNS (*isso.fidelramos.net* in my case) pointing to the server.

6. Enable and start *isso*, and reload *caddy*:

        :::shell
        systemctl enable isso
        systemctl start isso
        systemctl reload caddy    

7. Now I can access [isso.fidelramos.net/admin](https://isso.fidelramos.net/admin).

8. Add configuration to *pelicanconf.py*:

        :::python
        ISSO_URL = "//isso.fidelramos.net"
        ISSO_OPTIONS = {
            "vote": "false",
        }    

9. Deploy the blog. Comments are live! 🎉

## The future

I'm looking forward to seeing how much use the comments will get.
I'm sure they will encourage me to write more.

Spam worries me, because Isso has no automatic filtering system.
I don't want to anticipate solving a problem before it manifests itself, but we'll see how long the peace lasts....

Did you make it this far? You can't leave without leaving a comment!
