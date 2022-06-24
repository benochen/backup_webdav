import numbers
import os.path
import shutil
from Exceptions.StorageSizeQuotaRangeException import StoarageSizeQuotaRangeException
from Exceptions.NotANumberException import NotANumberException
from logzero import logger

class StorageCapacity:

    def __init__(self,storage_name,file_path,quota):


        if  not isinstance(quota,numbers.Number):
            raise NotANumberException("The value of quota should be a number")
        if(quota < 0 and quota > 1 ):
            raise StoarageSizeQuotaRangeException("The quota should be a float between 0 and 1")
        self.storage_name = storage_name
        self.file_path = file_path
        self.storage_size = -1
        self.storage_free = -1
        self.storage_used = -1
        self.file_size = -1
        self.quota = quota

    def getStorageName(self):
        return self.storage_name

    def getStoragePath(self):
        return self.file_path


    def getStorageSize(self):
        if(self.storage_size == -1):
            self.computeStorageSize()

        return self.storage_size

    def getFileSize(self):
        if(self.file_size == -1):
            self.file_size = self.computeFileSize()


    def computeStorageSize(self):
        logger.debug("The size of %s is %s",str(self.storage_name),str(shutil.disk_usage(self.storage_name)))
        self.storage_size,self.storage_used,self.storage_free =  shutil.disk_usage(self.storage_name)

    def computePathSize(self):
        if(os.path.isfile(self.file_path)):
            self.file_size=os.path.getsize(self.file_path)
        else:
            self.file_size = self.computeDirectorySize(self.file_path)
        return self.file_size

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
        logger.debug("%s-%s=%s",str(self.storage_free),str(self.storage_size),str(float(self.storage_free-self.file_size)))
        if self.storage_free - self.file_size <=0:
            logger.debug("%s-%s=%s",str(self.storage_free),str(self.storage_size),str(float(self.storage_free-self.file_size)))
            logger.debug("storage_free - file_size is less or equals to zero. Abort")
        else:
            logger.info("The disk has a storage capacity of %s GB and can store a zip file of %s GB. Check if it will not exceed quota of %s %% ",str(self.getStorageSizeInGB()),str(self.getFileSizeInGB()),str(self.quota*100))
            if float(self.storage_free-self.file_size) <= (self.storage_free*self.quota):
                logger.debug("Enough space to zip but the file zip will exit quoata abort;")
            else:
                logger.info("Quota is ok")
                logger.debug("It will remain %s GB after the zip is created",str((self.storage_free-self.file_size)/(1024*1024*1024)))
        return  float(self.storage_free-self.file_size>0) and float(self.storage_free-self.file_size) >= (self.storage_free*self.quota)

    def getFileSizeInGB(self):
        print(self.file_size)
        return self.file_size/( 1024*1024*1024)

    def getStorageSizeInGB(self):
        return self.storage_size/(1024*1024*1024)

    def getFreeStorageInGb(self):
        return self.storage_free/(1024*1024*1024)

    def displayZizeInGb(self):
        logger.debug("file_size="+str(self.getFileSizeInGB())+";storage_size="+str(self.getStorageSizeInGB())+";storage_free="+str(self.getFreeStorageInGb()))

