#!/bin/bash
FILE_DUMP_INDEXES=$HOME/backup_indexes.tar.gz

# create directory BACKUP_INDEXES to temporary put the files of the tar
BACKUP_INDEXES=$HOME/backup_indexes_$RANDOM

if [ ! -d "$BACKUP_INDEXES" ]; then
    mkdir -p "$BACKUP_INDEXES"
fi

# extract files
tar -xzf $FILE_DUMP_INDEXES -C $BACKUP_INDEXES

echo "Restoring indexes from backup ..."
# restore indexes
multielasticdump \
    --direction=load \
    --match='^.*$' \
    --input=$BACKUP_INDEXES \
    --output=http://127.0.0.1:9200 \
    --quiet=true \
    --debug=false

# restore aliases
for alias in $BACKUP_INDEXES/*.alias.json; do
    elasticdump \
    --input=$alias \
    --output=http://127.0.0.1:9200 \
    --type=alias \
    --quiet=true \
    --debug=false
done
echo "Indexes have been restored"

# remove directory BACKUP_INDEXES
rm -r $BACKUP_INDEXES