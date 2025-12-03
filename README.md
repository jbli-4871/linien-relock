LINIEN - RELOCK
======

This is a copy of [linien v0.3.2](https://github.com/linien-org/linien/tree/v0.3.2) that's been modified to:
- fix package dependency issues
- include a "Relock" mode that uses the RedPitaya to control a Vescent Lockbox via a TTL pulse through Analog Output 2.

Please refer to the main [linien v0.3.2 repo](https://github.com/linien-org/linien/tree/v0.3.2) for more details about the base package.

The installation has different syntax for different operating systems, so refer to the relevant section for your own system.

Installation Instructions (Mac OS)
---------------
### 0. Giving yourself a workspace

We want to keep track of where all of our files go, so first create a folder somewhere on your computer that you can access. Your Desktop is a good place. All of our other steps will be done inside this folder, so name it something descriptive "linien_folder". Next, open a Terminal and move to there using *cd*. You can check what directory you're in with the following command in your terminal:
```bash
pwd
```

You should see the name of the folder as the last thing in this output. 

### 1. Setting up a virtual environment

Because the original linien v0.3.2 package depends on several packages that have since been updated/deprecated, the safest way to install this version of linien on a new computer is to create a virtual environment (venv). This prevents version compatibility errors between linien's required packages and any packages you might already have installed on your computer. 

Before creating the venv, check if you have Python 3.12 installed. Linien will not run on newer version of Python. In your command window type
```bash
python3.12 --version
```

If this does not return something like "Python 3.12.x", you will need to install Python 3.12. You can do this by visiting the [official Python website](https://www.python.org/downloads/release/python-3127/) and downloading the installer that's relevant for your operating system. It doesn't matter which version of Python 3.12 you install, so just install any stable release like the one in the link. Because we are on Mac, you can just scroll to the bottom of the page and click the yellow button that says "Download macOS 64-bit universal2 installer"

Now, after following the instructions in the installer, in the same terminal window run:
```bash
python3.12 --version
```

If you get a result like "Python 3.12.x" then you've successfully installed the package. 

Next, use this Python version to create a virtual environment to house all of the linien packages. 
```bash
python3.12 -m venv linienvenv
```

Attach this venv to your command window:
```bash
source linienvenv/bin/activate
```

After venv activation you should see your prompt line have a "(linienvenv)" before your file location.

Note where your virtual environment is by running this command (again) in the same command window that you just activated your virtual environment:
```bash
where python
```

Your output might contain multiple lines, but the first line should point to your virtual environment location: something like */Users/jeffreyli/Desktop/linienvenv/bin/python*. Copy this somewhere for later.

### 2. Installing linien-relock on your computer: 

Now you are (finally!) ready to install linien. First, download or clone this Github repo. There are many ways to do this, but the easiest is to navigate to the top of the page, click the green "<> Code" button, and download the zip file. 

Whatever method you use, make sure linien-relock folder is inside your workspace folder. Inside the linien-relock folder, there is a file called *install_linien.sh*. Open this file in a text editor. The tenth line says
```bash
VENV="/Users/jeffreyli/Desktop/Ni Lab/linienvenv"
```

Modify this to the path for your virtual environment (DO NOT include "/bin/python") that you recorded in step 1 of the installation. With this complete, in your terminal navigate to the linien-relock folder and run the following command:
```bash
./install_linien.sh
```

This should install linien-relock and all of its necessary dependencies inside your venv

### 3. Installing linien-relock on your Red Pitaya:

First, install the Red Pitaya OS 1.04-28 found on the [Red Pitaya website](https://www.python.org/downloads/release/python-3127/) with installation instructions at the bottom of the page. Note down the host name of the Red Pitaya. It should be something of the form "RP-XXXXXX.LOCAL/" written on the board above the ethernet port. Afterwards, you should connect the Red Pitaya via ethernet to a router that has internet access. There are ways to set up linien on the Red Pitaya without internet, but they're much more painful.

If the Red Pitaya has internet access: In your terminal running the virtual environment, run 
```bash
python
```

to create a Python screen and run the following two lines.
```python
from linien.gui.app import run_application
run_application()
```

This will bring up the GUI. You can click the "New device" button and add your device's hostname in the instructed box. Once added, click on the hostname that corresponds to your Red Pitaya in the main window. This will automatically connect to the Red Pitaya and prompt you to install the server. Click "yes" and wait for the install to finish/the GUI to appear. Close the GUI. We now need to modify this install with our custom files for relock.

Now, we need to establish secure communication between our computer and the Red Pitaya running linien. We do this by generating an SSH keypair

Run the following command in any terminal window:
```bash
ssh-keygen -t rsa -b 4096
```
Press Enter when prompted to accept defaults. Then copy this ssh key onto the Red Pitaya with 
```bash
ssh-copy-id root@rp-XXXXXX.local
```
When prompted, enter "root" as the password for the Red Pitaya. You can then test password-less login with
```bash
ssh root@rp-XXXXXX.local
```
If this does not prompt you for a password, then you've successfully copied the SSH key. Exit the SSH window by running *exit* inside of it.

You can now set up the script to copy the new server files over. Find the file in the linien-relock folder called *install_relock_server.sh* and locate line 16. It should say 
```bash
RP_IP="rp-XXXXXX.local"        # Red Pitaya IP address EDIT THIS
```
Modify this with your Red Pitaya host name. Then, in a terminal run the bash file with
```bash
./install_relock_server.sh
```

This completes your installation of linien-relock on both your computer and the Red Pitaya

Installation Instructions (Windows)
---------------

### 0. Giving yourself a workspace

We want to keep track of where all of our files go, so first create a folder somewhere on your computer that you can access. Your Desktop is a good place. All of our other steps will be done inside this folder, so name it something descriptive "linien_folder". Next, open a Command Prompt and move to there using *cd*. You can check what directory you're in with the following command in your Command Prompt:
```bash
cd
```

### 1. Setting up a virtual environment

Because the original linien v0.3.2 package depends on several packages that have since been updated/deprecated, the safest way to install this version of linien on a new computer is to create a virtual environment (venv). This prevents version compatibility errors between linien's required packages and any packages you might already have installed on your computer. 

Before creating the venv, check if you have Python 3.12 installed. Linien will not run on newer version of Python. Open a command window and type
```bash
python3.12 --version
```

If this does not return something like "Python 3.12.x", you will need to install Python 3.12. You can do this by visiting the [official Python website](https://www.python.org/downloads/release/python-3127/) and downloading the installer that's relevant for your operating system. It doesn't matter which version of Python 3.12 you install, so just install any stable release like the one in the link. Because we are on Windows, you can just scroll to the bottom of the page and click the yellow button that says "Download Python install manager" and follow the instructions there.

After this, in the same Command Prompt window as earlier, run:
```bash
py -0
```
If you see a line that says "-V:3.12 " then you've successfully installed the package. 

Next, use this Python version to create a virtual environment to house all of the linien packages. Run:
```bash
py -3.12 -m venv linienvenv
```

Attach this venv to your command window.
```bash
linienvenv\Scripts\activate.bat
```

After venv activation you should see your prompt line have a "(linienvenv)" before your file location.

Note where your virtual environment is by running this command (again) in the same command window that you just installed your virtual environment:
```bash
where python
```

Your output might contain multiple lines, but the first line should point to your virtual environment location: something like *C:\Users\jeffreyli\Desktop\linienvenv\Scripts\python.exe*. Copy this somewhere for later.

### 2. Installing linien-relock on your computer: 

Now you are (finally!) ready to install linien. First, download or clone this Github repo. There are many ways to do this, but the easiest is to navigate to the top of the page, click the green "<> Code" button, and download the zip file. 

Whatever method you use, make sure linien-relock folder is inside your workspace folder. Inside the linien-relock folder, there is a file called *install_linien.bat*. Open this file in a text editor. The ninth line says:
```bash
set VENV=C:\Users\jeffreyli\Desktop\Ni Lab\linienvenv
```

Modify this to the path for your virtual environment that you recorded in step 1 of the installation (DO NOT include "/bin/python"). With this complete, in your terminal (with the virtual environment) run the following command:
```bash
install_linien.bat
```

### 3. Installing linien-relock on your Red Pitaya:

First, install the Red Pitaya OS 1.04-28 found on the [Red Pitaya website](https://www.python.org/downloads/release/python-3127/) with installation instructions at the bottom of the page. Note down the host name of the Red Pitaya. It should be something of the form "RP-XXXXXX.LOCAL/" written on the board above the ethernet port. Afterwards, you should connect the Red Pitaya via ethernet to a router that has internet access. There are ways to set up linien on the Red Pitaya without internet, but they're much more painful.

If the Red Pitaya has internet access: In your terminal running the virtual environment, run 
```bash
python
```

to create a Python screen and run the following two lines.
```python
from linien.gui.app import run_application
run_application()
```

This will bring up the GUI. You can click the "New device" button and add your device's hostname in the instructed box. Once added, click on the hostname that corresponds to your Red Pitaya in the main window. This will automatically connect to the Red Pitaya and prompt you to install the server. Click "yes" and wait for the install to finish/the GUI to appear. Close the GUI. We now need to modify this install with our custom files for relock.

Now, we need to establish secure communication between our computer and the Red Pitaya running linien. We do this by generating an SSH keypair. Run the following command in a Command Prompt:
```bash
ssh-keygen
```
Hit Enter when prompted for inputs. This will generate two files. Take note of the one with extension "id_rsa.pub"
```makefile
C:\Users\<you>\.ssh\id_rsa
C:\Users\<you>\.ssh\id_rsa.pub
```
Copy the RSA public key from your computer to the Red Pitaya using the command (replacing <you> with the correct path)
```bash
scp C:\Users\<you>\.ssh\id_rsa.pub root@<RP_IP>:/root/authorized_keys_tmp
```
Then SSH into the Red Pitaya:
```bash
ssh root@rp-XXXXXX.local
```
Once inside the Red Pitaya, run the following commands to register your computer's RSA key
```bash
mkdir -p ~/.ssh
cat authorized_keys_tmp >> ~/.ssh/authorized_keys
rm authorized_keys_tmp
chmod 600 ~/.ssh/authorized_keys
```
You can exit the Red Pitaya (run *exit* in the ssh window). You can now set up the script to copy the new server files over. Find the file in the linien-relock folder called *install_relock_server.bat* and locate line 12. It should say 
```bash
set RP_IP=rp-XXXXXX.local 
```

Modify this with your Red Pitaya host name. Then, in your Command Prompt run the install file by calling
```bash
install_relock_server.bat
```

This completes your installation of linien-relock on both your computer and the Red Pitaya

Using linien-relock
---------------

### 1. Running linien-relock:

Because we are now using virtual environments, running the GUI will require first activating the appropriate virtual environment. On **Mac OS** run
```bash
source linienvenv/bin/activate
```

On **Windows** run
```bash
linienvenv\Scripts\activate.bat
```

Afterwards, the instructions are the same. Inside this virtual environment, create a python environment
```bash
python
```
And run the following two commands to bring up the GUI. 
```python
from linien.gui.app import run_application
run_application()
```

### 2. Modifying linien-relock:
If you are modifying files on your own computer, you can just run *install_linien.sh* on Mac OS and *install_linien.bat* on Windows to apply your changes.

If you are modifying files on the Red Pitaya, you will have to reboot the Red Pitaya in order for the changes to take affect. You can do this by SSH-ing into the Red Pitaya and running 
```bash
reboot
```

Tips and Tricks
---------------
The original linien 0.3.2 is a bit of a frankensteined package due to its age - some of the code packages and even some of the Python releases it uses are no longer supported by PyPI and/or modern hardware. Linien-relock tries to fix some of these problems, but it is also a series of solutions rather than a new package built from first-principles. As such, it's not inconceivable that users will find themselves needing to debug dependency problems if they make minor modifications to the code. 

At a high level, linien-relock (and linien) works in the following manner. Signals come into the Red Pitaya and are processed on the FPGA. The Python server on the Red Pitaya occasionally samples the FPGA and, based on what it sees, performs some sort of logic action. Certain parameters that the server interacts with (e.g. the Analog In 1 signal) are exposed over a network connection that your computer can read using it's own Python client. The GUI then visually formats this information into something that you can click and drag. Server-side errors will thus be displayed on the Red Pitaya and client-side errors will be displayed on your computer. 

It is recommended to first debug client-side errors, which you can do by monitoring the terminal in which you ran 
```python
from linien.gui.app import run_application
run_application()
```

Once client-side errors are addressed, you can look at server-side errors. First, connect to the Red Pitaya using the GUI. Subsequently, open another terminal window and SSH into the Red Pitaya. Run the command 
```bash
screen -ls
```

If you see something like "XXXX.spectrolockserver" then the client has connected to the Red Pitaya and started the server. You can see what the server is doing by running the command:
```bash
screen -r
```

Any problems with server-side code will be reflected in error messages in this screen. You can exit this screen by using *Ctrl + A + D*. 


Uninstalling
---------------
If you ever want to uninstall linien relock, the way to do so is quite simple. Just delete the virtual environment folder ("linienvenv") and the linien-relock folder. Since everything was installed inside the virtual environment, this won't leave anything behind on your computer.