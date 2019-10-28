blog.fidelramos.net
===================

This is the full source code for my personal blog:
[blog.fidelramos.net](https://blog.fidelramos.net/).

It's built with [Pelican](http://getpelican.com/) using the [Flex
theme](https://github.com/alexandrevicenzi/Flex). I have been making
changes to Flex to cover my needs, until my PRs are accepted upstream
this blog needs [my fork of Flex](https://github.com/haplo/Flex).

Set up
======

``` shell
$ git clone https://github.com/haplo/blog.fidelramos.net.git
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
