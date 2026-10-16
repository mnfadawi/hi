# Phone ElectriK — Vertical Welcome Sign (Samsung TV via USB)

Files built for a **standard Samsung TV mounted on its side (portrait)**,
playing from a USB flash drive. **Do not rotate anything with the remote**:
the picture is already turned inside the file.

## Which file do I use?

There are two folders. They hold the same sign, turned opposite ways, because
the right one depends on which way your TV was turned when it went on the wall.

| Folder | Use it if… |
|---|---|
| `TV-turned-CLOCKWISE/` | The TV's original **top edge is now on the RIGHT** |
| `TV-turned-COUNTERCLOCKWISE/` | The TV's original **top edge is now on the LEFT** |

Not sure? Put both `.jpg` files on the drive, open each one on the TV, and keep
the folder whose picture is right-side up.

Each folder contains:

- **`PhoneElectriK-Welcome.mp4`**: the welcome sign on its own. A 30-minute
  1920×1080 H.264 (Constrained Baseline, yuv420p) video with a soft shine
  across the orange bars.
- **`PhoneElectriK-2Slide.mp4`**: a two-slide version to try. It shows the
  welcome sign for 15 s, then a clean cut to **Our Repair Services** for 15 s,
  repeating. It uses the same video settings and is also 30 minutes long.
  The services slide uses the wording from `services.html` on the website,
  including the refurbished devices and "We Also Buy Devices" sections.
- `PhoneElectriK-Welcome.jpg` / `PhoneElectriK-Services.jpg`: still images
  of each slide, for the test above or as a backup.

Use **one** video on the drive, not both.

## Setting up the USB drive

1. Format the drive as **FAT32** or **exFAT**. A drive with nothing else on it works best.
2. Copy **only one** video (`PhoneElectriK-Welcome.mp4` or `PhoneElectriK-2Slide.mp4`) from the correct folder to the
   **root** of the drive (not inside a folder). If there are other files on the
   drive, the TV will play them as well.
3. Plug it into the TV. Open **Source → USB** and play the video.
4. During playback, press **Enter/OK** (or **Down**) on the remote, open
   **Options → Repeat**, and choose **Repeat One**, or **Repeat All** if that's
   the only choice. It will now loop all day.
5. If black bars appear, set **Picture Size** to **16:9 Standard**, and turn
   on **Fit to Screen** if your model has it.

## One-time TV settings (stops the "kicked back to Home" problem)

Names vary slightly by model year:

- **Settings → General → System Manager → Time → *Auto Protection Time*** (or
  Settings → General → *Auto Protection Time*): set it to **Off** or the
  longest value.
- **Settings → General → Eco Solution / Power and Energy Saving**: turn off
  **Auto Power Off**, **No Signal Power Off** and **Motion Lighting**.
- **Settings → General → Smart Features → *Autorun Smart Hub* / *Autorun Last
  App***: turn these **off** so the TV doesn't open the Home menu on its own.
- Keep the TV's software up to date. Several USB playback bugs have been
  fixed in updates.

## Why this works (short version)

- The TV's **photo viewer** turns on its burn-in screensaver (**Auto
  Protection Time**) when it sees a still image, and it often leaves the USB
  app when it does. It also throws away any rotation done with the remote
  whenever it reloads the picture. Its **video player** doesn't use that
  screensaver, and its **Repeat** setting is made to run all day.
- The video is a plain **1920×1080 landscape** file, so the TV has nothing to
  rotate, rescale or "correct". The sign is simply drawn sideways inside it.
- It uses the most widely supported settings: H.264 Constrained Baseline\@4.0 (no B-frames, no CABAC), yuv420p,
  BT.709, 30 fps, with a silent AAC audio track and no rotation tag. The
  picture barely changes from frame to frame, so the file stays small and
  easy for the TV to play.
- The still images are **baseline** (not progressive) JPEGs with **no EXIF
  orientation tag**. Some Samsung models only load progressive JPEGs up to
  1024×768 and fail or show black on anything bigger.
- `tv-display.html` and the `.svg` files **can't be opened from a USB stick** on
  a consumer Samsung TV (the media player only plays photos, video and music).
  Use the files in this folder instead.

## Changing the design

- Slide 1 / Welcome: edit `../tv-poster.png` (portrait, 1080×1920).
- Slide 2 / Services: edit `slide2-services.html`. `render_slide.js` turns it
  into a 1080×1920 picture and stops with an error if the text runs off the
  bottom.

Then rebuild everything:

```bash
python3 usb-sign/build.py   # needs Python 3 (Pillow, numpy), ffmpeg, Node + playwright
```

In the 2-slide video, slide 1's background is shifted from #0d0d0d to pure
#000000 so both slides match. The Welcome-only video is left exactly as it was.
