import os
import zipfile
import shutil

text = f"A greenhouse gas is a gas that absorbs and emits radiant energy within the thermal infrared range, causing the greenhouse effect. The primary greenhouse gases in Earth's atmosphere are water vapor (H2O), carbon dioxide (CO2), methane (CH4), nitrous oxide (N2O), and ozone. Without greenhouse gases, the average temperature of Earth's surface would be about -18 °C (0 °F), rather than the present average of 15 °C (59 °F).The atmospheres of Venus, Mars and Titan also contain greenhouse gases."

def currentDir():
    return os.getcwd()

def listdirs(directory):
    try:
        entries = os.listdir(directory)
        directories = [entry for entry in entries if os.path.isdir(os.path.join(directory, entry))]
        return directories
    except Exception as e:
        return str(e)

def makeDir(nudir):
    return os.mkdir(nudir)

def changeDir(nudir):
    os.chdir(nudir)
    
def removeDir(dirname):
    os.rmdir(dirname)
    
def removeFile(fname):
    os.remove(fname)

def listfiles(directory):
    try:
        entries = os.listdir(directory)
        files = [entry for entry in entries if os.path.isfile(os.path.join(directory, entry))]
        return files
    except Exception as e:
        return str(e)
    
def utilUnzip(zfile):  
    with zipfile.ZipFile(zfile,"r") as zf:
        zf.extractall()

def createFile(string):
    fdesc = "temp.txt"
    file = open(fdesc, 'w')
    file.write(string)
    file.close()
    return file

def readFile(fname):
    file = open(fname, 'r')
    text = file.read()
    file.close()
    return text

def filecopy(source,destination):
    dest = shutil.copy(source, destination)

def Validate():
    print("Current Directory",currentDir())
    if os.path.exists("Sandbox") and os.path.isdir("Sandbox"):
        shutil.rmtree("Sandbox")
    makeDir("Sandbox")
    changeDir("Sandbox")
    print("Current Directory",currentDir())
    createFile(text)
    print("File contents",readFile("temp.txt"))
    filecopy("temp.txt","copy1.txt")
    filecopy("temp.txt","copy2.txt")
    filecopy("temp.txt","copy3.txt")
    filecopy("../Utility.zip","copy.zip")
    print("File List",listfiles("."))
    utilUnzip("copy.zip")
    removeFile("temp.txt")
    filelist = listfiles(".")
    [removeFile(file) for file in filelist]
    print("After files removed: ",listfiles("."))
    changeDir("..")
    removeDir("Sandbox")
    return True
    
import unittest
class Tests(unittest.TestCase):
    def test(self):
        success = Validate()
        self.assertEqual(success,True)
        
if __name__=='__main__':
    unittest.main()
    