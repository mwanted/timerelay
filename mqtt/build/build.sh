#!/usr/bin/env sh

tar -cvf app.tar -C ../app/ . --exclude-from=../../.gitignore

docker build -f Dockerfile -t mw/timarelaymqtt:master . 

rm -rf app.tar
