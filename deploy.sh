#!/bin/bash
cd src
make publish
rsync -av --delete output/ fidelramos.net:/home/fidel/www/blog.fidelramos.net
