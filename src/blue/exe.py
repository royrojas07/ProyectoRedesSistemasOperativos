import shutil
import subprocess

shutil.copy("spider.py", "spider1")
subprocess.call(['chmod', '0777', "spider1"]) #el ejecutable que acabo de armar le doy permisos 

