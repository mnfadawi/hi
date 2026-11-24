# Phone ElectriK social videos

Ready-to-post vertical videos (1080x1920) for TikTok, Instagram Reels, Facebook Reels and YouTube Shorts.
Every video has an AI voice reading it, and every video ends with the 90-day warranty, the address and the phone number.

- **Videos:** `out/*.mp4` (the `-cover.jpg` next to each one is the opening screen, to use as the cover)
- **Captions:** `CAPTIONS.md` (TikTok, Instagram, Facebook and YouTube versions for every video)

## How to post
1. Upload the video.
2. Paste the caption for that platform from `CAPTIONS.md`.
3. Tag the location: **Phone ElectriK, Torrance**.
4. Optional: add a trending sound and turn its volume down to about 10–20%, so the voice is still clear.
5. Post the same video to TikTok, Instagram Reels, Facebook Reels and YouTube Shorts.
   Tip: Instagram can share each Reel to your Facebook page automatically (turn on "Share to Facebook" when posting).

## Posting plan: one video a day
Post them in number order: 01 (posted), 02, 03 … 20. That's 20 days of posts.
Best times: around 12–2 PM or 6–9 PM. After 2 weeks, check which videos got the most views and make more like those.

What changed in 02–20 (after looking at the real TikTok and Instagram numbers):
- Shorter: most videos are now 15–25 seconds, so more people watch to the end and see the address.
- The opening line shows from the very first frame (that frame is also the thumbnail).
- "TORRANCE · WALK-INS WELCOME" on every screen, so every second is a local ad.
- One ending screen: 90-day warranty, address, phone and "Walk in today".
- A slightly faster voice.
- New captions that ask a question, to get comments.

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
