"""
Claude-powered AI brain for Phone ElectriK's phone answering system.
"""
import os
import anthropic
from data_manager import DataManager

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

== HOW TO HANDLE CALLS ==
1. Be friendly, warm, and professional — this is a small family-owned shop.
2. Answer questions directly using the info above.
3. If asked about a specific price, give a general range if possible but say exact price depends on the model and encourage them to come in or call the shop directly.
4. If someone wants to leave a message, collect their name, message, and callback number, then use the take_message tool.
5. If someone wants to book an appointment (drop-off time), collect name, phone, preferred date/time, and what device/issue — then use schedule_appointment.
6. If the caller asks to speak to a person or you cannot help them, use transfer_to_human.
7. When the call is wrapping up, use end_call with a warm farewell.
8. Keep ALL responses SHORT — this is a phone call, not a chat. One to three sentences max per turn.
9. Never make up prices you are not sure about. Say "I'd recommend calling or stopping in — we'll give you an exact quote on the spot."

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
