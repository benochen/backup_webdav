import configparser

from models.catalog.FullBackupCatalog import FullBackupCatalog
from unittest import TestCase

class Test(TestCase):
        def test_fullbackup_repository(self):
                config = configparser.ConfigParser()
                config.read('..\\..\\config.ini')
                print(config["BACKUP"]["store"])
                fullbackup_repository = FullBackupCatalog(config["BACKUP"]["store"],config["BACKUP"]["entity"])
                fullbackup_repository.setStatus("OK")
                fullbackup_repository.setStartAt("2020-01-01 00:00:00")
                fullbackup_repository.setEndAt("2020-01-01 00:00:00")
                fullbackup_repository.setExpirationTime("2020-01-01 00:00:00")
                fullbackup_repository.setZipSize(100)
                fullbackup_repository.setZipPath("test")
                fullbackup_repository.setHashZip("test")
                fullbackup_repository.setFiles(["test"])
                fullbackup_repository.setHost("test")
                fullbackup_repository.setSourceType("test")
                fullbackup_repository.setBackupId("test")
                fullbackup_repository.save()


        def test_findInProgressByEntity():
                config = configparser.ConfigParser()
                config.read('config.ini')
                backup_id="test"
                fullbackup_repository = FullBackupCatalog(config["BACKUP"]["store"],config["BACKUP"]["entity"])
                fullbackup_repository.setStatus("OK")
                fullbackup_repository.setStartAt("2020-01-01 00:00:00")
                fullbackup_repository.setEndAt("2020-01-01 00:00:00")
                fullbackup_repository.setExpirationTime("2020-01-01 00:00:00")
                fullbackup_repository.setZipSize(100)
                fullbackup_repository.setZipPath("test")
                fullbackup_repository.setHashZip("test")
                fullbackup_repository.setFiles(["test"])
                fullbackup_repository.setHost("test")
                fullbackup_repository.setSourceType("test")
                fullbackup_repository.setBackupId()
                fullbackup_repository.save()
                result = FullBackupCatalog.findInProgressByEntity(config["BACKUP"]["entity"])
                assert result == None
                fullbackup_repository.delete(backup_id)

