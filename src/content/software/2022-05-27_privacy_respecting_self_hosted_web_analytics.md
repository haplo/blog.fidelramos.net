Title: Privacy-respecting self-hosted Web Analytics
Date: 2022-05-27
Lang: en
Category: Software
Tags: privacy,web,analytics,self-hosting
Slug: privacy-respecting-self-hosted-web-analytics

It all started with a desire: I wanted some basic analytics for this blog to know how it's
doing, which articles are popular and which are the main referrers. But therein lied the
conundrum: I am a privacy zealot, very much against extensive online tracking (just look
at the [browser extensions I use]({filename}2022-02-23_web_browser_addons.md)), so using a
third-party service that collected all my visitors' data was against the question.

I knew there were open-source web analytics projects out there, like Piwik which has been
around for a long time, but never had the time or need to look into them seriously. Until
now.

Please note that this article is by no means an extensive list. There are a lot of other
options out there, just check out [this big
list](https://github.com/newTendermint/awesome-analytics). Each software has its own pros
and cons, but I hope this article can help you choose and make the jump towards
self-hosted analytics, or at least to abandon Google Analytics in favor of an
open-source-based SAAS option.

[TOC]

# My requirements

I researched options for my specific use case:

1. Must be free software (*free as in freedom, not as in free beer*) and self-hosted.

2. Simple deployment, the fewer moving parts the better. SQLite if possible so no DB
  server will be needed. No Redis/Memcached if it can be avoided. Option to deploy without
  Docker would be nice.

3. Reasonable resource usage. My sites don't usually get a lot of traffic, so I would like
  to reuse the 2 GB VPS that hosts this blog.

4. Technology that I can easily hack is a plus. I will favor Python projects, but YMMV.

5. Lightweight and not too intrusive. I basically just want to know which articles are
   seen when, plus referrers, no need for advanced analytics.

6. Actively maintained.

# Matomo (formerly Piwik)

[Home page](https://matomo.org/)

1. GPLv3. Paid SAAS cloud service with free [self-hosting option](https://matomo.org/matomo-on-premise/).

2. [Installation docs](https://matomo.org/faq/on-premise/installing-matomo/).
    - Requires a webserver (Apache, Nginx, etc.)
    - Requires MySQL.
    - Configuration of Matomo is all done in-app.

3. [Matomo self-hosted requirements](https://matomo.org/faq/on-premise/matomo-requirements/):
    - <100k page views/month: 1 server for both app and DB. 2 CPU, 2 GB RAM, 50GB SSD disk.
    - ~1M page views/month: 1 server for both app and DB. 4 CPU, 8 GB RAM, 250GB SSD disk.
    - ~10M page views/month: 2 servers for app and DB. 8 CPUs, 16 GB RAM, 400GB SSD disk
    - ~100M page views/month: 3 or more servers for app, DB and load balancer. 16 CPUs,
      32 GB RAM, 1 TB SSD disk.

4. PHP for backend. VueJS and TypeScript for frontend. [Github
   repository](https://github.com/matomo-org/matomo) and [developer
   guide](https://developer.matomo.org/guides/contributing-to-piwik-core).

5. Very comprehensive set of [collected
   analytics](https://matomo.org/feature-overview/). [Wordpress
   plugin](https://matomo.org/installing-matomo-for-wordpress/) available.

6. About 10 commits per week, multiple [contributors](https://matomo.org/team/).

# Plausible

[Home page](https://plausible.io/open-source-website-analytics)

1. AGPLv3. Paid SAAS cloud service with free [self-hosting
   option](https://plausible.io/self-hosted-web-analytics), but the latter lags behind in
   features (2 releases per year).

2. [Official installation
   documentation](https://plausible.io/docs/self-hosting#up-and-running). tldr; needs
   *docker-compose*, PostgreSQL and Clickhouse.

3. From [Plausible's requirements documentation](https://plausible.io/docs/self-hosting#requirements):

    > The server must have a CPU with x86_64 architecture and support for SSE 4.2
    > instructions. We recommend using a minimum of 4GB of RAM but the requirements will
    > depend on your site traffic.

4. Elixir/Phoenix backend. React and Tailwind frontend. [Github
   repository](https://github.com/plausible/analytics) and [developer
   guide](https://github.com/plausible/analytics/blob/master/CONTRIBUTING.md).

5. <1 KiB tracking script. No cookies. I couldn't find a concrete list of tracked metrics,
   but it seems less extensive than Matomo or OWA.

6. Weekly activity, usually condensed in long-form pull requests.

# Shynet

[Home page](https://github.com/milesmcc/shynet)

1. Apache License Version 2.0. Self-hosted only.

2. Easy deployment with Docker or *docker-compose*, otherwise undocumented manual
   deployment. Supports any DB that Django supports, including SQLite. Cache server
   optional.

3. Low resource consumption, basically just a Python process running Django, ~100 MiB of
   RAM when using SQLite.

4. Python/Django backend. Uses its own [TailwindCSS
   plugin](https://github.com/milesmcc/a17t) for frontend. Easy to build from source
   (Docker image). [Github repository](https://github.com/milesmcc/shynet) and [developer
   guide](https://github.com/milesmcc/shynet/blob/master/CONTRIBUTING.md)

5. <1 KiB tracking script. No cookies. 1x1 pixel tracking fallback. Well-defined list of
   [captured metrics](https://github.com/milesmcc/shynet#metrics), pretty basic.

6. Not a lot of new feature development, but dependencies are kept up to date and the main
   developer is very responsive to issues and pull requests (see conclusions).

# Open Web Analytics (OWA)

[Home page](https://www.openwebanalytics.com/)

1. GPLv2. Self-hosted only.

2. From [OWA's installation
   documentation](https://github.com/Open-Web-Analytics/Open-Web-Analytics/wiki/Installation)
   and [technical
   requirements](https://github.com/Open-Web-Analytics/Open-Web-Analytics/wiki/Technical-Requirements):
    - Only PHP projects supported.
    - In-app install wizard.
    - [Only Apache 2.x officially
      supported](https://github.com/Open-Web-Analytics/Open-Web-Analytics/wiki/Technical-Requirements#web-server). Nginx
      works but needs manual configuration.
    - [MySQL *with strict mode
      off*](https://github.com/Open-Web-Analytics/Open-Web-Analytics/wiki/Technical-Requirements#databases=).

3. Unclear as to the exact requirements.

4. PHP backend. Webpack for frontend assets. Multiple repositories: [base
   repo](https://github.com/Open-Web-Analytics/Open-Web-Analytics/wiki/Installation),
   [Wordpress plugin repo](https://github.com/Open-Web-Analytics/owa-wordpress-plugin),
   [SDK for PHP repo](https://github.com/Open-Web-Analytics/owa-php-sdk).

5. Very detailed tracking, including heatmaps and "*Domstream session recordings*", but
   only for PHP apps. Dedicated [integration
   plugins](https://github.com/Open-Web-Analytics/Open-Web-Analytics/wiki/Integration-Plugins)
   for WordPress and MediaWiki.

6. Actively maintained, but apparently by a single developer.

# Conclusions and my winner

Looking at the highlighted requirements my choice for this humble blog was easy: Shynet
won hands down, it checked every box. For bigger sites Plausible and Matomo both seem to
be good options. I would say Plausible has a better foundational technology (it launched
in 2019 after all) but Matomo has been around for longer (2007), it's more battle-tested
and seems to collect more data. Plausible has [a comparison page between Plausible and
Matomo](https://plausible.io/vs-matomo). OWA might be a good option for PHP and Wordpress
sites.

Shynet's hackability, point 4 in my requirements list, quickly came into the spotlight
because [SQLite support was
broken](https://github.com/milesmcc/shynet/issues/208). Fortunately [I was able to fix
it](https://github.com/milesmcc/shynet/pull/210) and deploy it into the very server where
you have been reading this article. This is why I love free software.

Another issue with the deployment was that the server didn't have Docker installed and I
wanted to keep it that way, so I used the opportunity to learn about
[Podman](https://podman.io/). I instantly fell in love with it and its ability to run
rootless containers, which is a boon to security. Only issue I encountered was having to
change the permissions of the mounted data volume, otherwise Shynet's Django process was
unable to write the SQLite DB as files were owned by *root* inside the container. [This
article](https://www.tutorialworks.com/podman-rootless-volumes/) explains it well, tldr;
need to use `podman unshare`.

To end this article, here is a screenshot of Shynet's data for this blog (isn't it great
to be able to share knowing that nobody's privacy is at stake?):

[
![blog.fidelramos.net on my Shynet instance]({static}/images/privacy_respecting_self_hosted_web_analytics/shynet.png "Click to see full size"){: .align-center}
]({static}/images/privacy_respecting_self_hosted_web_analytics/shynet.png" "Click to see full size")
