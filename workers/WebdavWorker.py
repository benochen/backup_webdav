

import os
from datetime import datetime
import pathlib
import shutil
from webdav3.client import Client
from webdav3.exceptions import WebDavException
from logzero import logger, logfile


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


    def computeDiskSize(self,path):
        capacity = dict()
        capacity['total'],capacity['used'],capacity['free'] = shutil.disk_usage(path)
        return capacity


    def computePathSize(self,path):
        return os.scandir(path)

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


