from pymongo.errors import ServerSelectionTimeoutError
from logzero import logger
from reporitory.FullBackupRepository import FullBackupRepository
from models.catalog.FullBackupCatalog import FullBackupCatalog
from models.catalog.ItemCatalog import ItemCatalog
from models.catalog.FileState import FileState
from datetime import date
from models.catalog.Status import Status
from  reporitory.EntityRepository import EntityRepository


try:
    repository_full_backup=FullBackupRepository("backup_webdav")
    repository_entity=EntityRepository("backup_webdav")
    s2=repository_entity.findOne("MDC")
    s1=repository_entity.findOne("chenal.org")
    file_1=ItemCatalog(path="/home/myuser/plan.txt",
                   hash_file="12dfeaa234567af",
                   type='file',
                   file_state=FileState.ADDED,
                   file_size=12654
    )

    file_2=ItemCatalog(path="/home/myuser/Image/plan.jpg",
                   hash_file="22dfaaa234567ac",
                   type='file',
                   file_state=FileState.ADDED,
                   file_size=12654
    )


    one_backup=repository_full_backup.findOne("222-3333-4444-4444")
    full_backup_catalogs=repository_full_backup.findAll()
    print(full_backup_catalogs)
    fullback_1=FullBackupCatalog(host="www.example.com",
                             source_type="WEBDAV",
                             entity=s2,
                             root="MyExample",
                             backup_id="3333-2222-333-4444",
                             zip_size=0,
                             zip_path="/opt/backup/store/MyExample/333-2222-333-444-20220119.zip",
                             hash_zip="NULL",
                             start_at=date(2023,1,19).ctime(),
                             end_at=date(2023,1,19).ctime(),
                             expiration_time=date(2023,1,26).ctime(),
                             files=[],
                             status=Status.EXPIRED
                            )

    repository_full_backup.delete_by_status(Status.EXPIRED,s1)

except ServerSelectionTimeoutError:
    logger.error("MMMMongoDb not reachable")
except TypeError as e:
    logger.error("type error : %s :",str(e))
except Exception  as e:
    print(e)
    logger.error("Unknown exception occurs")
finally:
    logger.debug("We close all mongodb connection if any")
    repository_full_backup.close_mongo_connect(alias="default")
