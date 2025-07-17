blog.fidelramos.net
===================

This is the full source code for my personal blog: [blog.fidelramos.net](https://blog.fidelramos.net/).

It's built with [Pelican](http://getpelican.com/) using [Reflex theme](https://github.com/haplo/reflex).

Set up
======

You need [uv](https://github.com/astral-sh/uv) installed.

``` shell
git clone https://github.com/haplo/blog.fidelramos.net.git
git clone https://github.com/haplo/reflex.git pelican-theme-reflex
cd blog.fidelramos.net
uv sync
```

Developing
==========

``` shell
cd src && make devserver  # then navigate to http://localhost:8000
```

Deployment
==========

``` shell
./deploy.sh
```
