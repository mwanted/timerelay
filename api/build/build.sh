#!/usr/bin/env sh

git pull

tar -cvf app.tar -C app/ . --exclude-from=.gitignore

docker build -f build/Dockerfile -t mw/timarelayapi:master . 

rm -rf app.tar