blog.fidelramos.net
===================

This is the full source code for my personal blog: [blog.fidelramos.net](https://blog.fidelramos.net/).

It's built with [Pelican](http://getpelican.com/) using [Reflex theme](https://github.com/haplo/reflex).

Set up
======

``` shell
git clone https://github.com/haplo/blog.fidelramos.net.git
git clone https://github.com/haplo/reflex.git pelican-theme-reflex
git clone https://github.com/getpelican/pelican-plugins.git
cd blog.fidelramos.net
python3 -m venv virtualenv
. virtualenv/bin/activate
pip install -r requirements.txt
```

Developing
==========

``` shell
. virtualenv/bin/activate
cd src
make devserver  # then navigate to http://localhost:8000
```

Deployment
==========

``` shell
./deploy.sh
```
