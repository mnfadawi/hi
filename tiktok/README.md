# Phone ElectriK social videos

Ready-to-post vertical videos (1080x1920) for TikTok, Instagram Reels, Facebook Reels and YouTube Shorts.
Every video has an AI voice reading it, and every video ends with the warranty slide and the shop's info.

- **Videos:** `out/*.mp4` (the `-cover.jpg` next to each one is the opening screen, to use as the cover)
- **Captions:** `CAPTIONS.md` (TikTok, Instagram, Facebook and YouTube versions for every video)

## How to post
1. Upload the video.
2. Paste the caption for that platform from `CAPTIONS.md`.
3. Tag the location: **Phone ElectriK, Torrance**.
4. Optional: add a trending sound and turn its volume down to about 10–20%, so the voice is still clear.
5. Post the same video to TikTok, Instagram Reels, Facebook Reels and YouTube Shorts.
   Tip: Instagram can share each Reel to your Facebook page automatically (turn on "Share to Facebook" when posting).

## 3-week posting plan (1–2 a day)
Strongest videos first, and a mix of repairs, trust and selling.

| Day | Morning | Evening |
|---|---|---|
| 1 | 00 full video | 02 battery signs |
| 2 | 01 water damage | 07 why us |
| 3 | 03 cracked screen | 09 we buy phones |
| 4 | 04 charging port | 08 walk in |
| 5 | 06 screen signs | 10 refurbished |
| 6 | 11 diagnostic | 17 game consoles |
| 7 | 05 more than phones | 20 South Bay |
| 8 | 14 slow phone | 12 data transfer |
| 9 | 15 back glass | 19 accessories |
| 10 | 13 unlocking | 18 Apple Watch |
| 11 | 16 camera lens | |
| 12–21 | Repost the 5 that got the most views, then ask for a new batch | |

Best times to post: around 12–2 PM and 6–9 PM.

## Making more videos
Write new videos in `videos.json` (wrap a word in `*stars*` to make it orange; add `"say"` to change what the voice reads), then:

```
pip install kokoro-onnx soundfile pillow numpy
mkdir -p models && cd models
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.int8.onnx
curl -LO https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
cd ..
python3 make_videos.py           # all videos (or: python3 make_videos.py battery)
python3 combine.py               # the full combined video
python3 captions.py              # CAPTIONS.md
```
Change the voice with `VOICE=am_michael python3 make_videos.py` (a male voice). The default is `af_heart`.
