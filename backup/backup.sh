#!/bin/bash
# 1. Make dump of db
# 2. Copy dump on OS
# 3. Remove old dumps from OS
# WARNING: this file is in the crontab.
set +ev

##############
# Dump db
##############
# read user and database name from configuration file
IFS=" = "
while read var value
do
	if [ "$var" == "INVENIO_SQL_USER" ] || [ "$var" == "INVENIO_SQL_DB" ]
	then
    	export "$var"="$value"
	fi
done < ~/big-map-archive/.env

DOCKER_CONTAINER_ID=$(docker ps -aqf "name=big-map-archive-db-1")
FILE_DUMP="/var/lib/postgresql/data/big_map_archive_dump.bak"

echo "Dump of database started ..."
docker exec $DOCKER_CONTAINER_ID sh -c "pg_dump -U $INVENIO_SQL_USER -F t $INVENIO_SQL_DB  >  ${FILE_DUMP}"
echo "Dump of database completed"

##############
# Backup indexes
##############
# create directory BACKUP_INDEXES to temporary put the files
BACKUP_INDEXES="$HOME/backup_indexes_$RANDOM"

if [ ! -d "$BACKUP_INDEXES" ]; then
    mkdir -p "$BACKUP_INDEXES"
fi

# backup OpenSearch indices & all their types
echo "Backup of indexes started ..."
multielasticdump \
  --direction=dump \
  --match='^.*$' \
  --input=http://127.0.0.1:9200 \
  --includeType=data,mapping,analyzer,alias,settings,template \
  --output=$BACKUP_INDEXES \
  --quiet=true \
  --debug=false
echo "Backup of indexes completed"

tar -zcf $HOME/backup_indexes.tar.gz -C $BACKUP_INDEXES .
chmod 700 $HOME/backup_indexes.tar.gz
echo "Made tarball $HOME/backup_indexes.tar.gz of backup files"

rm -r $BACKUP_INDEXES

##############
# Copy dump db and backup indexes to Object Store
##############
echo "Copy db dump and backup of indexes to Object Store"
~/.virtualenvs/big-map-archive/bin/python "$HOME"/big-map-archive/backup/copy_backup_to_os.py