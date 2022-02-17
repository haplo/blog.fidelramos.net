blog.fidelramos.net
===================

This is the full source code for my personal blog:
[blog.fidelramos.net](https://blog.fidelramos.net/).

It's built with [Pelican](http://getpelican.com/) using the [Flex
theme](https://github.com/alexandrevicenzi/Flex), which needs to be checked out
for the current settings to work.

Set up
======

``` shell
$ git clone https://github.com/haplo/blog.fidelramos.net.git
$ git clone https://github.com/alexandrevicenzi/Flex.git pelican-theme-Flex
$ git clone https://github.com/getpelican/pelican-plugins.git
$ cd blog.fidelramos.net
$ python3 -m venv virtualenv
$ . virtualenv/bin/activate
(virtualenv)$ pip install -r requirements.txt
```

Developing
==========

``` shell
$ . virtualenv/bin/activate
(virtualenv)$ cd src
(virtualenv)$ make devserver  # then navigate to http://localhost:8000
```

Deployment
==========

``` shell
$ . virtualenv/bin/activate
(virtualenv)$ cd src
make rsync_publish
```
