from typing import Optional
import os
import time
import typer
import pathlib
import configparser
from webdav3.client import Client
from webdav3.exceptions import WebDavException

app = typer.Typer()


@app.command()
def hello(name: Optional[str] = None):
    if name:
        typer.echo(f"Hello {name}")
    else:
        typer.echo("Hello World!")


@app.command()
def bye(name: Optional[str] = None):
    if name:
        typer.echo(f"Bye {name}")
    else:
        typer.echo("Goodbye!")


def copy(client,root,update,dest):
    print("enter in method copy with path="+root)
    print("update="+str(update))
    folders=client.list(root,get_info=True)
    print(folders)
    for file in folders:
        if file["isdir"]:
            length=len(file["path"].split("/"))
            endPath=file["path"].split("/")[length-2]
            print("endPath="+endPath)
            newRoot=root+"/"+endPath
            print("new root="+newRoot)
            if(  root.split("/")[len(root.split("/"))-1] != endPath):
                print("HERE")
                update= copy(client,newRoot,update,dest)
        else:
            destinationFolder=dest+os.path.sep+root.replace("/",os.path.sep)
            completeDestinationPath=destinationFolder+os.path.sep+os.path.basename(file["path"])
            os.makedirs(destinationFolder, exist_ok=True)
            remotePath=pathlib.Path(file["path"])
            remotePathStr= str(remotePath.relative_to(*remotePath.parts[:5]).as_posix())
            print("file "+remotePathStr+" will be copied in "+completeDestinationPath)
            try:
                if( not os.path.isfile(completeDestinationPath)):
                    print("File does not exist. I copy it")
                    client.download_sync(remote_path=remotePathStr, local_path=completeDestinationPath)

                else:
                    print("file Exist. skip")
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




@app.command()
def ls(root: Optional[str] = None):
    config=configparser.ConfigParser()
    config.read("config.ini")


    options = {
        'webdav_hostname':config["WEBDAV"]['url'] ,
        'webdav_login': config["WEBDAV"]['username'],
        'webdav_password': config["WEBDAV"]['password']
    }
    start_time = time.time()
    update=dict()
    dest=config["BACKUP"]['destination']
    update["size"]=0
    update["number"]=0
    client = Client(options)
    update=copy(client,root,update,dest)
    print("size="+str(int(update["size"]/(1024*1024*1024)))+" Go")
    print("number of files="+str(update["number"]))
    print("--- %s seconds ---" % (time.time() - start_time))
if __name__ == "__main__":
    app()
