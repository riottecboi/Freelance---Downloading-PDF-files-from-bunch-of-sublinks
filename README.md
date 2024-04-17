# Automation Python Script to download PDF from the site

In this project, I used Selenium to visit and download PDF files to a local machine 

## Installation

This project running on Python 3.11, so please be sure that you are install Python 3.11 on your machine

````bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update 
sudo apt install python3.11
`````

Use the package manager [pip](https://pip.pypa.io/en/stable/)

````bash
sudo apt-get install python3-pip
`````

to install packages.

```bash
python3.11 -m pip install -r requirements.txt 
```

## Usage
Replace the username/password inside `main.py` by any prefered text editor

````python
username = 'xxxx'
password = 'xxxx'
```````

save a file and running a file

```bash
python3.11 main.py
```

## Demo

Screenshots and video demo are stored at 
- `demo/screenshots` 
- `demo/video`

Outputs for an available links also stored as two files 

- `sublinks.txt`
- `sublinks_max_3_segments.txt`
