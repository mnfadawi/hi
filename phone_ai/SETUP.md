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
| `TRANSFER_NUMBER` | Your cell or the number to forward to when a human is requested |

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

## Step 4 — Point your Twilio number to this server

1. Go to **Twilio Console → Phone Numbers → Manage → Active Numbers**
2. Click your business number
3. Under **Voice & Fax**, set:
   - **A call comes in** → **Webhook**
   - URL: `https://YOUR-SERVER/voice/answer`
   - HTTP: **HTTP POST**
4. Save.

That's it. Call your number and the AI will answer.

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
