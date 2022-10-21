#!/bin/bash
# 1. Make dump of db
# 2. Copy dump on OS
# 3. Remove old dumps from OS
# WARNING: this file is in the crontab.
set +ev
# read user and database name from configuration file
IFS=" = "
while read var value
do
	if [ "$var" == "SQL_USER" ] || [ "$var" == "SQL_DB" ]
	then
    	export "$var"="$value"
	fi
done < ~/.virtualenvs/big-map-archive/var/instance/invenio.cfg

DOCKER_CONTAINER_ID=$(docker ps -aqf "name=big-map-archive_db_1")
FILE_DUMP="/var/lib/postgresql/data/big_map_archive_dump.bak"

echo "Dump of database started ..."
docker exec $DOCKER_CONTAINER_ID sh -c "pg_dump -U $SQL_USER -F t $SQL_DB  >  ${FILE_DUMP}"
echo "Dump of database completed"

~/.virtualenvs/big-map-archive/bin/python "$HOME"/big-map-archive/backup/copy_dump_to_os.py


