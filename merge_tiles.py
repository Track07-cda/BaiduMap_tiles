import os
import sys

from PIL import Image

from gmap_utils import *


def merge_tiles(zoom, lat_start, lat_stop, lon_start, lon_stop, satellite=True):
    
    TYPE, ext = 'r', 'png'
    if satellite:
        TYPE, ext = 's', 'jpg'
    
    x_start, y_start = bd_latlng2xy(zoom, lat_start, lon_start)
    x_stop, y_stop = bd_latlng2xy(zoom, lat_stop, lon_stop)
    x_start = int(x_start/256)
    y_start = int(y_start/256)
    x_stop = int(x_stop/256)
    y_stop = int(y_stop/256)
    print("x range", x_start, x_stop)
    print("y range", y_start, y_stop)
    
    w = (x_stop - x_start) * 256
    h = (y_stop - y_start) * 256
    
    print("width:", w)
    print("height:", h)
    
    result = Image.new("RGBA", (w, h))
    
    for x in range(x_start, x_stop):
        for y in range(y_start, y_stop):
            
            filename = "%d_%d_%d_%s.%s" % (zoom, x, y, TYPE, ext)
            
            if not os.path.exists(filename):
                print("-- missing", filename)
                continue
                    
            x_paste = (x - x_start) * 256
            y_paste = (y_stop - y) * 256
            
            try:
                i = Image.open(filename)
            except Exception as e:
                print("-- %s, removing %s" % (e, filename))
                trash_dst = os.path.expanduser("~/.Trash/%s" % filename)
                os.rename(filename, trash_dst)
                continue
            
            result.paste(i, (x_paste, y_paste))
            
            del i
    
    result.save("map_%s.%s" % (TYPE, ext))

if __name__ == "__main__":
    
    zoom = 19
 
    lat_start, lon_start = 31.022547,121.429391
    lat_stop, lon_stop = 31.041453,121.45749
    
    merge_tiles(zoom, lat_start, lat_stop, lon_start, lon_stop, satellite=False)
