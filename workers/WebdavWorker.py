

import os
from datetime import datetime
import pathlib
import shutil
from webdav3.client import Client
from webdav3.exceptions import WebDavException
from logzero import logger, logfile
from logger.MyloggerJson import JSONLogger
import zipfile

from models.catalog.FileState import FileState
from models.catalog.FullBackupCatalog import FullBackupCatalog
from models.catalog.ItemCatalog import ItemCatalog
from tools.HashFile import Sha256
from tools.stat import Stat


class WebDavWorker:

    def __init__(self,url,username,password,root_archive,entity):
        self.url=url
        self.username=username
        self.password=password
        self.options = {
            'webdav_hostname': self.url,
            'webdav_login': self.username,
            'webdav_password': self.password
        }
        self.client = Client(self.options)
        self.root_archive=root_archive
        self.entity=entity

    def __init__(self,config:dict,fullcatalog_repository:FullBackupCatalog):
        self.url=config["WEBDAV"]["url"]
        self.username=config["WEBDAV"]["username"]
        self.password=config["WEBDAV"]["password"]
        self.options = {
            'webdav_hostname': self.url,
            'webdav_login': self.username,
            'webdav_password': self.password
        }
        self.client = Client(self.options)
        self.root_archive=config["BACKUP"]["store"]
        self.entity=config["BACKUP"]["entity"]
        self.logger=JSONLogger(config["LOGGER"]["logfile"],config["WEBDAV"]["username"],config["BACKUP"]["entity"])

    def computeDiskSize(self,path):
        capacity = dict()
        capacity['total'],capacity['used'],capacity['free'] = shutil.disk_usage(path)
        return capacity

    def listFileToZip(self,source):
        logger.debug("Start listing file in %s to be zipped",source)
        if not source:
            logger.error("Error with sources")
            return []

        if os.path.exists(source):
            logger.error("%s does not exists",source)
        logger.debug("Check done. Start listing")
        files = []
        # r=root, d=directories, f = files
        for r, d, f in os.walk(source):
            for file in f:
                files.append(os.path.join(d, file))

        return files


    def computePathSize(self,path):
        return os.scandir(path)


    def zipFile(self,sources,destname,update):
        logger.debug("Start zip files")
        logger.debug("Zipping folder %s",destname)

        if( not destname):
            return False

        if(not sources):
            return False

        if(not os.path.exists(self.root_archive)):
            os.mkdir(self.root_archive)
        now=datetime.today().strftime("%Y%m%d%H%M%S")
        final_dest_directory= self.root_archive+os.path.sep+self.entity
        if not os.path.exists(final_dest_directory):
            os.makedirs(final_dest_directory)
        archive_path=final_dest_directory+os.path.sep+now+'_'+destname+".zip"
        update["archive_path"] = archive_path
        logger.debug("Start zip process")
        i=1
        size=len(sources)
        logger.debug("%s files will be zipped",size)
        with zipfile.ZipFile(archive_path,"w") as zf:
            for file in sources:
               logger.debug("Zip operation completed at %s %%",str(int((i/size)*100)))
               zf.write(file)
               i=i+1
        return update


    def zip_catalog(self,source,destname,stat):
        if( not destname):
            return False

        if(not source):
            return False

        if(not os.path.exists(self.root_archive)):
            os.mkdir(self.root_archive)


        now=datetime.today().strftime("%Y%m%d%H%M%S")

        final_dest_directory= self.root_archive+os.path.sep+self.entity
        if not os.path.exists(final_dest_directory):
            os.makedirs(final_dest_directory)
        final_dest=final_dest_directory+os.path.sep+now+'_'+destname
        archive_path = final_dest
        shutil.make_archive(final_dest, "zip", source)
        return stat,archive_path


    def zip(self,source,destname,update):
        if( not destname):
            return False

        if(not source):
            return False

        if(not os.path.exists(self.root_archive)):
            os.mkdir(self.root_archive)


        now=datetime.today().strftime("%Y%m%d%H%M%S")

        final_dest_directory= self.root_archive+os.path.sep+self.entity
        if not os.path.exists(final_dest_directory):
            os.makedirs(final_dest_directory)
        final_dest=final_dest_directory+os.path.sep+now+'_'+destname
        update["archive_path"] = final_dest
        shutil.make_archive(final_dest, "zip", source)
        return update



    def completeBackupCatalog(self,stat:Stat,root:str,dest:str,files):
        print(stat)
        files=files
        logger.debug("enter in method copy with remote folder=%s",root)
        logger.debug("update=%s", stat)
        folders = self.client.list(root, get_info=True)
        for file in folders:
            if file["isdir"]:
                length = len(file["path"].split("/"))
                endPath = file["path"].split("/")[length - 2]
                logger.debug("endPath=%s",endPath)
                newRoot = root + "/" + endPath
                if (root.split("/")[len(root.split("/")) - 1] != endPath):

                    stat,files = self.completeBackupCatalog(stat,newRoot, dest,files)
            else:
                destinationFolder = dest + os.path.sep + root.replace("/", os.path.sep)
                completeDestinationPath = destinationFolder + os.path.sep + os.path.basename(file["path"])
                os.makedirs(destinationFolder, exist_ok=True)
                remotePath = pathlib.Path(file["path"])
                remotePathStr = str(remotePath.relative_to(*remotePath.parts[:5]).as_posix())
                logger.debug("file %s will be copied in %s",remotePathStr,completeDestinationPath)
                try:
                    if (not os.path.isfile(completeDestinationPath)):
                        logger.debug("File %s does not exist. Copying",completeDestinationPath)
                        self.client.download_sync(remote_path=remotePathStr, local_path=completeDestinationPath)


                    else:
                        logger.debug("File %s exists. Skipping",completeDestinationPath)
                    if file["size"]:
                        stat.count(stat.getFileSize()+int(file["size"]))
                    hash = Sha256.get_instance().compute(completeDestinationPath)
                    file_1 = ItemCatalog(path=completeDestinationPath,
                                         hash_file=hash,
                                         type='file',
                                         file_state=FileState.ADDED,
                                         file_size=file["size"]
                                         )
                    files.append(file_1)


                except WebDavException as exception:
                    with open('errors.log', 'w') as f:
                        f.write(remotePathStr)
                        f.close()
                except KeyError as exception:
                    with open('key_errors.log', 'w') as f:
                        f.write(remotePathStr)
                        f.close()

        return stat,files

    def completeBackup(self,update,root,dest):

        logger.debug("enter in method copy with remote folder=%s",root)
        logger.debug("update=%s", update)
        folders = self.client.list(root, get_info=True)
        for file in folders:
            if file["isdir"]:
                length = len(file["path"].split("/"))
                endPath = file["path"].split("/")[length - 2]
                logger.debug("endPath=%s",endPath)
                newRoot = root + "/" + endPath
                if (root.split("/")[len(root.split("/")) - 1] != endPath):

                    update = self.completeBackup( update,newRoot, dest)
            else:
                destinationFolder = dest + os.path.sep + root.replace("/", os.path.sep)
                completeDestinationPath = destinationFolder + os.path.sep + os.path.basename(file["path"])
                os.makedirs(destinationFolder, exist_ok=True)
                remotePath = pathlib.Path(file["path"])
                remotePathStr = str(remotePath.relative_to(*remotePath.parts[:5]).as_posix())
                logger.debug("file %s will be copied in %s",remotePathStr,completeDestinationPath)
                try:
                    if (not os.path.isfile(completeDestinationPath)):
                        logger.debug("File %s does not exist. Copying",completeDestinationPath)
                        self.client.download_sync(remote_path=remotePathStr, local_path=completeDestinationPath)

                    else:
                        logger.debug("File %s exists. Skipping",completeDestinationPath)
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


