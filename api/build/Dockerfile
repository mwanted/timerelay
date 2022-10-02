FROM centos7-py36-bottle:v1

WORKDIR /app
ADD app.tar /app

EXPOSE 80/tcp
ENTRYPOINT ["/bin/sh", "/code/entry.sh"]
