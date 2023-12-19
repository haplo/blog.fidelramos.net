#!/bin/bash

# sanity check that we are in master branch, otherwise we might be pushing
# articles that are not finished yet!
if [[ $(git rev-parse --abbrev-ref HEAD) != "master" ]]; then
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    echo "!!! Not on master branch, aborting deployment !!!"
    echo "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
    exit 1
fi

cd src
make publish
rsync -av --delete output/ fidelramos.net:/home/fidel/www/blog.fidelramos.net
