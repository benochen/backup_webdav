import logzero
from typing import Optional
import os
import time
from datetime import datetime
import typer
import pathlib
import configparser

from pymongo.errors import ServerSelectionTimeoutError

from models.catalog.FullBackupCatalog import FullBackupCatalog
from models.catalog.Status import Status
from reporitory.EntityRepository import EntityRepository
from reporitory.FullBackupRepository import FullBackupRepository
from  tools.StorageCapacity import StorageCapacity
from tools.StorageCleaner import StorageCleaner
from workers.WebdavWorker import WebDavWorker
from tools.stat import Stat
from logger.MyloggerJson import JSONLogger
from webdav3.exceptions import WebDavException
from logzero import logger, logfile
from ErrorCode.ErrorCode import StatusCodes
from mongoengine import *

app = typer.Typer()


@app.command()
def hello(name: Optional[str] = None):
    if name:
        typer.echo(f"Hello {name}")
    else:
        typer.echo("Hello World!")


@app.command()
def bye(name: Optional[str] = None):
    if name:
        typer.echo(f"Bye {name}")
    else:
        typer.echo("Goodbye!")


def copy(client,root,update,dest):
    folders=client.list(root,get_info=True)
    print(folders)
    for file in folders:
        if file["isdir"]:
            length=len(file["path"].split("/"))
            endPath=file["path"].split("/")[length-2]
            print("endPath="+endPath)
            newRoot=root+"/"+endPath
            print("new root="+newRoot)
            if(  root.split("/")[len(root.split("/"))-1] != endPath):
                update= copy(client,newRoot,update,dest)
        else:
            destinationFolder=dest+os.path.sep+root.replace("/",os.path.sep)
            completeDestinationPath=destinationFolder+os.path.sep+os.path.basename(file["path"])
            os.makedirs(destinationFolder, exist_ok=True)
            remotePath=pathlib.Path(file["path"])
            remotePathStr= str(remotePath.relative_to(*remotePath.parts[:5]).as_posix())
            print("file "+remotePathStr+" will be copied in "+completeDestinationPath)
            try:
                if( not os.path.isfile(completeDestinationPath)):
                    client.download_sync(remote_path=remotePathStr, local_path=completeDestinationPath)

                else:
                 update["number"] = update["number"] + 1
                if file["size"]:
                    update["size"] = update["size"] + int(file["size"])
            except WebDavException as exception:
                with open('errors.log', 'w') as f:
                    f.write(remotePathStr)
                    f.close()
            except KeyError as exception:
                with open('key_errors.log', 'w') as f:
                    f.write(remotePathStr)
                    f.close()


    return update


def loadconfig(config_file:str):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config



@app.command()
def backup_catalog(root: Optional[str] = None, entity: Optional[str]="default",noclean: Optional[bool]=False,nozip: Optional[bool]=False,nocopy:Optional[bool]=False):
    try:
        conn = connect('backup_webdav')
        entity_repository=EntityRepository('backup_webdav')
        repository_full_backup = FullBackupRepository("backup_webdav")
        entity_mongo=entity_repository.findOne(entity)
        backup_id = repository_full_backup.generateUUID(entity_mongo)
        zip_name=backup_id+".zip"
        start_time_global=datetime.now()
        stat=Stat()
        config=loadconfig("config.ini")
        print(config)
        retention_day = config["BACKUP"]['retention_days']
        store_root_folder = config["BACKUP"]['store']
        destination_backup=config["BACKUP"]['destination']
        print(config["LOGGER"]["logfile"])
        mylogger=JSONLogger(config["LOGGER"]["logfile"],config["WEBDAV"]["username"],entity)
        retention_day = config["BACKUP"]['retention_days']

        store = os.path.join(store_root_folder, entity)
        zip_full_path = os.path.join(store, zip_name)
        files=list()
        fullback_1 = FullBackupCatalog(host=config["WEBDAV"]["url"],
                                       source_type="WEBDAV",
                                       entity=entity_mongo,
                                       root=root,
                                       backup_id=backup_id,
                                       zip_size=0,
                                       zip_path=zip_full_path,
                                       hash_zip="NULL",
                                       start_at=start_time_global,
                                       end_at=start_time_global,
                                       expiration_time=start_time_global,
                                       files=files,
                                       status=Status.IN_PROGRESS)

        repository_full_backup.insert(fullback_1)

        client = WebDavWorker(config,repository_full_backup)

        mylogger.info("Connection to Webdav succeed ")
        mylogger.info("Connection to %s succeed with username=%s",config["WEBDAV"]['url'],config["WEBDAV"]["username"])
        mylogger.info("Start backup of %s to %s", root,destination_backup)
        capacity = client.computeDiskSize(destination_backup)
        mylogger.info("The computed capacity is %s",capacity)
        if not nocopy:
            mylogger.info("Remote copy will be performed as nocopy flag is set to False")
            stat,files = client.completeBackupCatalog(stat,root,destination_backup,files)
            end_time=datetime.now()
            fullback_1 = FullBackupCatalog(host=config["WEBDAV"]["url"],
                                           source_type="WEBDAV",
                                           entity=entity_mongo,
                                           root=root,
                                           backup_id=backup_id,
                                           zip_size=0,
                                           zip_path=zip_full_path,
                                           hash_zip="NULL",
                                           start_at=start_time_global,
                                           end_at=end_time,
                                           expiration_time=end_time,
                                           files=files,
                                           status=Status.IN_PROGRESS_REMOTE_FILE_COPIED
                                           )
            repository_full_backup.insert(fullback_1)
        else:
            mylogger.info("Remote Copy has not been performed as nocopy flag is set to True")

        mylogger.debug("root=%s", root)
        to_zip = destination_backup+os.path.sep+root
        mylogger.debug("to_zip=%s", destination_backup)
        mylogger.info("Backup  %s complete", root)
#        mylogger.info("Copy of remote file completed in %s seconds ", str(float(time.time()) - float(start_time_global)))
        logger.info("Check there is enough space to zip folder %s", to_zip)
        if os.name == "posix":
            storage_capacity = StorageCapacity("/", to_zip, 0.10)
        else:
            mylogger.debug("Current path of dest is %s", zip_full_path)
            driveletter, path = os.path.splitdrive(zip_full_path)

            mylogger.debug("The computed driveletter is is %s", driveletter)
            storage_capacity = StorageCapacity(driveletter, to_zip, 0.10)
            storage_capacity.displayZizeInGb()
        dest_webdav_copy =  destination_backup
        if (not storage_capacity.canFileBeingZipped()):
            storage_capacity.displayZizeInGb()
            exit()
            mylogger.error("The storage %s does not contain enough space",555,store_root_folder)
            mylogger.info("Trying to remove oldest backup")
            cleaner = StorageCleaner(store, 3)
            mylogger.debug("We will clean %s ", store)
            if cleaner.removeOldestFile() == False:
                mylogger.error("Error when attempt to remove older file in %s", store)
            else:
                mylogger.info("Successfully remove oldest zip file in %s", store)
            mylogger.info("Check if there is enough space to zip")
            if not storage_capacity.canFileBeingZipped():
                mylogger.info("Still not enough space to zip %s to %s", dest_webdav_copy, store)
                exit();
        mylogger.info("Storage root contains enough space ")
        mylogger.info("Create zip from %s to %s ", dest_webdav_copy, root)
        start_time = time.time()
        if not nozip:
            mylogger.info("folder %s will be zipped as nozip flag is set to True", dest_webdav_copy+os.path.sep+root)
            stat,archive_path = client.zip_catalog( dest_webdav_copy+os.path.sep+os.path.sep+root, root, stat)
            mylogger.info("size=%s Go", str(int(stat.getFileSize() / (1024 * 1024 * 1024))))
            mylogger.info("number of files=%s", str(stat.getFileCopied()))
            mylogger.info("Creation of zip Operation competed in %s seconds ", (time.time() - start_time))
            mylogger.info("In the store %s search for file older than %s days", store, retention_day)
            fullback_1.setStatus(Status.ACTIVE.value)
            repository_full_backup.insert(fullback_1)

        else:
            mylogger.info("The folder %s will not be zipped as nozip flag is set to True", dest_webdav_copy)
            fullback_1.setStatus(Status.COMPLETED_NO_ZIP.value)
            repository_full_backup.insert(fullback_1)
        if noclean:
            mylogger.info("noclean flag enabled. %s will not be cleaned", store)
            exit()
        files_to_delete = list()

        cleaner = StorageCleaner(store, retention_day)
        files_to_delete = cleaner.search_by_age()
        mylogger.debug("files to delete;count=%s;list=%s", str(len(files_to_delete)), str(files_to_delete))
        cleaner.delete(files_to_delete)
        mylogger.info("Cleaning of %s succeed", str(files_to_delete))
        logger.info("Cleaning storage folder %s:", to_zip)
        cleaner.delete_directory(to_zip)
        mylogger.info("Cleaning of %s succeed", dest_webdav_copy)
  #      mylogger.info("The global backup process takes %s seconds", (time.time() - start_time_global))

    except PermissionError as e:
            mylogger.log("Error when cleaning file. Reason=%s", str(e),)

    except ServerSelectionTimeoutError as e:
            mylogger.error("Cannnot connect to mongoDB","",StatusCodes.SERVICE_UNAVAILABLE.value)




@app.command()
def backup(root: Optional[str] = None, entity: Optional[str]="default",noclean: Optional[bool]=False,nozip: Optional[bool]=False,nocopy:Optional[bool]=False):
    try:

        start_time_global=time.time()
        config = configparser.ConfigParser()
        config.read("config.ini")
        print("test")
        start_time = time.time()
        update = dict()
        dest = config["BACKUP"]['destination']
        update["size"] = 0
        update["number"] = 0
        logfile(config["LOGGER"]["logfile"])
        logger.debug("Enable client connection with the following config  url=%s,username=%s,password=********",
                     config["WEBDAV"]['url'], config["WEBDAV"]["username"])

        store_root_folder = config["BACKUP"]['store']
        store=os.path.join(store_root_folder,entity)


        client = WebDavWorker(config["WEBDAV"]['url'], config["WEBDAV"]['username'], config["WEBDAV"]['password'],
                              config["BACKUP"]['store'],entity)
        retention_day = config["BACKUP"]['retention_days']
        logger.info("Connection to %s succeed", config["WEBDAV"]['url'])
        logger.info("Start backup of %s to %s", root, dest)
        capacity = client.computeDiskSize(dest)
        if not nocopy:
            logger.info("Remote copy will be performed as nocopy flag is set to False")
            update = client.completeBackup(update, root, dest)
        else:
            logger.info("Remote Copy has not been performed as nocopy flag is set to True")
        logger.info("Completion of WebDav copy Operation competed in %s seconds ", (time.time() - start_time))

        logger.debug("root=%s",root)
        to_zip = dest + os.path.sep + root
        logger.debug("to_zip=%s",to_zip)
        logger.info("Backup  %s complete", root)
        logger.info("Copy of remote file completed in %s seconds ", (time.time() - start_time))
        logger.info("Check there is enough space to zip folder %s", to_zip)
        if os.name == "posix":
            storage_capacity = StorageCapacity("/", to_zip, 0.10)
        else:
            logger.debug("Current path of dest is %s",dest)
            driveletter,path=os.path.splitdrive(dest)
            logger.debug("The computed driveletter is is %s", driveletter)
            storage_capacity = StorageCapacity(driveletter,to_zip,0.10)
        dest_webdav_copy=dest + os.path.sep + root
        if (not storage_capacity.canFileBeingZipped()):
            storage_capacity.displayZizeInGb()

            logger.error("The storage does not contain enough space")
            logger.info("Trying to remove oldest backup")
            cleaner=StorageCleaner(store,3)
            logger.debug("We will clean %s ",store)
            if cleaner.removeOldestFile() == False:
                logger.error("Error when attempt to remove older file in %s",store)
            else:
                logger.info("Successfully remove oldest zip file in %s",store)
            logger.info("Check if there is enough space to zip")
            if not storage_capacity.canFileBeingZipped():
                logger.info("Still not enough space to zip %s to %s",dest_webdav_copy,store)
                exit();
        logger.info("Storage root contains enough space ")
        logger.info("Create zip from %s to %s ", dest_webdav_copy, root)
        start_time=time.time()
        if not nozip:
            logger.info("folder %s will be zipped as nozip flag is set to True",dest_webdav_copy)
            update = client.zip(dest_webdav_copy, root, update)
            logger.info("size=%s Go", str(int(update["size"] / (1024 * 1024 * 1024))))
            logger.info("number of files=%s", str(update["number"]))
            logger.info("Creation of zip Operation competed in %s seconds ", (time.time() - start_time))
            logger.info("In the store %s search for file older than %s days", store, retention_day)
        else:
            logger.info("The folder %s will not be zipped as nozip flag is set to True",dest_webdav_copy)
        if noclean:
            logger.info("noclean flag enabled. %s will not be cleaned",store)
            logger.info("The global backup process takes %s seconds", (time.time() - start_time_global))
            exit()
        files_to_delete = list()
        cleaner = StorageCleaner(store, retention_day)
        files_to_delete = cleaner.search_by_age()
        logger.debug("files to delete;count=%s;list=%s", str(len(files_to_delete)), str(files_to_delete))
        cleaner.delete(files_to_delete)
        logger.info("Cleaning of %s succeed",str(files_to_delete))
        logger.info("Cleaning storage folder %s:",dest_webdav_copy)
        cleaner.delete_directory(dest_webdav_copy)
        logger.info("Cleaning of %s succeed",dest_webdav_copy)
        logger.info("The global backup process takes %s seconds", (time.time() - start_time_global))
    except PermissionError as e:
        logger.error("Error when cleaning file. Reason=%s",str(e) )
    except Exception as e:
        logger.error("General error. Reason=%s",str(e))

if __name__ == "__main__":
    app()
