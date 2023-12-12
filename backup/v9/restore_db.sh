#!/bin/bash
# $1 == DB_USER
# $2 == DB_NAME
# Change path in FILE_DUMP accordingly

DOCKER_CONTAINER_ID=$(docker ps -aqf "name=big-map-archive-db-1")
FILE_DUMP="/var/lib/postgresql/data/big_map_archive_dump.bak"
docker exec $DOCKER_CONTAINER_ID pg_restore -U $1 -d $2 $FILE_DUMP
