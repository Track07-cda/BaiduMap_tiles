# http://oregonarc.com/2011/02/command-line-tile-cutter-for-google-maps-improved/
# http://media.oregonarc.com/fish/tile.py

import math
import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import json
import time
import random

akey = 'uzIatbtHgfCTr71dWxnHolfZqG6vARNc'

def latlon2px(z,lat,lon):
    x = 2**z*(lon+180)/360*256
    y = -(.5*math.log((1+math.sin(math.radians(lat)))/(1-math.sin(math.radians(lat))))/math.pi-1)*256*2**(z-1)
    return x,y

def latlon2xy(z,lat,lon):
    x,y = latlon2px(z,lat,lon)
    x = int(x/256)#,int(x%256)
    y = int(y/256)#,int(y%256)
    return x,y

def bd_latlng2xy(z,lat,lng,max_retries=3,retry_delay=2):
    """
    Convert Baidu Map latitude and longitude to x, y coordinates
    
    Args:
        z: zoom level
        lat: latitude
        lng: longitude
        max_retries: maximum number of retry attempts
        retry_delay: base delay between retries in seconds
        
    Returns:
        Tuple (x, y) of coordinates
    """
    url='http://api.map.baidu.com/geoconv/v1/?'
    args = {'coords':str(lng)+','+str(lat),
            'from':5,
            'to':6,
            'output':'json',
            'ak':akey}
    data = urllib.parse.urlencode(args)
    
    retry_count = 0
    while retry_count < max_retries:
        try:
            response = urllib.request.urlopen(url+data)
            result = response.read()
            result = json.loads(result)
            
            # Check if the API returned an error
            if result.get("status") != 0:
                retry_count += 1
                print(f"API error: {result}, attempt {retry_count}/{max_retries}")
                if retry_count >= max_retries:
                    raise Exception(f"API error after {max_retries} attempts: {result}")
                time.sleep(retry_delay * retry_count + random.random())
                continue
                
            loc = result["result"][0]
            res = 2**(18-z)
            x = loc['x']/res
            y = loc['y']/res
            return x,y
            
        except Exception as e:
            retry_count += 1
            if retry_count >= max_retries:
                print(f"Failed after {max_retries} attempts: {e}")
                raise
            print(f"Error in bd_latlng2xy: {e}, retrying {retry_count}/{max_retries}...")
            time.sleep(retry_delay * retry_count + random.random())

if __name__ == "__main__":
    z=19
    lat=31.025819
    lng=121.434229
    x,y = bd_latlng2xy(z,lat,lng)
    print(x//256)
    print(y//256) # only right when lat>0 lng>0