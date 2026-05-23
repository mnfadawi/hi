# Phone ElectriK — AI Phone Answering Setup

## What it does
- Answers every call with a friendly AI greeting
- Answers questions: prices, services, hours, location, what devices you fix
- Takes messages and saves them to `data/messages.json`
- Books drop-off appointments and saves them to `data/appointments.json`
- Transfers callers to a real person if they ask

---

## Requirements
- Python 3.11+
- A [Twilio](https://twilio.com) account (free trial works to test)
- An [Anthropic API key](https://console.anthropic.com)
- A publicly reachable URL for the Flask server (see Step 3)

---

## Step 1 — Install dependencies

```bash
cd phone_ai
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

---

## Step 2 — Configure environment

```bash
cp .env.example .env
```

Edit `.env` and fill in:
| Variable | Where to find it |
|---|---|
| `ANTHROPIC_API_KEY` | https://console.anthropic.com |
| `TWILIO_ACCOUNT_SID` | Twilio Console → Account Info |
| `TWILIO_AUTH_TOKEN` | Twilio Console → Account Info |
| `TWILIO_NUMBER` | Your Twilio phone number in +1XXXXXXXXXX format |
| `TRANSFER_NUMBER` | Your cell — calls forward here when a human is requested |

---

## Step 3 — Expose the server publicly

### Option A: Local testing with ngrok (free)
```bash
# Terminal 1 — start Flask
python app.py

# Terminal 2 — expose it
ngrok http 5000
```
ngrok gives you a URL like `https://abc123.ngrok.io`.

### Option B: Deploy to a cloud server (production)
Deploy the `phone_ai/` folder to any VPS, Railway, Render, or Heroku.
Make sure the server runs on the PORT you set.

---

## Step 4 — Connect your store number (323) 348-6756

You have two options:

### Option A: Port your number to Twilio (Recommended for production)
This makes Twilio own your number so all calls go directly to the AI.

1. Go to **Twilio Console → Phone Numbers → Port & Host a Number**
2. Enter `(323) 348-6756` and follow the porting wizard
3. Porting typically takes 2–4 weeks; your number keeps working during the transfer
4. Once ported, set the webhook (see below)

### Option B: Forward your store phone to a Twilio number (Fastest to test)
Keep your existing carrier. Just forward calls to a Twilio number that runs the AI.

1. In Twilio Console, **buy a new number** (≈$1/month)
2. Set that number as `TWILIO_NUMBER` in your `.env`
3. On your store phone, enable **call forwarding** to the new Twilio number
   - Most carriers: dial `*72` then the Twilio number, press Call
   - Or do it through your carrier's account portal
4. Set the webhook on your Twilio number (see below)

### Point the Twilio number at this server

1. Go to **Twilio Console → Phone Numbers → Manage → Active Numbers**
2. Click your number
3. Under **Voice & Fax**, set:
   - **A call comes in** → **Webhook**
   - URL: `https://YOUR-SERVER/voice/answer`
   - HTTP: **HTTP POST**
4. Save.

That's it — call the number and the AI will answer.

---

## Viewing messages & appointments

While the server is running:
- Messages: `http://localhost:5000/messages`
- Appointments: `http://localhost:5000/appointments`

The raw JSON files are in `phone_ai/data/`.

---

## Customizing the AI

Edit the `_SYSTEM_PROMPT` in `ai_handler.py` to update:
- Specific pricing
- New services
- Business policies
- Tone / personality
