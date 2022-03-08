from typing import Optional
import os
import typer
import easywebdav
from webdav3.client import Client

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


def copy(client,path):
    print("enter in method copy with path="+path)
    folders=client.list(path,get_info=True)
    print(folders)
    for file in folders:
        if file["isdir"]:
            length=len(file["path"].split(os.path.sep))
            endPath=file["path"].split(os.path.sep)[length-2]
            print("endPath="+endPath)
            newRoot=os.path.join(path,endPath)
            print("new root="+newRoot)
            if(  path.split(os.path.sep)[len(path.split(os.path.sep))-1] != endPath):
                print("HERE")
                copy(client,newRoot)
        else:
            print("file "+file["path"]+" file will be copied")




@app.command()
def ls(path):
    options = {
        'webdav_hostname': "",
        'webdav_login': "",
        'webdav_password': ""
    }
    client = Client(options)
    copy(client,root)

if __name__ == "__main__":
    app()
