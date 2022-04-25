import numbers
import os.path
import shutil
from Exceptions.StorageSizeQuotaRangeException import StoarageSizeQuotaRangeException
from Exceptions.NotANumberException import NotANumberException
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

        print(self.file_size)
        return  float(str(self.file_size)) <= self.storage_free * self.quota


