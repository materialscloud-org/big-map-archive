# The database migration should be started from the master branch where v9 is installed.
# The db migration is done in a python 3.8 virtualenv.
# Once the db is migrate it can be restored in the python 3.9 virtualenv for v12 that
# is in the branch migration.

# IMPORTANT!!!: do not run the full script but proceed step by step, 
# there are still some operations that are 'manual', follow the comments
PATH_TO_BIGMAP_VENV="/home/vgranata/.virtualenvs/bm_archiverdm_migration"
PATH_TO_BIGMAP_APP="/home/vgranata/app/archive-rdm/big-map-archive"
cd $PATH_TO_BIGMAP_APP

# move to master branch where v9 is installed
git checkout master

# copy migration and backup scripts from branch develop_v12
git checkout develop_v12 migration
git checkout develop_v12 backup
############################
# Step 1: install version 9
# use Pipfile_v9.0.2.lock that is in branch develop_v12
############################

# use Pipfile_v9.0.2 and Pipfile_v9.0.2.lock that are in branch develop_v12:
cd $PATH_TO_BIGMAP_APP
cp migration/python3.8/Pipfile_v9.0.2 Pipfile
cp migration/python3.8/Pipfile_v9.0.2.lock Pipfile.lock

# recreate virtualenv v9
sudo rm -rf $PATH_TO_BIGMAP_VENV
# python3.8 -m venv $PATH_TO_BIGMAP_VENV
mkvirtualenv -p /usr/bin/python3.8 bm_archiverdm_migration

cd $PATH_TO_BIGMAP_APP
workon bm_archiverdm_migration
nvm use v14.18.1
pip install invenio-cli

# install packages in virtualenv
invenio-cli install

# recreate containers (including db)
invenio-cli services setup -f --no-demo-data

############################
# Step 2: restore the database and indexes from db dump
############################
# Take the last db dump from production (folder dump of the CSCS container) and copy it locally.
# Copy dump to the docker container:
# DOCKER_CONTAINER_ID=$(docker ps -aqf "name=big-map-archive-db-1")
# docker cp ~/<dump_filename> $DOCKER_CONTAINER_ID:/var/lib/postgresql/data
# check filepath FILE_DUMP is correct in backup/restore_db.sh 
source .env
cd $PATH_TO_BIGMAP_APP/backup/v9
python restore_db_es.py

# assets build might not be needed to migrate, it can be skipped
# cd $PATH_TO_BIGMAP_APP
# invenio-cli assets build
# the application still gives errors, can skip at this stage "invenio-cli run":
# problem to load vocaulbalries and problem to see record
# AttributeError: 'UIJSONSerializer' object has no attribute 'serialize_object_to_dict'

############################
# Step 3: Upgrade to InvenioRDM v10
############################
cd $PATH_TO_BIGMAP_APP
invenio-cli packages update 10.0

# assets build might not be needed to migrate, it can be skipped
# invenio-cli assets build

# Execute the database migration
# set depends_on = None:
# depends_on = "eb9743315a9d"  # invenio-accounts: add_userprofile
# depends_on = None
# in here:
# <venv>/lib/python3.8/site-packages/invenio_userprofiles/alembic/41157f1933d6_remove_table.py
invenio alembic upgrade
pipenv run invenio shell $(find $(pipenv --venv)/lib/*/site-packages/invenio_app_rdm -name migrate_9_0_to_10_0.py)

############################
# Step 4: Upgrade to InvenioRDM v11
############################
cd $PATH_TO_BIGMAP_APP
invenio-cli packages update 11.0

# Execute the database migration
invenio alembic upgrade
pipenv run invenio shell $(find $(pipenv --venv)/lib/*/site-packages/invenio_app_rdm -name migrate_10_0_to_11_0.py)

############################
# Step 4.1: Make a dump of the migrated database v11
############################
cd $PATH_TO_BIGMAP_APP

DOCKER_CONTAINER_ID=$(docker ps -aqf "name=big-map-archive-db-1")
FILE_DUMP="/var/lib/postgresql/data/big_map_archive_dump_migrated_v11.bak"

# Make dump of database
echo "Dump of database started ..."
docker exec $DOCKER_CONTAINER_ID sh -c "pg_dump -U big-map-archive -F t big-map-archive  >  ${FILE_DUMP}"
echo "Dump of database completed"
docker cp $DOCKER_CONTAINER_ID:$FILE_DUMP .

############################
# Step 5: Upgrade to InvenioRDM v12
############################
# Move to the branch develop_v12
# You will need to remove the copied folders of migration and backup to 
# be able to change branch
# IMPOTANT change to the virtualenv for v12!!!
git checkout develop_v12
workon bm_archiverdm
nvm use v14.18.1

############################
# Step 7: Destroy and restart services
############################
# delete all indexes
curl -X DELETE http://localhost:9200/*

invenio-cli services stop
invenio-cli services destroy

# check every container is indeed removed, even docker.elastic.co
docker ps
# if docker.elastic.co are present remove them by hand
docker stop <container_id>
docker rm <container_id>

source .env
# setup the services
invenio-cli services setup -f --no-demo-data
# Execute the database migration
# set depends_on = None:
# depends_on = "eb9743315a9d"  # invenio-accounts: add_userprofile
# depends_on = None
# in here:
# <venv>/lib/python3.9/site-packages/invenio_userprofiles/alembic/41157f1933d6_remove_table.py
invenio alembic upgrade # this should do nothing, it is just for a check
############################
# Step 8: Restore database from v11
############################
# copy last db dump to the docker container:
DOCKER_CONTAINER_ID=$(docker ps -aqf "name=big-map-archive-db-1")
docker cp big_map_archive_dump_migrated_v11.bak $DOCKER_CONTAINER_ID:/var/lib/postgresql/data
# IMPOTANT !!!! check filepath FILE_DUMP is correct in backup/restore_db.sh 
# comment restore_es in backup/v9/restore_db_es.py
cd $PATH_TO_BIGMAP_APP/backup/v9
python restore_db_es.py

invenio alembic upgrade # this should update the db
############################
# Step 9: Run migration script to v12 and recreate indexes
############################
# pipenv run invenio shell $(find $(pipenv --venv)/lib/*/site-packages/invenio_app_rdm -name migrate_11_0_to_12_0.py)
# I had to make few changes, run this instead:
cd $PATH_TO_BIGMAP_APP
pipenv run invenio shell migration/migrate_11_0_to_12_0.py

# create statistics indexes
invenio queues declare

# create the communities by running the app to read in app_data
rm celerybeat-schedule.db
invenio-cli run
############################
# Step 10: create communities owner and communities,
# and run migrate.py to: 
# - make all records/drafts and files restrictes
# - add bigmap community to all records/drafts
# - add bigmap community to all users
############################
cd $PATH_TO_BIGMAP_APP

# read default owner of communities 
# IFS=" = "
# while read var value
# do
# 	if [ "$var" == "INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL" ]
# 	then
#     	export "$var"="$value"
# 	fi
# done < ~/app/archive-rdm/big-map-archive/.env

source ~/app/archive-rdm/big-map-archive/.env

# create owner (not active) of communities 
invenio users create $INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL --password=$INVENIO_DEFAULT_COMMUNITY_OWNER_PASSWORD

# Attribute owner INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL to communities,
# the communities are already created beacuse of the file communities.yaml in app_data
cd $PATH_TO_BIGMAP_APP
invenio bmarchive users add_community battery2030 owner $INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL
invenio bmarchive users add_community bigmap owner $INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL
invenio bmarchive users add_community bat4ever owner $INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL
invenio bmarchive users add_community hidden owner $INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL
invenio bmarchive users add_community spartacus owner $INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL
invenio bmarchive users add_community sensibat owner $INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL
invenio bmarchive users add_community instabat owner $INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL
invenio bmarchive users add_community healingbat owner $INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL
invenio bmarchive users add_community opera owner $INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL
invenio bmarchive users add_community opincharge owner $INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL
invenio bmarchive users add_community phoenix owner $INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL
invenio bmarchive users add_community salamander owner $INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL
invenio bmarchive users add_community ultrabat owner $INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL

# make all records/drafts and files restrictes,
# add bigmap community to all records/drafts, 
# add bigmap community to all users.
cd $PATH_TO_BIGMAP_APP/migration
python3 migrate_bigmap.py

# run the application
cd $PATH_TO_BIGMAP_APP
# stop the running invenio-cli
nvm use v14.18.1
invenio-cli assets build
invenio-cli run 

############################
# Step 11: Make a backup of the migrated database v12
############################
cd $PATH_TO_BIGMAP_APP/backup
# !!!IMPORTANT comment the last 2 lines of backup.sh (the copy to the OS)
. backup.sh
# the backup of the indexes is called backup_indexes.tar.gz and is in the home directory
# copy the db dump from the container
docker cp $DOCKER_CONTAINER_ID:var/lib/postgresql/data/big_map_archive_dump.bak .

############################
# Step 12: Restore the backup on the production machine
############################
# copy backup_indexes.tar.gz in the home directory of the production machine
# copy the db dump in the container of the production machine
docker cp big_map_archive_dump.bak $DOCKER_CONTAINER_ID:/var/lib/postgresql/data/
cd $PATH_TO_BIGMAP_APP/backup
python3 restore_backup.py


############################
# NOTE on INDEXES
# it is enought to restore only the database and then recreate the indexes
# because in v9 the usage statistics was not tracked.
# After having installed the latest db follow the procedure below to
# restore all indexes.
############################
# The indexing process takes time, once you run these commands you need to wait several minutes
# check the progress via 
curl -X GET http://127.0.0.1:9200/_cat/indices?s=index:desc

# recreate indices
invenio index destroy --yes-i-know
invenio index init

# reindex records
invenio rdm-records rebuild-index
invenio communities rebuild-index

# reindex all other indexes in invenio shell
$ invenio shell

from invenio_access.permissions import system_identity
from invenio_communities.proxies import current_communities
from invenio_records_resources.proxies import current_service_registry
from invenio_requests.proxies import current_events_service, current_requests_service

# reindex users
users_service = current_service_registry.get("users")
users_service.rebuild_index(system_identity)

# reindex groups
groups_service = current_service_registry.get("groups")
groups_service.rebuild_index(system_identity)

# reindex members and archived invitations
members_service = current_communities.service.members
members_service.rebuild_index(system_identity)

# reindex requests
for req_meta in current_requests_service.record_cls.model_cls.query.all():
    request = current_requests_service.record_cls(req_meta.data, model=req_meta)
    if not request.is_deleted:
        current_requests_service.indexer.index(request)

# reindex requests events
for event_meta in current_events_service.record_cls.model_cls.query.all():
    event = current_events_service.record_cls(event_meta.data, model=event_meta)
    current_events_service.indexer.index(event)