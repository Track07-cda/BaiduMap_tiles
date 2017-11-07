# BaiduMap tiles

## Getting Started

### Download Baidu Maps tiles

Edit `download_tiles.py` to specify the area and the zoom level you want.

```py
zoom = 8

lat_start, lon_start = 31.717714,105.540665
lat_stop, lon_stop = 39.659668,111.262224

satellite = True    # roads if false

download_tiles(zoom, lat_start, lat_stop, lon_start, lon_stop, satellite)
```

You can easily find Baidu coordinates with [http://api.map.baidu.com/lbsapi/getpoint/](http://api.map.baidu.com/lbsapi/getpoint/).

Then, run `$ python download_tiles.py` and get individual tiles in `tile` folder.

### Merge Baidu Maps tiles

Edit `merge_tiles.py` to specify the area and the zoom level you want, it's just the same as before.

    zoom = 19
 
    lat_start, lon_start = 31.022547,121.429391
    lat_stop, lon_stop = 31.041453,121.45749

    satellite = True    # roads if false

Then, run `$ python merge_tiles.py` and get `map_s.jpg` for satellite or `map_r.png` for roads.


Note: merging the tiles requires [Python Image Library](http://www.pythonware.com/products/pil/).

## Reference

- <http://api.map.baidu.com/lbsapi/getpoint/>
- <http://developer.baidu.com/map/jsdemo.htm#a1_2>
- <http://developer.baidu.com/map/reference/index.php>
- <http://lbsyun.baidu.com/index.php?title=jspopular>
