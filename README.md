> Like the cleaning of a house...

![simpsons clock](itneverends.jpg)

Here we are in the year ~~2025~~ 2026 and yet another modification of Brandon Withrow's Simpsons TV [Waveshare-version TV build][original-build].

This one includes some great changes from [Jeremy Whelchel's updated version](https://github.com/jeremywhelchel/simpsonstv), notably the touchscreen support and adds onto those as well for more recent Raspberry Pi OS (Bullseye, Bookworm) support.

## Modern Raspberry Pi OS support

The core issue in making this project in 2024/25/26 is that the original guide uses the legacy version of RaspberryPi OS (Buster) along with a video player `omxplayer` that no longer works on the newer version of the OS. Jeremy's version uses a newer player `mpv` that unfortunately I also could not get to work on the newest OS (Bullseye) (2024-03-12, Lite) on a PI Zero. I didn't want to rely on the legacy OS, so I wanted to see if I could get it working in the modern OS using trusty ol' [VLC][vlc].

After much thrashing here it is.

## Installation instructions

As new Raspberry Pi Os's are released I am trying to occasionally revisit and update if needed. `main` branch should always be the latest tested; see branches or releases for older releases like v11 (Bookworm).

### Current version notes

**OS Lite 32-Bit Bullseye (12)**
Raspberry PI Zero W
VLC

A number of changes in the newer versions of PiOS make things overall easier, but different from the [original build][original-build]. I'll note them here as I encountered them. Notably the only settings needed in the `config.txt` are the gpio and specific screen dtoverlay settings.

### Getting the screen to work

Despite the instructions in the [Waveshare Wiki][waveshare-wiki], using the config provided for the Bookworm and Bullesye branches of PiOS would not work for me. After lots of trial and error I ended up using the same config they had posted for the legacy Buster branch, and for that still worked. Still use the same `dtbo` files they provide in the link above.

`config.txt`

```
dtoverlay=waveshare-28dpi-3b-4b
dtoverlay=waveshare-28dpi-3b
dtoverlay=waveshare-28dpi-4b
```

#### Waveshare 3.5in. 640x480

I have also made a Futurama TV and I decided to try a
slightly larger screen. Here are the changes I made for the larger screen.

[Waveshare wiki for 3.5][waveshare-35]

`config.txt`

```
dtoverlay=vc4-kms-v3d
dtoverlay=waveshare-35dpi
dtoverlay=waveshare-touch-35dpi
```

### Installing vlc and related package

Still logged into the Pi, install vlc by running

```
sudo apt install vlc
```

The touch script also makes use of a [simple python package](https://github.com/MatejMecka/python-vlc-http) to make communicating to VLCs http server easier. Newer versions of PiOS also don't seem to include `evdev` so we can install that too.

> Depending on your system, you may need to use `pipx` instead or use the flag `--break-system-packages` if you encounter issues installing with `pip`.

```
apt install python-vlc-http
pip install evdev
```

### Other notes

The updated `touch.py` in this repo should be more resilient to other types of screens and eventbus order. It also includes a constant at the top
to use if you rotate your screen that will ensure the touch inputs are also rotated.

As of OS 12, `rc.local` isn't included (mentioned in the original guide as the method to override pin output) but you can still do the same with a service file (also included in this repo):

gpio-init.service
```
[Unit]
Description=GPIO initialization
Before=tvplayer.service

[Service]
Type=oneshot
ExecStart=/usr/bin/raspi-gpio set 18 op dl
ExecStart=/usr/bin/raspi-gpio set 19 op a5
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

Update the permissions on the `start.sh` script to allow it to be run from the service.

```
chmod +x simpsonstv/start.sh
```

VLC will also not run as root from the service files, so make sure that your `.service` files have a `user` entry in them. The ones included in this repo do, but make sure the user matches the actual user you have setup on your Pi.

I also used an [updated version of the 3D model by Freakadude](https://www.thingiverse.com/thing:5027609) that printed and worked very well.

---

_Further notes from Jeremy's version that are helpful:_

## Touchscreen player control

The [Waveshare 2.8" screen][waveshare-wiki] has capacitive touch that wasn't used in the original
build. I added a simple `touch.py` job to listen to screen events and send a
handful of commands to the video player. Be sure to add a corresponding systemd
service.

You can:
- Touch left side of screen - seek back 15 seconds
- Touch middle of screen - play / pause
- Touch right side of screen - seek forward 45 seconds
- Swipe from left to right - next video
- Swipe from right to left - previous video

## Videos on FAT partition

It's much easier to manage the videos when they are on a separate FAT partition
on the SD Card. Rather than copying over the network or mounting another thumb
drive, the card can be plugged in to a normal computer and files can be copied
to a mounted partition.

After initially flashing Raspbian (and editing `config.txt`, etc) but before first boot, which will auto-resize partition to take up all the remaining free space, create a new fat32 partition at the END of the free space. But still leaving enough room for the original linux partition to grow. I left 10GB. This was done using Gparted on a separate linux machine.

Later, once the RPpi is up and you are logged in, you can manually resize the
ext4 partition, via something like:

```
# Resize the ext4 / partition
sudo parted
> print
> resizepart 2 8G
> <ctrl-D>

# Extend the ext4 filesystem to fill up the partitioned space.
df -h
blkid
sudo resize2fs /dev/mmcblk0p2
df -h
```

Finally, auto-mount the videos data partition at `/video`
`sudo mkdir /video`

Then add the following line to `/etc/fstab`

```
  /dev/mmcblk0p3 /video vfat defaults 0 2
```

## Hardware changes

I also glued in the screen upside down, since the bezel was better covered by
the 3d printed housing that way. To invert the screen, set `display_rotate=3` in `/boot/config.txt`

Switched from Micro-USB to USB-C for the power input. Use something like this
[Adafruit USB Type-C breakout board](https://www.adafruit.com/product/4090). Make sure the breakout board has CC resistors that properly indicate 5 volts--otherwise this won't work with C-to-C cables.

[original-build]: https://withrow.io/simpsons-tv-build-guide-waveshare
[waveshare-wiki]: https://www.waveshare.com/wiki/2.8inch_DPI_LCD
[waveshare-35]: https://www.waveshare.com/wiki/3.5inch_DPI_LCD
[vlc]: https://www.videolan.org/vlc/