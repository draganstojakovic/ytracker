## yTracker

---

I hold no responsibility if you break your computer while using this program.

### Install

Install using pip:

```
git clone https://github.com/draganstojakovic/ytracker.git
cd ytracker
pip install -e .
```

or,

install using pipx:

```
git clone https://github.com/draganstojakovic/ytracker.git
cd ytracker
pipx install --include-deps .
```

### Usage:

```
Usage: ytracker [COMMAND]

Manage the ytracker service.

Commands:
  start    Start the ytracker service.
  stop     Stop the ytracker service.
  help     Show this help message and exit (default).
```

Before running `ytracker start` you should create a text file containing urls
to the YouTube channel's you want to subscribe to. Put each url on its own line, like this:

```
https://www.youtube.com/@Some-Channel/videos
https://www.youtube.com/@Some-Other-Channel/videos

```

File should here: `~/.local/share/ytracker/ytracker_urls.txt`

Make sure to name the file exactly like this `ytracker_urls.txt`

In case you want to manually create a config file, here's example:

```
{
  "download_path": "/home/your-user/Videos/ytracker",
  "refresh_interval": 2,
  "storage_size": 5,
  "video_quality": "720"
}
```

This step is optional, ytracker will automatically create this config like in the example above.

download_path
: Path on disk where videos will be downloaded to. Please pick the directory with a right permissions.

refresh_interval
: Time interval defined in hours of how often ytracker will check for new content.

storage_size
: Size on disk limit defined in gigabytes of how much storage can videos take before older videos are deleted.

video_quality
: Video resolution. Supported values: 360, 480, 720, 1080


### Note

This program is Unix only, so no Windows Os support, and it was only tested on Debian GNU/Linux,
so it may not work of Apple devices.