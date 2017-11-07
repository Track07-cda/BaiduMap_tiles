#!/usr/bin/python

import urllib2
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
    
    print "x range", start_x, stop_x
    print "y range", start_y, stop_y
    
    for x in xrange(start_x, stop_x):
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
        for y in xrange(self.start_y, self.stop_y):
            if satellite:
                download_satellite(self.x, y, self.zoom)
                download_tile(self.x, y, self.zoom, True)
            else:
                download_tile(self.x, y, self.zoom)


def download_tile(x, y, zoom, satellite=False):
    url = None
    filename = None
    folder = "tile/"
    # styles is roadmap when downloading satellite
    styles = "sl" if satellite else "pl"

    query = "qt=tile&x=%d&y=%d&z=%d&styles=%s&scaler=1&udt=20170927" % (x, y, zoom, styles)
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
            req = urllib2.Request(url, data=None)
            response = urllib2.urlopen(req)
            bytes = response.read()
        except Exception, e:
            print "--", filename, "->", e
            sys.exit(1)
        
        if bytes.startswith("<html>"):
            print "-- forbidden", filename
            sys.exit(1)
        
        print "-- saving " + filename
        
        f = open(full_file_path, 'wb')
        f.write(bytes)
        f.close()
        
        time.sleep(1 + random.random())
    else:
        print "-- existed " + filename
            

if __name__ == "__main__":
    
    zoom = 8
 
    lat_start, lon_start = 31.717714,105.540665
    lat_stop, lon_stop = 39.659668,111.262224

    satellite = False
	
    download_tiles(zoom, lat_start, lat_stop, lon_start, lon_stop, satellite)
