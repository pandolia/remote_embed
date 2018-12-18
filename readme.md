
Introduction
-------------

**remote_embed** is a remote version of [python code.interact](https://docs.python.org/2/library/code.html#code.interact) which let your remote python process break into interactive mode so that you can attach to and interact with it from a local machine(or another terminal in the same machine).

The only function you will use is **embed()**. As I said, it is just a remote version of **code.interact()**.

When you need remote_embed
---------------------------

* When you want to debug a python process runs at a remote mathine.
* When you want to debug a GUI python process which without a terminal.
* When you want to debug a C/C++ process which embed python intepreter in itself.

Usage
-----

1. Install **remote_embed** in your remote machine:

```bash
pip install remote_embed
```

Or just put [remote_embed.py](https://raw.githubusercontent.com/pandolia/remote_embed/master/remote_embed.py) into your remote project directory.

2. In remote script, import **remote_embed** and insert **embed** at the line where you want to break:

```python
from remote_embed import Embed; embed = Embed('your_ip', your_port)

a = 0

def myfunc(x, y, z):
    print(a, x, y, z)
    embed()
    print(a, x, y, z)

myfunc(1, 2, [3])
```

Run the script on the remote machine, you will see the remote process break at that line and waiting for a local debugger to attach.

3. Run **nc {yourip} {port}** on your local machine to attach to and interact with the remote process. You can read local variables and global variables of the remote process, and input python statements/expressions to be executed/evaluated in the remote process. When you finish, type **exit** or just close the local terminal. This will cause the remote process jump out from interactive mode and resume the execution.

In windows, you can download **nc** from [here](https://eternallybored.org/misc/netcat/).

If you just want interact with another process from the same machine, just use **embed = Embed(port=6000)**. This will make the process break and listen on **127.0.0.1:6000**. Then you can open another terminal and run **nc 127.0.0.1 6000** to attach to and interact with it.

If you just use **embed = Embed()**, the process will listen on **127.0.0.1:first_available_port**, and print the port being listened on its terminal(specifically: its sys.stderr).

4. If you are tired of opening another terminal and typing nc commands, you can pass a **popup** parameter and make the process break and then automatically popup a new terminal which has already attached to itself. On windows, you just need to provide the path of **nc.exe**, for example:

```python
from remote_embed import Embed; embed = Embed(popup='\\yourpath\\nc.exe')

def myfunc(x, y, z):
    # ...
    embed() # break here and popup a new interactive terminal
    # ...
```

On other platforms, you need to write a popup function, take MacOS for example:

```python
import subprocess

# this function must popup a new terminal which runs "nc {host} {port}"
# and return immediately. DO NOT BLOCK.
def mypopup(host, port):
    subprocess.call(['open','-W','-a','Terminal.app', 'nc', host, str(port)])

from remote_embed import Embed; embed = Embed(popup=mypopup)

def myfunc(x, y, x):
    # ...
    embed() # break here and popup a new interactive terminal
    # ...
```


Detail of the Embed function
-----------------------------

```python
def Embed(
    host='127.0.0.1',           # the ip which you want to listen at
    port=0,                     # the port which you want to listen at
    popup=None,                 # a popup function or the path of 'nc.exe'(in windows)
    log_writer=sys.stderr,      # the logger's writer
    this_coding=None,           # the coding of the process which you want to debug,
                                # default to 'gb18030' in windows, and 'utf8' in other platforms
    remote_coding=None,         # the coding of the debugger, default to `this_coding`
    help_info=None              # a help infomation printed at the debugger's terminal when it attached,
                                # default to the line infomation of the break point
):

    # ...

    def embed():
        # ...
    
    return embed
```
