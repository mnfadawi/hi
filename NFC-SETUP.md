# NFC Review Stands — Setup

Two tap-to-review stands for the counter: one for **Google**, one for **Yelp**.

| Stand  | Program the chip with          | Currently sends people to |
|--------|--------------------------------|---------------------------|
| Google | `https://phoneelectrik.com/g`  | Google reviews for Phone ElectriK (set in `g.html`) |
| Yelp   | `https://phoneelectrik.com/y`  | yelp.com/biz/phone-electrik-torrance-2 (set in `y.html`) |

The chips point to our own website, and the website forwards to Google or Yelp.
If a review link ever changes, just edit `g.html` / `y.html`. **You never have to reprogram the chips.**

## 1. What to buy

- **2 NFC stickers, NTAG213 or NTAG215** (round, ~25–30 mm). Get "on-metal"/anti-metal ones only if the stand is metal.
- **2 acrylic sign holders, 4" × 6" portrait** (the L-shaped or T-shaped counter kind).

## 2. Print the inserts

1. Open `https://phoneelectrik.com/nfc-stand.html` (or `nfc-stand.html` locally) in Chrome.
2. Click **Print**. Paper: **Letter**. Scale: **100% / Actual size**. Turn on **Background graphics**.
3. Cut on the dashed lines, then slide each card into its stand.
   Cardstock or glossy photo paper looks best.

## 3. Program the chips (5 minutes, any phone)

1. Install the free **NFC Tools** app (iPhone or Android).
2. Tap **Write** → **Add a record** → **URL / URI**.
3. Type `phoneelectrik.com/g` (the app adds `https://`). Tap **OK**.
4. Tap **Write**, then hold the top of your phone against the sticker until it says it's done.
5. Test it: lock and unlock your phone, tap the sticker, and the Google page should open.
6. Repeat with the second sticker, using `phoneelectrik.com/y`.
7. *(Optional, once both work)* **Other → Lock tag** so customers can't overwrite it.
   Locking is permanent. Only lock it after you've tested it.

## 4. Stick them on

Put each sticker on the **back** of its stand, directly behind the orange "Tap your phone here"
circle. NFC reads through acrylic and paper just fine. Label the stickers G and Y so you don't mix them up.

## How customers use it

- **iPhone (XS and newer):** hold the top edge of the phone to the circle. A banner pops up; tap it.
- **Android:** NFC must be on (it usually is). Tap the middle of the back of the phone to the circle.
- **No NFC / not working:** the QR code on each card goes to the same link.

## Make the Google link go straight to the "write a review" box (recommended)

Right now `g.html` opens Google's search results for our reviews. For a one-tap review box:

1. Sign in at **business.google.com** (or search "my business" on Google while signed in).
2. Click **Ask for reviews** / **Get more reviews** and copy the link (looks like `https://g.page/r/XXXX/review`).
3. In `g.html`, replace the Google URL in **all three places** (the `meta refresh`, `REVIEW_URL`, and the button link) with that link.

The chips and QR codes keep working. Nothing else changes.

## A note about Yelp

Yelp's rules discourage businesses from **asking** customers for reviews, and Yelp can flag a business
that does it. That's why the Yelp card says "Find us on Yelp" instead of "Review us on Yelp." Google allows review requests.
