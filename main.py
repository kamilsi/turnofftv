#!/usr/bin/env python3
"""
This script turns off your webOS-based TV at night for you.
https://github.com/kamilsi/turnofftv/blob/main/readme.md
"""

__author__ = "Kamil Sijko"
__version__ = "0.1.0"
__license__ = "MIT"

from pywebostv.discovery import * 
from pywebostv.connection import *
from pywebostv.controls import *
import os 
import pickle
import time
import subprocess
import logging

logging.basicConfig(filename='turnoff_TV.log', encoding='utf-8',
 level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def startup():
    """ Check for API key and load or print prompt """
    if os.path.exists("store.pkl"):
        with open('store.pkl', 'rb') as f:
            store = pickle.load(f)
    else:
        print("First run, TV has to be turned on.")
        store = {}
        store["ip"] = input('What is the IP of the TV?')
        client = WebOSClient(store["ip"])
        client.connect()
        for status in client.register(store):
            if status == WebOSClient.PROMPTED:
                print("Please accept the connect on the TV!")
                with open('store.pkl', 'wb') as f:
                    pickle.dump(store, f)     
            elif status == WebOSClient.REGISTERED:
                raise RuntimeError("Unexpected registration")

    return store

def main(store):
    p = subprocess.Popen(["ping", store["ip"], "-c", "1"], stdout=subprocess.PIPE)
    p.wait()
    if p.poll() == 0:
        logging.info("TV is on.")
        client = WebOSClient(store["ip"])
        client.connect()
        for status in client.register(store):
            if status == WebOSClient.PROMPTED:
                raise RuntimeError("API key seems to be off, please delete it.")
            elif status == WebOSClient.REGISTERED:
                logging.debug("Registration successful!")
        system = SystemControl(client)
        system.notify("TV will be turned off in 15 seconds")
        logging.info("Notified.")
        time.sleep(15)
        system.power_off()
        logging.info("Turned off TV.")
        time.sleep(60)
    else:
        time.sleep(60)

if __name__ == "__main__":
    """ This is executed when ruśn from the command line """
    logging.info("Started")
    store = startup()
    while True:
        main(store)