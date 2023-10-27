# The database migration should be started from the master branch where v9 is installed.
# The db migration is done in a python 3.8 virtualenv.
# Once the db is migrate it can be restored in the python 3.9 virtualenv for v12 that
# is in the branch migration.

# IMPORTANT!!!: do not run the full script but proceed step by step, 
# there are still some operation that are 'manual', follow the comments
PATH_TO_BIGMAP_VENV="/home/vgranata/.virtualenvs/bm_archiverdm"
PATH_TO_BIGMAP_APP="/home/vgranata/app/archive-rdm/big-map-archive"
cd $PATH_TO_BIGMAP_APP

# move to master branch where v9 is installed
git checkout master

# copy migration scripts from branch migration
git checkout migration migration

############################
# Step 1: install version 9
# use Pipfile_v9.0.2.lock that is in branch migration
############################

# use Pipfile_v9.0.2 and Pipfile_v9.0.2.lock that are in branch migration:
cd $PATH_TO_BIGMAP_APP
cp migration/python3.8/Pipfile_v9.0.2 Pipfile
cp migration/python3.8/Pipfile_v9.0.2.lock Pipfile.lock

# recreate virtualenv v9
sudo rm -rf $PATH_TO_BIGMAP_VENV
python3.8 -m venv $PATH_TO_BIGMAP_VENV
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
cd $PATH_TO_BIGMAP_APP/backup
python restore_db_es.py

# assets build might not be needed to migrate, it can be skipped
cd $PATH_TO_BIGMAP_APP
invenio-cli assets build
# the application still gives errors, can skip at this stage "invenio-cli run":
# problem to load vocaulbalries and problem to see record
# AttributeError: 'UIJSONSerializer' object has no attribute 'serialize_object_to_dict'

############################
# Step 3: Upgrade to InvenioRDM v10
############################
invenio-cli packages update 10.0

# assets build might not be needed to migrate, it can be skipped
invenio-cli assets build

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
invenio-cli packages update 11.0

# Execute the database migration
invenio alembic upgrade
pipenv run invenio shell $(find $(pipenv --venv)/lib/*/site-packages/invenio_app_rdm -name migrate_10_0_to_11_0.py)

############################
# Step 5: Upgrade to InvenioRDM v12
############################
invenio-cli packages update 12.0.0b2.dev36
pipenv uninstall flask-babelex

# Re-build assets
# This gives problem, skip it:
# <venv>/var/instance/assets/templates/custom_fields doesn't exist
# assets build might not be needed to migrate, it can be skipped
# invenio-cli assets build

# Execute the database migration
# set depends_on = None:
# depends_on = "eb9743315a9d"  # invenio-accounts: add_userprofile
# depends_on = None
# in here:
# <venv>/lib/python3.8/site-packages/invenio_userprofiles/alembic/41157f1933d6_remove_table.py
invenio alembic upgrade

# this is to start the stats indexes it can be skipped for now
# it should be done once we install the migrated dump to v12 in the python 3.9 virtualenv
# invenio queues declare

# Not able to do update:
# invenio index update communities-communities-v1.0.0
# invenio index update rdmrecords-drafts-draft-v6.0.0
# invenio index update rdmrecords-records-record-v6.0.0

# Instead destroyed and recreated indexes:
invenio index destroy --force --yes-i-know
invenio index init
invenio rdm-records rebuild-index
invenio communities rebuild-index

# The migration file in the virtualenv did not work:
# pipenv run invenio shell $(find $(pipenv --venv)/lib/*/site-packages/invenio_app_rdm -name migrate_11_0_to_12_0.py)
# I had to make few changes, run this instead:
pipenv run invenio shell migration/migrate_11_0_to_12_0.py

# re-update the indexes after data migration
invenio index destroy --force --yes-i-know
invenio index init
invenio rdm-records rebuild-index
invenio communities rebuild-index

############################
# Step 6: Make a dump of the migrated database
############################
cd $PATH_TO_BIGMAP_APP

DOCKER_CONTAINER_ID=$(docker ps -aqf "name=big-map-archive-db-1")
FILE_DUMP="/var/lib/postgresql/data/big_map_archive_dump_migrated.bak"

echo "Dump of database started ..."
docker exec $DOCKER_CONTAINER_ID sh -c "pg_dump -U big-map-archive -F t big-map-archive  >  ${FILE_DUMP}"
echo "Dump of database completed"
docker cp $DOCKER_CONTAINER_ID:$FILE_DUMP .

############################
# END OF DATABASE MIGRATION
############################
echo "END OF DATABASE MIGRATION: the migrated db dump is big_map_archive_dump_migrated.bak"

############################
# Step 7: Go to branch migration where v12 is installed, use python 3.9
############################
git checkout migration
source .env
# this is needed to pass from elasticsearch to opensearch
invenio-cli services stop
invenio-cli services destroy

# recreate virtualenv v12
sudo rm -rf $PATH_TO_BIGMAP_VENV
python3.9 -m venv $PATH_TO_BIGMAP_VENV
cd $PATH_TO_BIGMAP_APP
workon bm_archiverdm
nvm use v14.18.1
pip install invenio-cli

# install packages in virtualenv
# Note: need to comment the blueprint in mc_archive_inveniordm views to install the packages
invenio-cli install

# recreate containers (including db)
invenio-cli services setup -f --no-demo-data

############################
# Step 8: restore the migrated database and indexes from db dump
############################
# copy last db dump to the docker container:
DOCKER_CONTAINER_ID=$(docker ps -aqf "name=big-map-archive-db-1")
docker cp big_map_archive_dump_migrated.bak $DOCKER_CONTAINER_ID:/var/lib/postgresql/data
# check filepath FILE_DUMP is correct in backup/restore_db.sh 

cd $PATH_TO_BIGMAP_APP/backup
python restore_db_es.py

# run the application
cd $PATH_TO_BIGMAP_APP
invenio-cli assets build
invenio-cli run 
