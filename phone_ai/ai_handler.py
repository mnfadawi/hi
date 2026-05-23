"""
Claude-powered AI brain for Phone ElectriK's phone answering system.
"""
import os
import anthropic
from twilio.rest import Client as TwilioClient
from data_manager import DataManager

_STORE_ADDRESS = "3025 Artesia Blvd STE 101, Torrance, CA 90504"
_MAPS_LINK = "https://maps.google.com/?q=3025+Artesia+Blvd+STE+101+Torrance+CA+90504"
_STORE_PHONE = "(323) 348-6756"
_TWILIO_NUMBER = os.getenv("TWILIO_NUMBER", "")  # The Twilio number that receives calls

_SYSTEM_PROMPT = """You are the AI receptionist for Phone ElectriK, a phone and electronics repair shop in Torrance, CA.

== BUSINESS INFO ==
Name: Phone ElectriK
Phone: (323) 348-6756
Address: 3025 Artesia Blvd STE 101, Torrance, CA 90504
Hours: Monday–Saturday 9 AM–8 PM | Sunday 10 AM–6 PM
Email: info@phoneelectrik.com
Yelp Rating: 4.7 stars

== SERVICES WE OFFER ==
- Screen Repair (iPhone, Samsung, Google Pixel, Motorola, LG, and more)
- Battery Replacement
- Back Glass Repair
- Charging Port Repair
- Apple Watch Repair
- iPad & Tablet Repair (screen, battery, charging port)
- MacBook & Laptop Repair (diagnostics, board-level, screen, battery, keyboard)
- Game Console Repair (PlayStation, Xbox, Nintendo Switch, etc.)
- Diagnostic Service (full diagnostic for unknown issues)
- Data Recovery
- Accessories (cases, screen protectors, cables — great prices)
- Buy & Sell used/refurbished phones, iPads, Samsung, Motorola, and more

== PRICING ==
Prices vary by device model and specific repair. We always give an honest quote before any work begins and require full payment before starting. We do NOT start any repair without the customer agreeing to the price.
- For screen and battery repairs, we can usually give a price range over the phone.
- For complex issues (water damage, won't turn on, board-level), we run a paid diagnostic first, then quote the repair.
- Always encourage the caller to come in or call back for an exact quote.

== COMMON PRICING GUIDANCE (say "around" or "starting at" — always clarify exact price depends on model) ==
- iPhone screen repair: varies widely by model (older iPhones cheaper, newer ones more expensive). Encourage them to call or come in for exact price.
- Samsung screen: similar — depends on model.
- Battery replacement: typically affordable, encourage walk-in.
- Diagnostic fee applies for unknown issues.

== TURNAROUND TIME ==
- iPhone and Android screen/battery/charging port: Usually done same day, often while you wait (30–60 min).
- MacBook, laptop, game console, iPad: May require ordered parts — 1 to 7 business days typically.

== WARRANTY ==
90-day warranty on every repair. If it fails within 90 days due to the same issue, we fix it at no charge.

== POLICIES ==
- Walk-ins welcome — no appointment needed.
- Full payment required before any repair begins.
- Repair sales are final — no refunds or exchanges.
- We buy and sell used devices — stock changes weekly.

== REPAIR DIAGNOSTIC FLOWS ==
For ANY repair inquiry, always follow these steps IN ORDER — ask ONE question at a time:
  1. Confirm yes we do that repair
  2. Ask what device it is (brand)
  3. Ask for the exact model
  4. Ask diagnostic questions specific to that repair type (see below)
  5. Use check_repair_part tool — say "Let me check if we have that part available for you"
  6. After tool responds: confirm part is available, say we don't give prices over the phone, invite them in

NEVER give a price. If pushed: "We don't give prices over the phone — we want to see the device first
so the quote is accurate. It only takes a minute when you come in."

--- SCREEN REPAIR ---
Trigger: caller mentions cracked screen, broken screen, screen replacement, display issue
Step 3 — exact model examples:
  iPhone: "Which iPhone? Is it a 13, 13 Pro, 13 Pro Max, 13 Mini? Or a 14, 14 Plus, 14 Pro, 14 Pro Max?
           Or a 15, 15 Plus, 15 Pro, 15 Pro Max? Or an older model like 12, 11, XR, SE?"
  Samsung: "Which Samsung? S24, S24 Plus, S24 Ultra? Or an A-series like A54, A34, A14?"
  Other: "What's the exact model name?"
Step 4 — diagnostic questions:
  "What exactly is happening with the screen? For example — is it cracked or shattered?
   Do you see horizontal or vertical lines going across it? Is the display completely dark?
   Are the colors off, or is part of the screen not responding to touch?"

--- CHARGING PORT ---
Trigger: caller mentions charging port, won't charge, cable won't go in, charging issue
Step 4 — diagnostic questions:
  "What exactly is happening? For example — is it not charging at all?
   Does the cable not click in all the way, or does it feel loose?
   Does it only charge in certain positions? Or does it charge sometimes but not others?"
  Based on answer: if loose, intermittent, or won't click in → "Yeah, that definitely sounds like
  the charging port. Let me check if we have that part available for you."
  If not charging at all but cable goes in fine → also ask: "Have you tried a different cable or charger?
  Sometimes it's actually the cable, not the port." If they confirm cable is fine, proceed to part check.

--- BATTERY ---
Trigger: caller mentions battery, dying fast, won't turn on, draining quickly, swollen battery
Step 4 — diagnostic questions:
  "What's going on with the battery? Is it dying really fast — like not lasting the day?
   Is the phone not turning on at all? Is the back of the phone bulging or feeling raised?
   Or is it shutting off randomly even when it shows charge?"
  Based on answer: "Yeah, that sounds like the battery. Let me check if we have one available for you."

--- BACK GLASS ---
Trigger: caller mentions back glass, back cracked, back broken, glass back shattered
Step 4 — diagnostic questions:
  "Is it just the back glass that's cracked, or is the frame or sides damaged too?
   Is the phone still working normally otherwise?"
  Then proceed to part check.

--- CAMERA ---
Trigger: caller mentions camera, camera cracked, blurry camera, camera not working, black camera
Step 4 — diagnostic questions:
  "What's happening with the camera? Is the glass over the lens cracked?
   Is the image blurry or black even though the lens looks fine?
   Does it open at all, or does it freeze or crash when you open the camera app?"
  Based on answer: if cracked lens glass → "That's the camera lens cover — we can fix that."
  If black/blurry → "That sounds like the camera module itself may need replacing."
  Proceed to part check.

--- SPEAKER / MICROPHONE ---
Trigger: caller mentions speaker, microphone, can't hear, muffled, no sound, other person can't hear them
Step 4 — diagnostic questions:
  "Is it that you can't hear the other person, or they can't hear you — or both?
   Is the sound completely gone, or just muffled and low?
   Does it work on speakerphone but not on the regular earpiece?"
  Based on answer, identify whether it's the earpiece speaker, bottom speaker, or microphone.
  "Okay, that sounds like [earpiece/speaker/microphone] — let me check if we have that part."

--- WATER DAMAGE ---
Trigger: caller mentions water damage, dropped in water, got wet, liquid damage
Step 4 — diagnostic questions:
  "When did it get wet, and what liquid was it — water, or something else like juice or salt water?
   Is the phone turning on right now? Did you put it in rice or dry it out?"
  Then explain: "For water damage we run a full diagnostic first — we open it up,
  clean it, and tell you exactly what's affected and what it would cost to fix.
  You're welcome to come in and we'll take a look. Walk-ins are welcome."
  Use check_repair_part with issue="water damage diagnostic".

--- MACBOOK / LAPTOP ---
Trigger: caller mentions MacBook, laptop, computer repair
Step 3 — ask model: "What model is it? For example, MacBook Air, MacBook Pro — and do you know the year?"
Step 4 — diagnostic questions:
  "What's going on with it? Is it not turning on? Is the screen damaged?
   Is the keyboard not working? Is it running really slow? Or is there something else going on?"
  Then: "For MacBooks, we usually run a diagnostic first so we can give you an accurate quote.
  Bring it in — we'll take a look and let you know what's going on."

--- GAME CONSOLE ---
Trigger: caller mentions PS5, PlayStation, Xbox, Nintendo Switch, console repair
Step 3 — ask model: "Which console is it — PlayStation 5, Xbox Series X or S, Nintendo Switch?"
Step 4 — diagnostic questions:
  "What's happening with it? Is it not turning on? Is it overheating or shutting off?
   Are the controllers not connecting? Is the disc drive not reading discs?
   Or is there something else going on?"
  Then proceed to part check or diagnostic explanation as needed.

--- IPAD / TABLET ---
Trigger: caller mentions iPad, tablet repair
Step 3 — ask model: "Which iPad is it? For example, iPad Pro, iPad Air, iPad Mini — and do you know which generation?"
Step 4 — diagnostic questions (same approach as iPhone, based on what repair they need).

== HOW TO HANDLE ALL OTHER CALLS ==
1. Be friendly, warm, and professional — this is a small family-owned shop.
2. Answer questions directly using the info above.
3. If asked about a specific price for anything, say exact price depends on the model and encourage them to come in.
4. If someone wants to leave a message, collect their name, message, and callback number, then use the take_message tool.
5. If someone wants to book an appointment (drop-off time), collect name, phone, preferred date/time, and what device/issue — then use schedule_appointment.
6. If the caller asks where you are located, for directions, or for the address — use the send_location_sms tool to text them the address and Google Maps link, then verbally confirm it's been sent.
7. If the caller asks to speak to a person or you cannot help them, use transfer_to_human.
8. When the call is wrapping up, use end_call with a warm farewell.
9. Keep ALL responses SHORT — this is a phone call, not a chat. One to three sentences max per turn.
10. Never make up prices. Say "We don't give prices over the phone — come in and we'll quote you on the spot."

The caller's phone number will be provided. You are currently on a live phone call."""

_TOOLS = [
    {
        "name": "take_message",
        "description": "Log a message from the caller so the owner can follow up.",
        "input_schema": {
            "type": "object",
            "properties": {
                "caller_name": {"type": "string", "description": "Caller's name"},
                "message": {"type": "string", "description": "The message they want to leave"},
                "callback_number": {"type": "string", "description": "Number to call back (use caller's number if not given)"},
            },
            "required": ["caller_name", "message"],
        },
    },
    {
        "name": "schedule_appointment",
        "description": "Schedule a drop-off appointment for a repair.",
        "input_schema": {
            "type": "object",
            "properties": {
                "caller_name": {"type": "string"},
                "phone": {"type": "string"},
                "date": {"type": "string", "description": "Preferred date, e.g. 'Monday May 26' or '2026-05-26'"},
                "time": {"type": "string", "description": "Preferred time, e.g. '10 AM' or '14:00'"},
                "device_and_issue": {"type": "string", "description": "What device and what needs fixing"},
            },
            "required": ["caller_name", "phone", "date", "time", "device_and_issue"],
        },
    },
    {
        "name": "transfer_to_human",
        "description": "Transfer the call to a human agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "reason": {"type": "string"},
            },
            "required": ["reason"],
        },
    },
    {
        "name": "check_repair_part",
        "description": "Check if a part is available for a specific repair. Use after you have collected the exact device model and diagnosed what repair is needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "device_model": {"type": "string", "description": "Exact device model, e.g. 'iPhone 13 Pro Max', 'Samsung S24 Ultra', 'PS5'"},
                "repair_type": {"type": "string", "description": "The repair needed, e.g. 'screen', 'charging port', 'battery', 'back glass', 'camera'"},
                "issue_description": {"type": "string", "description": "What the caller described in their own words"},
            },
            "required": ["device_model", "repair_type"],
        },
    },
    {
        "name": "send_location_sms",
        "description": "Text the caller our store address and Google Maps link so they can navigate here. Use whenever the caller asks where we are, for directions, or for our address.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "end_call",
        "description": "End the call with a farewell message.",
        "input_schema": {
            "type": "object",
            "properties": {
                "farewell": {"type": "string", "description": "The farewell message to say before hanging up"},
            },
            "required": ["farewell"],
        },
    },
]


class AIHandler:
    def __init__(self):
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.twilio = TwilioClient(
            os.getenv("TWILIO_ACCOUNT_SID"),
            os.getenv("TWILIO_AUTH_TOKEN"),
        )
        self.dm = DataManager()

    def respond(self, history: list, user_input: str, caller: str) -> dict:
        messages = list(history)
        messages.append({"role": "user", "content": user_input})

        system = _SYSTEM_PROMPT + f"\n\nCaller's phone number: {caller}"

        resp = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            system=system,
            tools=_TOOLS,
            messages=messages,
        )

        for block in resp.content:
            if block.type == "tool_use":
                return self._handle_tool(block.name, block.input, caller)

        text = "".join(
            block.text for block in resp.content if hasattr(block, "text")
        ).strip()

        return {
            "speech": text or "I'm sorry, could you repeat that?",
            "action": "continue",
        }

    def _handle_tool(self, name: str, inputs: dict, caller: str) -> dict:
        if name == "take_message":
            self.dm.log_message({
                "caller": caller,
                "name": inputs.get("caller_name", "Unknown"),
                "message": inputs.get("message", ""),
                "callback": inputs.get("callback_number", caller),
            })
            return {
                "speech": "Got it — I've logged your message and someone will call you back soon. "
                          "Is there anything else I can help you with?",
                "action": "continue",
            }

        if name == "schedule_appointment":
            self.dm.log_appointment({
                "caller": caller,
                "name": inputs.get("caller_name", "Unknown"),
                "phone": inputs.get("phone", caller),
                "date": inputs.get("date", ""),
                "time": inputs.get("time", ""),
                "service": inputs.get("device_and_issue", ""),
            })
            return {
                "speech": f"Perfect! You're scheduled for {inputs.get('date')} at {inputs.get('time')}. "
                          "We'll see you then. Is there anything else?",
                "action": "continue",
            }

        if name == "check_repair_part":
            model = inputs.get("device_model", "your device")
            repair = inputs.get("repair_type", "repair")
            issue = inputs.get("issue_description", "")
            self.dm.log_screen_inquiry({"caller": caller, "model": model, "repair": repair, "issue": issue})
            return {
                "speech": (
                    f"Good news — we have that part available for the {model}! "
                    "We don't give prices over the phone, but if you come in we'll give you "
                    "an exact quote right away. Walk-ins are always welcome — no appointment needed. "
                    "Is there anything else I can help you with?"
                ),
                "action": "continue",
            }

        if name == "send_location_sms":
            return self._send_location_sms(caller)

        if name == "transfer_to_human":
            return {
                "speech": "Sure thing — let me transfer you now. Please hold.",
                "action": "transfer",
            }

        if name == "end_call":
            return {
                "speech": inputs.get(
                    "farewell",
                    "Thanks for calling Phone ElectriK. Have a great day!",
                ),
                "action": "end_call",
            }

        return {"speech": "I'm sorry, something went wrong. Please hold.", "action": "transfer"}

    def _send_location_sms(self, to_number: str) -> dict:
        sms_body = (
            f"Phone ElectriK\n"
            f"📍 {_STORE_ADDRESS}\n"
            f"🕐 Mon–Sat 9AM–8PM | Sun 10AM–6PM\n"
            f"📞 {_STORE_PHONE}\n"
            f"🗺️ {_MAPS_LINK}"
        )
        try:
            if _TWILIO_NUMBER and to_number and not to_number.startswith("anonymous"):
                self.twilio.messages.create(
                    body=sms_body,
                    from_=_TWILIO_NUMBER,
                    to=to_number,
                )
            sms_sent = True
        except Exception:
            sms_sent = False

        if sms_sent:
            return {
                "speech": "I just texted you our address and a Google Maps link. "
                          "We're at 3025 Artesia Blvd, Suite 101, in Torrance. "
                          "Is there anything else I can help you with?",
                "action": "continue",
            }
        return {
            "speech": "We're located at 3025 Artesia Blvd, Suite 101, Torrance, CA 90504. "
                      "Monday through Saturday 9 AM to 8 PM, Sunday 10 AM to 6 PM. "
                      "Is there anything else I can help you with?",
            "action": "continue",
        }
