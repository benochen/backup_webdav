from typing import Optional
import os
import time
import typer
import pathlib
import configparser
from  tools.StorageCapacity import StorageCapacity
from tools.StorageCleaner import StorageCleaner
from workers.WebdavWorker import WebDavWorker
from webdav3.exceptions import WebDavException
from logzero import logger, logfile
import json
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






@app.command()
def backup(root: Optional[str] = None, entity: Optional[str]="default"):
    try:
        config = configparser.ConfigParser()
        config.read("config.ini")
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
        update = client.completeBackup(update, root, dest)
        logger.debug("root=%s",root)
        to_zip = dest + os.path.sep + root
        logger.debug("to_zip=%s",to_zip)
        logger.info("Backup  %s complete", root)
        logger.info("Copy of remote file completed in %s seconds ", (time.time() - start_time))
        logger.info("Check there is enough space to zip folder %s", to_zip)
        storage_capacity = StorageCapacity("/", to_zip, 0.9)
        dest_webdav_copy=dest + os.path.sep + root
        if (not storage_capacity.canFileBeingZipped()):
            logger.error("The storage does not contain enough space")
            exit()
        logger.info("Storage root contains enough space ")
        logger.info("Create zip from %s to %s ", dest_webdav_copy, root)
        update = client.zip(dest_webdav_copy, root, update)
        logger.info("size=%s Go", str(int(update["size"] / (1024 * 1024 * 1024))))
        logger.info("number of files=%s", str(update["number"]))
        logger.info("Creation of zip Operation competed in %s seconds ", (time.time() - start_time))
        logger.info("In the store %s search for file older than %s days", store, retention_day)
        files_to_delete = list()
        cleaner = StorageCleaner(store, retention_day)
        files_to_delete = cleaner.search_by_age()
        logger.debug("files to delete;count=%s;list=%s", str(len(files_to_delete)), str(files_to_delete))
        cleaner.delete(files_to_delete)
        logger.info("Cleaning of %s succeed",str(files_to_delete))
        logger.info("Cleaning storage folder %s:",dest_webdav_copy)
        cleaner.delete_directory(dest_webdav_copy)
        logger.info("Cleaning of %s succeed",dest_webdav_copy)
    except PermissionError as e:
        logger.error("Error when cleaning file. Reason=%s",str(e) )
    except Exception as e:
        logger.error("General error. Reason=%s",str(e))

if __name__ == "__main__":
    app()
