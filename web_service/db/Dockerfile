# vi: ft=Dockerfile
FROM postgis/postgis:13-master@sha256:ce122525421548187febe53ef7f31a90429b129d3b1089348ed57e9296d1354c

COPY ./entrypoint_inject.sh ./healthcheck.sh /
COPY ./initdb/* /docker-entrypoint-initdb.d/

ENTRYPOINT ["/entrypoint_inject.sh"]

CMD             ["/usr/local/bin/docker-entrypoint.sh", "postgres"]
HEALTHCHECK CMD ["/entrypoint-inject.sh", "/healthcheck.sh"]
