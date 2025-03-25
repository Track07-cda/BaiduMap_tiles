# BaiduMap tiles

## Getting Started

### Environment Setup

This project requires a Baidu Maps API key. Create a `.env` file in the root directory with your API key:

```
BAIDU_API_KEY=your_api_key_here
```

You can copy the provided `.env.example` file and replace the placeholder with your actual API key:

```bash
cp .env.example .env
# Edit the .env file to add your API key
```

### Installation

Install the required dependencies:

```bash
pip install -r requirements.txt
```

### Download Baidu Maps tiles

Edit `download_tiles.py` to specify the area, zoom levels, and whether you want satellite or road maps:

```py
zoom_levels = list(range(8, 18))  # Download tiles for zoom levels 8 through 17

lat_start, lon_start = 30.763961, 119.926525
lat_stop, lon_stop = 32.053984, 121.408616

satellite = False    # Set to True for satellite images, False for road maps

download_tiles(zoom_levels, lat_start, lat_stop, lon_start, lon_stop, satellite)
```

You can easily find Baidu coordinates with [http://api.map.baidu.com/lbsapi/getpoint/](http://api.map.baidu.com/lbsapi/getpoint/).

Then, run `$ python download_tiles.py` and get individual tiles in `tile` folder.

The script now supports:
- Downloading multiple zoom levels in a single run
- Automatic retries for failed downloads (up to 3 times by default)
- Progress tracking with failed download counts
- Parallel downloading using threads

### Merge Baidu Maps tiles

Edit `merge_tiles.py` to specify the area and zoom level for the tiles you want to merge:

```py
zoom = 19
 
lat_start, lon_start = 31.022547,121.429391
lat_stop, lon_stop = 31.041453,121.45749

satellite = True    # Set to False for road maps
```

Then, run `$ python merge_tiles.py` and get `map_s.jpg` for satellite or `map_r.png` for road maps.

Note: merging the tiles requires [Python Image Library (PIL)](https://python-pillow.org/).

## Reference

- <http://api.map.baidu.com/lbsapi/getpoint/>
- <http://developer.baidu.com/map/jsdemo.htm#a1_2>
- <http://developer.baidu.com/map/reference/index.php>
- <http://lbsyun.baidu.com/index.php?title=jspopular>