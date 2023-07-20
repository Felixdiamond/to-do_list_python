import os
import subprocess
import time

def install_postgres():
    os.system('sudo sh -c \'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list\'')
    time.sleep(1)
    try:
        subprocess.check_call(['wget', '--quiet', '-O', '-', 'https://www.postgresql.org/media/keys/ACCC4CF8.asc'], stdout=subprocess.PIPE)
        time.sleep(1)
    except subprocess.CalledProcessError:
        os.system('sudo apt-get install wget')
        time.sleep(1)
        subprocess.check_call(['wget', '--quiet', '-O', '-', 'https://www.postgresql.org/media/keys/ACCC4CF8.asc'], stdout=subprocess.PIPE)
        time.sleep(1)
    os.system('sudo apt-key add -')
    os.system('sudo apt-get update')
    time.sleep(1)
    os.system('sudo apt-get install postgresql')
    time.sleep(3)
    os.system('sudo service postgresql start')
    time.sleep(3)
    os.system('sudo -i -u postgres')
    time.sleep(1)
    os.system('psql')
    time.sleep(1)
    os.system('CREATE DATABASE IF NOT EXISTS to_do_db;')
    time.sleep(1)
    os.system('\\q')
    time.sleep(1)
    os.system('exit')
    time.sleep(1)
    os.system('clear')