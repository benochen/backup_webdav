import os.path
import time
from datetime import datetime,timedelta
import shutil

from logzero import logger
class StorageCleaner:

    def __init__(self,search_folder,age):

        self.search_folder = search_folder
        self.age=age


    def getSearchFolder(self):
        return self.search_folder

    def getAge(self):
        return self.age

    def removeOldestFile(self):
        if not os.path.exists(self.search_folder):
            logger.error("%s does not exists", self.search_folder)
            return False

        logger.info("%s does  exists", self.search_folder)
        os.chdir(self.search_folder)

        files=sorted(os.listdir(os.getcwd()),key=os.path.getmtime)
        if(len(files)<=1):
            logger.error("No files to be removed in %s",self.search_folder)
            return False
        oldest=files[0]
        logger.info("Attempt to remove %s",oldest)
        os.remove(oldest)


        if(os.path.exists(oldest)):
            logger.error("Removal of %s failed",oldest)
            return False
        else:
            logger.error("Remove of %s is sucessfull",oldest)
            return True


    def search_by_age(self):
        files_to_delete=list()
        for path,dirs,files in os.walk(self.search_folder):
            for f in files:
                fp=os.path.join(path,f)
                ctime=datetime.strptime(time.ctime(os.path.getctime(fp)),"%a %b %d %H:%M:%S %Y")
                ctime_delta = ctime + timedelta(days=int(self.age)-1)
                today=datetime.today()
                if (today >=ctime_delta ):
                    logger.debug("%s older than %s",str(today),str(ctime_delta))
                    files_to_delete.append(fp)
        print(len(files_to_delete))
        return files_to_delete

    def delete(self,list_of_files):
        if len(list_of_files) == 0:
            return False

        for f in list_of_files:
            os.remove(f)
        return True
    def delete_directory(self,directory_path):
        shutil.rmtree(directory_path,ignore_errors=True)

    def computeDirectorySize(self,path):
        file_size=0
        path_tmp=path
        for path,dirs,files in os.walk(path_tmp):
            for f in files:
                fp=os.path.join(path,f)
                if(os.path.isfile(fp)):
                    file_size+=os.path.getsize(fp)
                else:
                    file_size=self.computePathSize(fp)

        return file_size



    def canFileBeingZipped(self):
        if self.file_size == -1  :
            self.file_size=self.computePathSize()
        if self.storage_size == -1 or self.storage_used == -1 or self.storage_free == -1:
            self.computeStorageSize()

        print(self.file_size)
        return  float(str(self.file_size)) <= self.storage_free * self.quota


