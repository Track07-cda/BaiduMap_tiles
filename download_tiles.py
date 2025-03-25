#!/usr/bin/python
"""
Baidu Map Tile Downloader

This script downloads map tiles from Baidu Maps for the specified geographic area
and zoom levels. It can download both satellite imagery and road maps.
"""

import urllib.request, urllib.error, urllib.parse
from threading import Thread, Lock
import os
from gmap_utils import *

import time
import random

failed_downloads = 0
failed_lock = Lock()

all_threads = []

def download_tiles(zoom_levels, lat_start, lat_stop, lon_start, lon_stop, satellite=True):
    """
    Download Baidu Map tiles for specified geographic area and zoom levels.
    
    Args:
        zoom_levels (list): List of zoom levels to download
        lat_start (float): Starting latitude (southern boundary)
        lat_stop (float): Ending latitude (northern boundary)
        lon_start (float): Starting longitude (western boundary)
        lon_stop (float): Ending longitude (eastern boundary)
        satellite (bool): If True, download satellite imagery; otherwise download road maps
        
    Returns:
        None
    """
    for zoom in zoom_levels:
        print(f"\n===== Downloading tiles for zoom level {zoom} =====")
        start_x, start_y = bd_latlng2xy(zoom, lat_start, lon_start)
        stop_x, stop_y = bd_latlng2xy(zoom, lat_stop, lon_stop)
        
        start_x = int(start_x//256)
        start_y = int(start_y//256)
        stop_x = int(stop_x//256)
        stop_y = int(stop_y//256)
        
        print("x range", start_x, stop_x)
        print("y range", start_y, stop_y)
        
        all_threads.clear()
        
        for x in range(start_x, stop_x):
            thread = FastThread(x, start_y, stop_y, zoom, satellite)
            all_threads.append(thread)
            thread.start()
        
        for thread in all_threads:
            thread.join()
        
        print(f"===== Download Complete for zoom level {zoom} =====")
    
    print("\n===== All zoom levels download complete =====")
    global failed_downloads
    if failed_downloads > 0:
        print(f"Total failed downloads: {failed_downloads}")
        print("=============================================")


class FastThread(Thread):
    """
    Thread class for parallel downloading of map tiles.
    
    Each thread downloads all tiles for a specific x-coordinate range.
    """
    def __init__(self, x, start_y, stop_y, zoom, satellite):
        """
        Initialize the download thread.
        
        Args:
            x (int): The x-coordinate for this thread to download
            start_y (int): The starting y-coordinate
            stop_y (int): The ending y-coordinate
            zoom (int): The zoom level
            satellite (bool): If True, download satellite imagery; otherwise download road maps
        """
        super(FastThread, self).__init__()
        self.x = x
        self.start_y = start_y
        self.stop_y = stop_y
        self.zoom = zoom
        self.satellite = satellite
    
    def run(self):
        """
        Execute the thread's download tasks.
        
        For each y-coordinate in the range, download the appropriate tile.
        For satellite mode, download both satellite and road tiles.
        """
        for y in range(self.start_y, self.stop_y):
            if self.satellite:
                download_satellite(self.x, y, self.zoom)
                download_tile(self.x, y, self.zoom, True)
            else:
                download_tile(self.x, y, self.zoom)


def download_tile(x, y, zoom, satellite=False):
    """
    Download a road map tile.
    
    Args:
        x (int): Tile x-coordinate
        y (int): Tile y-coordinate
        zoom (int): Zoom level
        satellite (bool): If True, use special road overlay styling for satellite view
        
    Returns:
        None
    """
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
    """
    Download a satellite imagery tile.
    
    Args:
        x (int): Tile x-coordinate
        y (int): Tile y-coordinate
        zoom (int): Zoom level
        
    Returns:
        None
    """
    url = None
    filename = None
    folder = "it/"

    path = "u=x=%d;y=%d;z=%d;v=009;type=sate&fm=46&udt=20170927" % (x, y, zoom)
    url = "http://shangetu0.map.bdimg.com/it/" + path
    filename = path.replace(";", ",") + ".jpg"

    download_file(url, filename, folder)


def download_file(url, filename, folder="", max_retries=3, retry_delay=2):
    """
    Download a file from a URL and save it to the specified path.
    
    Args:
        url (str): The URL to download from
        filename (str): The filename to save as
        folder (str): The folder to save to (will be created if it doesn't exist)
        max_retries (int): Maximum number of retry attempts
        retry_delay (int): Base delay between retries in seconds
        
    Returns:
        bool: True if download was successful, False otherwise
    """
    if folder and not os.path.exists(folder):
        os.makedirs(folder)
        
    full_file_path = folder + filename
    if os.path.exists(full_file_path):
        print("-- existed " + filename)
        return True
    
    retry_count = 0
    global failed_downloads
    while retry_count < max_retries:
        try:
            req = urllib.request.Request(url, data=None)
            response = urllib.request.urlopen(req)
            bytes_data = response.read()
            
            if bytes_data.startswith(b"<html>"):
                print(f"-- forbidden {filename}, retry {retry_count+1}/{max_retries}")
                retry_count += 1
                if retry_count >= max_retries:
                    with failed_lock:
                        failed_downloads += 1
                    print(f"-- giving up on {filename} after {max_retries} attempts")
                    return False
                time.sleep(retry_delay + random.random())
                continue
            
            print("-- saving " + filename)
            
            f = open(full_file_path, 'wb')
            f.write(bytes_data)
            f.close()
            
            time.sleep(1 + random.random())
            return True
            
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                with failed_lock:
                    failed_downloads += 1
                print(f"-- failed to download {filename} after {max_retries} attempts: {e}")
                return False
            else:
                print(f"-- {filename} -> {e}, retrying {retry_count}/{max_retries}...")
                time.sleep(retry_delay * retry_count + random.random())

            

if __name__ == "__main__":
    # Example configuration
    zoom_levels = list(range(8, 18))
 
    lat_start, lon_start = 30.763961, 119.926525
    lat_stop, lon_stop = 32.053984, 121.408616
    
    satellite = False
    
    download_tiles(zoom_levels, lat_start, lat_stop, lon_start, lon_stop, satellite)