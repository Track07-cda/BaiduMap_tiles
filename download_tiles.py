#!/usr/bin/python
"""
Baidu Map Tile Downloader

This script downloads map tiles from Baidu Maps for the specified geographic area
and zoom levels. It can download both satellite imagery, road maps, and vector tiles.
"""

import os
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from queue import Empty, Queue
from threading import Lock

from gmap_utils import *

failed_downloads = 0
failed_lock = Lock()
download_count = 0
download_lock = Lock()
progress_lock = Lock()

# Default number of worker threads
NUM_THREADS = 8

def download_tiles(zoom_levels, lat_start, lat_stop, lon_start, lon_stop, 
                  satellite=True, vector=False):
    """
    Download Baidu Map tiles for specified geographic area and zoom levels.
    
    Args:
        zoom_levels (list): List of zoom levels to download
        lat_start (float): Starting latitude (southern boundary)
        lat_stop (float): Ending latitude (northern boundary)
        lon_start (float): Starting longitude (western boundary)
        lon_stop (float): Ending longitude (eastern boundary)
        satellite (bool): If True, download satellite imagery; otherwise download road maps
        vector (bool): If True, download vector tiles instead of raster tiles
        
    Returns:
        None
    """
    global download_count, failed_downloads
    total_download_count = 0
    total_failed_downloads = 0
    
    # Vector and satellite modes are mutually exclusive
    if vector and satellite:
        print("Warning: Both vector and satellite modes selected. Defaulting to vector mode.")
        satellite = False
    
    for zoom in zoom_levels:
        # Reset counters for this zoom level
        download_count = 0
        failed_downloads = 0
        
        print(f"\n===== Downloading tiles for zoom level {zoom} =====")
        start_x, start_y = bd_latlng2xy(zoom, lat_start, lon_start)
        stop_x, stop_y = bd_latlng2xy(zoom, lat_stop, lon_stop)
        
        start_x = int(start_x//256)
        start_y = int(start_y//256)
        stop_x = int(stop_x//256) + 1
        stop_y = int(stop_y//256) + 1
        
        print("x range", start_x, stop_x)
        print("y range", start_y, stop_y)
        
        total_tiles = (stop_x - start_x) * (stop_y - start_y)
        if satellite:
            total_tiles *= 2  # For satellite we download both satellite and road overlay tiles
        
        print(f"Total tiles to download for zoom level {zoom}: {total_tiles}")
        print(f"Mode: {'Vector' if vector else 'Satellite' if satellite else 'Road map'}")
        
        # Create a queue of download tasks
        download_queue = Queue()
        
        # Add all download tasks to the queue
        for x in range(start_x, stop_x):
            for y in range(start_y, stop_y):
                if satellite:
                    # For satellite mode, download both satellite and road overlay
                    download_queue.put((x, y, zoom, False, True, False))  # Satellite tile
                    download_queue.put((x, y, zoom, True, True, False))   # Road overlay tile
                else:
                    # For road map or vector tile
                    download_queue.put((x, y, zoom, False, False, vector))
        
        # Use ThreadPoolExecutor to manage worker threads
        with ThreadPoolExecutor(max_workers=NUM_THREADS) as executor:
            # Start worker threads
            future_to_worker = {
                executor.submit(worker_thread, download_queue, total_tiles): i 
                for i in range(NUM_THREADS)
            }
            
            # Wait for all workers to complete
            for future in future_to_worker:
                try:
                    future.result()
                except Exception as exc:
                    print(f'Worker generated an exception: {exc}')
        
        print(f"===== Download Complete for zoom level {zoom} =====")
        print(f"Downloaded {download_count} tiles, Failed: {failed_downloads}")
        
        # Add to total counts
        total_download_count += download_count
        total_failed_downloads += failed_downloads
    
    print("\n===== All zoom levels download complete =====")
    print(f"Total tiles downloaded: {total_download_count}")
    print(f"Total failed downloads: {total_failed_downloads}")
    print("=============================================")


def worker_thread(download_queue, total_tiles):
    """
    Worker thread function that processes download tasks from the queue.
    
    Args:
        download_queue (Queue): Queue containing download tasks
        total_tiles (int): Total number of tiles to be downloaded
        
    Returns:
        None
    """
    while True:
        try:
            # Get a task from the queue with a timeout
            x, y, zoom, is_overlay, is_satellite, is_vector = download_queue.get(timeout=1)
            
            # Download the tile
            if is_satellite and not is_overlay:
                # This is a satellite image
                success = download_satellite(x, y, zoom)
            else:
                # This is a road map, road overlay, or vector tile
                success = download_tile(x, y, zoom, is_overlay, is_vector)
            
            # Report progress
            global download_count
            if success:
                with download_lock:
                    download_count += 1
                    current_count = download_count
                
                if current_count % NUM_THREADS == 0:
                    with progress_lock:
                        progress = min(100.0, (current_count / total_tiles) * 100)
                        print(f"Progress: {progress:.1f}% ({current_count}/{total_tiles})")
            
            # Mark task as done
            download_queue.task_done()
            
        except Empty:
            # Queue is empty, exit the thread
            break
        except Exception as e:
            # Handle other exceptions
            print(f"Worker thread error: {e}")
            break


def download_tile(x, y, zoom, satellite=False, vector=False):
    """
    Download a road map tile or vector tile.
    
    Args:
        x (int): Tile x-coordinate
        y (int): Tile y-coordinate
        zoom (int): Zoom level
        satellite (bool): If True, use special road overlay styling for satellite view
        vector (bool): If True, download vector tile instead of raster tile
        
    Returns:
        bool: True if download was successful, False otherwise
    """
    url = None
    filename = None
    
    if vector:
        folder = "vector/"
        # For vector tiles, use qt=vtile instead of qt=tile
        query = "qt=vtile&x=%d&y=%d&z=%d&styles=pl&scaler=1&udt=" % (x, y, zoom)
        url = "http://online0.map.bdimg.com/tile/?" + query
        filename = query + ".png"
    else:
        folder = "road/" if satellite else "tile/"
        scaler = "" if satellite else "&scaler=1"
        # styles is roadmap when downloading satellite
        styles = "sl" if satellite else "pl"
        query = "qt=tile&x=%d&y=%d&z=%d&styles=%s%s&udt=20250312" % (x, y, zoom, styles, scaler)
        url = "http://online0.map.bdimg.com/onlinelabel/?" + query
        filename = query + ".png"

    return download_file(url, filename, folder)


def download_satellite(x, y, zoom):
    """
    Download a satellite imagery tile.
    
    Args:
        x (int): Tile x-coordinate
        y (int): Tile y-coordinate
        zoom (int): Zoom level
        
    Returns:
        bool: True if download was successful, False otherwise
    """
    url = None
    filename = None
    folder = "it/"

    path = "u=x=%d;y=%d;z=%d;v=009;type=sate&fm=46&udt=20250312" % (x, y, zoom)
    url = "http://shangetu0.map.bdimg.com/it/" + path
    filename = path.replace(";", ",") + ".jpg"

    return download_file(url, filename, folder)


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
        # File already exists, consider it a successful download
        return True
    
    retry_count = 0
    global failed_downloads
    while retry_count < max_retries:
        try:
            req = urllib.request.Request(url, data=None)
            response = urllib.request.urlopen(req)
            bytes_data = response.read()
            
            if bytes_data.startswith(b"<html>"):
                retry_count += 1
                if retry_count >= max_retries:
                    with failed_lock:
                        failed_downloads += 1
                    return False
                time.sleep(retry_delay + random.random())
                continue
            
            f = open(full_file_path, 'wb')
            f.write(bytes_data)
            f.close()
            
            # Small delay to avoid overwhelming the server
            time.sleep(0.1 + random.random() * 0.2)
            return True
            
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                with failed_lock:
                    failed_downloads += 1
                return False
            else:
                time.sleep(retry_delay * retry_count + random.random())
            

if __name__ == "__main__":
    # Example configuration
    zoom_levels = list(range(8, 18))

    lon_start, lat_start = 119.926525, 30.763961
    lon_stop, lat_stop = 121.408616, 32.053984
    if lon_start > lon_stop:
        lon_start, lon_stop = lon_stop, lon_start

    if lat_start > lat_stop:
        lat_start, lat_stop = lat_stop, lat_start
    
    satellite = False
    vector = True  # Set to True to download vector tiles
    
    download_tiles(zoom_levels, lat_start, lat_stop, lon_start, lon_stop, satellite, vector)