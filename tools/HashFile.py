import hashlib


class Sha256:
    __instance = None

    @staticmethod
    def get_instance():
        if Sha256.__instance is None :
            Sha256.__instance=Sha256()
        return Sha256.__instance

    def __init__(self):
        file_hash=hashlib.sha256()
        self.BLOCK_SIZE=65536

    def compute(self,file):
        file_hash = hashlib.sha256()
        with open(file,'rb') as f:
            fb = f.read(self.BLOCK_SIZE)
            while len(fb)> 0:
                file_hash.update(fb)
                fb=f.read(self.BLOCK_SIZE)
        return file_hash.hexdigest()
