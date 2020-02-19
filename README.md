# Raman_Processing
Scripts in Python using multi processing to process Raman infrared data

## Needed Packages
### Default with Python 3.7 on every Anaconda new virtual environment
* python 3.x
* sqlite3                
* io             
* multiprocessing
* pathlib        
* time 
### Packages to install
* numpy
* matplotlib
* scipy
* obspy

The packages listed above may also be installed from Anaconda.
Anaconda® is a package manager, an environment manager and a collection of over 7,500+ open-source packages. Anaconda is free and easy to install.

It's a good practice to create a new virtual environment with Anaconda for every new project.

See [here](https://www.anaconda.com/distribution/) to download Anaconda. And [here](https://problemsolvingwithpython.com/01-Orientation/01.05-Installing-Anaconda-on-Linux/) to how to install on Linux.


Once Anaconda is installed, we close and reopen the terminal. Then we can create our environment with a specific version of Python executing in terminal the command:

``` [bash]
conda create -n envName python=3.7
``` 
Change envName with the name you want for your new environment. For this guideline we will use envName = raman. For example:
``` [bash]
conda create -n raman python=3.7
```

When conda asks you to proceed, type y.

Then activate the environment with:
``` [bash]
conda activate raman
```
Now that we've activated the environment, we'll install the needed packages with the command:
``` [bash]
conda install <package name>
```
i.e.
``` [bash]
conda install scipy
```
To install obspy:
```[bash]
conda install -c conda-forge obspy
```
When conda asks you to proceed, type y.

Fortunately, in order to install obspy, conda will install numpy, matplotlib and scipy.

## Data
The data used in this project is taken from the RRUFF™ project, and it can be found [here.](https://mega.nz/#!qnxDjJTQ!VX5XTlIOa-v-WYA58cEdWHJ7jJo5veWfCMgAtzbVpjI)

The files taken from the [RRUFF project](https://rruff.info/) were converted to a .db file in order to be easier to work with in Python.
The script to transform the .txt files from RRUFF to a database file can be found [here.](https://mega.nz/#!7ip1CTII!JRqj3PvkAlISpwcmNoAFp_dnZucFP2IGwLdY1eUfQC0)

However, if the user wants to work with a different set of spectral data, all the files from RRUFF can be found [here.](https://rruff.info/zipped_data_files/)

In order to execute any of the scripts (polinomial.py, Savitzky_Golay.py or airPLS.py) we need a specific arrange of directories. 

Firstly, we need to add to our main directory (~/anaconda3/envs/raman) the following files:

1. [polinomial.py](https://github.com/victoralexander132/Raman_Processing/blob/master/polinomial.py)
2. [Savitzky_Golay.py](https://github.com/victoralexander132/Raman_Processing/blob/master/Savitzky_Golay.py)
3. [airPLS_.py](https://github.com/victoralexander132/Raman_Processing/blob/master/airPLS.py)
4. [Funcion.py](https://github.com/victoralexander132/Raman_Processing/blob/master/Funcion.py)
5. [RRUFF.db](https://mega.nz/#!qnxDjJTQ!VX5XTlIOa-v-WYA58cEdWHJ7jJo5veWfCMgAtzbVpjI)

and two additional directories, one for the data (Datos) that is going to be analyzed and another one for the output of the scripts (Images).

the directory structure can be created by typing in terminal the commands:
```[bash]
cd ~/anaconda3/envs/raman
mkdir Datos Images
cd Images
mkdir airPLS polynomial SG
```
Secondly, open a terminal and type:
```[bash]
cd ~/anaconda3/envs/raman
conda activate raman
python airPLS.py
```
a selection file windows will appear, select the file that you want analyze, click open and wait to the script to finish.

After that, the image can be found on the Images/airPLS/ folder

Files to test the scripts can be found [here.](https://mega.nz/#F!rrh3Gb5R!RV2J0dlhSLk4djACNgS5eQ)
