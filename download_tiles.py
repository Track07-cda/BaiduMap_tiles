#!/usr/bin/python

import urllib.request, urllib.error, urllib.parse
from threading import Thread
import os, sys
import math
from gmap_utils import *

import time
import random

def download_tiles(zoom, lat_start, lat_stop, lon_start, lon_stop, satellite=True):

    start_x, start_y = bd_latlng2xy(zoom, lat_start, lon_start)
    stop_x, stop_y = bd_latlng2xy(zoom, lat_stop, lon_stop)
    
    start_x = int(start_x//256)
    start_y = int(start_y//256)
    stop_x = int(stop_x//256)
    stop_y = int(stop_y//256)
    
    print("x range", start_x, stop_x)
    print("y range", start_y, stop_y)
    
    for x in range(start_x, stop_x):
        # download(x, y, zoom)
        FastThread(x, start_y, stop_y, zoom, satellite).start()


class FastThread(Thread):
    def __init__(self, x, start_y, stop_y, zoom, satellite):
        super(FastThread, self).__init__()
        self.x = x
        self.start_y = start_y
        self.stop_y = stop_y
        self.zoom = zoom
        self.satellite = satellite
    
    def run(self):
        for y in range(self.start_y, self.stop_y):
            if satellite:
                download_satellite(self.x, y, self.zoom)
                download_tile(self.x, y, self.zoom, True)
            else:
                download_tile(self.x, y, self.zoom)


def download_tile(x, y, zoom, satellite=False):
    url = None
    filename = None
    folder = "road/" if satellite else "tile/"
    scaler = "" if satellite else "&scaler=1"
    # styles is roadmap when downloading satellite
    styles = "sl" if satellite else "pl"

    query = "qt=tile&x=%d&y=%d&z=%d&styles=%s%s&udt=20170927" % (x, y, zoom, styles, scaler)
    url = "http://online0.map.bdimg.com/onlinelabel/?" + query
    filename = query + ".png"

    download_file(url, filename, folder)


def download_satellite(x, y, zoom):
    url = None
    filename = None
    folder = "it/"

    path = "u=x=%d;y=%d;z=%d;v=009;type=sate&fm=46&udt=20170927" % (x, y, zoom)
    url = "http://shangetu0.map.bdimg.com/it/" + path
    filename = path.replace(";", ",") + ".jpg"

    download_file(url, filename, folder)


def download_file(url, filename, folder=""):
    full_file_path = folder + filename
    if not os.path.exists(full_file_path):
        bytes = None
        try:
            req = urllib.request.Request(url, data=None)
            response = urllib.request.urlopen(req)
            bytes = response.read()
        except Exception as e:
            print("--", filename, "->", e)
            sys.exit(1)
        
        if bytes.startswith(b"<html>"):
            print("-- forbidden", filename)
            sys.exit(1)
        
        print("-- saving " + filename)
        
        f = open(full_file_path, 'wb')
        f.write(bytes)
        f.close()
        
        time.sleep(1 + random.random())
    else:
        print("-- existed " + filename)
            

if __name__ == "__main__":
    
    zoom = 19
 
    lat_start, lon_start = 34.233188,108.91931,
    lat_stop, lon_stop = 34.241843,108.928293,

    satellite = True
	
    download_tiles(zoom, lat_start, lat_stop, lon_start, lon_stop, satellite)
