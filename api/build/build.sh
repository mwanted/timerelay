#!/usr/bin/env sh

tar -cvf app.tar -C ../app/ . --exclude-from=../../.gitignore

docker build -f Dockerfile -t mw/timarelayapi:master . 

rm -rf app.tar
