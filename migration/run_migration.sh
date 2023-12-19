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
workon bm_archiverdm
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
# Step 5: Upgrade to InvenioRDM v12
############################
# Move to the branch develop_v12
# You will need to remove the copied folders of migration and backup to 
# be able to change branch
git checkout develop_v12
nvm use v14.18.1

# Execute the database migration
# set depends_on = None:
# depends_on = "eb9743315a9d"  # invenio-accounts: add_userprofile
# depends_on = None
# in here:
# <venv>/lib/python3.9/site-packages/invenio_userprofiles/alembic/41157f1933d6_remove_table.py
invenio alembic upgrade

# delete all indexes
curl -X DELETE http://localhost:9200/*

############################
# Step 6: Make a dump of the migrated database v11
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
# Step 7: Destroy and restart services
############################
invenio-cli services stop
invenio-cli services destroy

# check every container is indeed removed, even docker.elastic.co
docker ps
# if docker.elastic.co are present remove them by hand
docker stop <container_id>
docker rm <container_id>

# rebuild the assets
nvm use v14.18.1
invenio-cli assets build

# setup the services
invenio-cli services setup -f --no-demo-data

############################
# Step 8: Restore database from v11
############################
# copy last db dump to the docker container:
DOCKER_CONTAINER_ID=$(docker ps -aqf "name=big-map-archive-db-1")
docker cp big_map_archive_dump_migrated_v11.bak $DOCKER_CONTAINER_ID:/var/lib/postgresql/data
# check filepath FILE_DUMP is correct in backup/restore_db.sh 

cd $PATH_TO_BIGMAP_APP/backup/v9
python restore_db_es.py

############################
# Step 9: Run migration script to v12 and recreate indexes
############################
# pipenv run invenio shell $(find $(pipenv --venv)/lib/*/site-packages/invenio_app_rdm -name migrate_11_0_to_12_0.py)
# I had to make few changes, run this instead:
pipenv run invenio shell migration/migrate_11_0_to_12_0.py

# re-update the indexes after data migration
# IMPORTANT: comment restore_db and update_files_location in file restore_db_es.py
cd $PATH_TO_BIGMAP_APP/backup/v9
python restore_db_es.py

# create statistics indexes
invenio queues declare

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

# create communities and attribute as owner INVENIO_DEFAULT_COMMUNITY_OWNER_MAIL
cd $PATH_TO_BIGMAP_APP
invenio bmarchive communities create battery2030
invenio bmarchive communities create bigmap
invenio bmarchive communities create instabat
invenio bmarchive communities create sensibat
invenio bmarchive communities create bat4ever
invenio bmarchive communities create spartacus
invenio bmarchive communities create hidden

# make all records/drafts and files restrictes,
# add bigmap community to all records/drafts, 
# add bigmap community to all users.
cd $PATH_TO_BIGMAP_APP/migration
python3 migrate_bigmap.py

# run the application
cd $PATH_TO_BIGMAP_APP
invenio-cli assets build
invenio-cli run 
