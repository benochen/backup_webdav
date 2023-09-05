class Stat:
    def __init__(self):
        self.file_copied = 0
        self.file_size = 0
        self.file_total_count_planned=0
        self.file_total_size_planned=0

    def count(self, size):
        self.file_copied += 1
        self.file_size += size

    def incrementTotalSizeAndCountFile(self,size):
        self.file_total_count_planned+=1
        self.file_total_size_planned+=size

    def display_summary(self):
        print("Total number of files copied:", self.file_copied)
        print("Total size of files copied:", self.file_size)

    def getFileSize(self):
        return self.file_size

    def getFileCopied(self):
        return self.file_copied

    def getFileCountPlanned(self):
        return self.file_count_planned

    def getCompletion(self):
        return (self.file_count_planned/self.file_copied)*100

    def __str__(self):
        return f'Stat(file_count_planned={self.file_total_count_planned},file_copied={self.file_copied}, file_size={self.file_size})'