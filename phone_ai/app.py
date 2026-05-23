"""
Phone ElectriK — AI Phone Answering System
Handles incoming Twilio calls and routes them through Claude.
"""
import os
from flask import Flask, request, Response
from twilio.twiml.voice_response import VoiceResponse, Gather, Dial
from twilio.request_validator import RequestValidator
from dotenv import load_dotenv
from ai_handler import AIHandler

load_dotenv()

app = Flask(__name__)
ai = AIHandler()

# Per-call conversation state keyed by Twilio CallSid
_conversations: dict[str, dict] = {}

TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
TRANSFER_NUMBER = os.getenv("TRANSFER_NUMBER", "")
VALIDATE_TWILIO = os.getenv("VALIDATE_TWILIO_REQUESTS", "true").lower() == "true"


def _validate_twilio(req) -> bool:
    if not VALIDATE_TWILIO:
        return True
    validator = RequestValidator(TWILIO_AUTH_TOKEN)
    url = req.url
    signature = req.headers.get("X-Twilio-Signature", "")
    return validator.validate(url, req.form, signature)


def _twiml(response: VoiceResponse) -> Response:
    return Response(str(response), mimetype="text/xml")


def _gather(action: str) -> Gather:
    return Gather(
        input="speech",
        action=action,
        timeout=6,
        speech_timeout="auto",
        language="en-US",
    )


@app.route("/voice/answer", methods=["POST"])
def answer():
    if not _validate_twilio(request):
        return Response("Forbidden", status=403)

    call_sid = request.form.get("CallSid", "unknown")
    caller = request.form.get("From", "Unknown number")

    _conversations[call_sid] = {"caller": caller, "history": []}

    response = VoiceResponse()
    gather = _gather("/voice/process")
    gather.say(
        "Thank you for calling Phone ElectriK in Torrance. "
        "I'm your automated assistant. How can I help you today?",
        voice="Polly.Joanna",
    )
    response.append(gather)
    response.redirect("/voice/no-input")
    return _twiml(response)


@app.route("/voice/process", methods=["POST"])
def process():
    if not _validate_twilio(request):
        return Response("Forbidden", status=403)

    call_sid = request.form.get("CallSid", "unknown")
    speech = request.form.get("SpeechResult", "").strip()

    if call_sid not in _conversations:
        _conversations[call_sid] = {"caller": "Unknown", "history": []}

    conv = _conversations[call_sid]
    result = ai.respond(conv["history"], speech, conv["caller"])

    conv["history"].append({"role": "user", "content": speech})
    conv["history"].append({"role": "assistant", "content": result["speech"]})

    response = VoiceResponse()

    if result["action"] == "transfer":
        response.say(result["speech"], voice="Polly.Joanna")
        if TRANSFER_NUMBER:
            dial = Dial()
            dial.number(TRANSFER_NUMBER)
            response.append(dial)
        else:
            response.say(
                "I'm sorry, I'm unable to transfer your call right now. "
                "Please call back or visit us in store. Goodbye!",
                voice="Polly.Joanna",
            )
            response.hangup()

    elif result["action"] == "end_call":
        response.say(result["speech"], voice="Polly.Joanna")
        response.hangup()
        _conversations.pop(call_sid, None)

    else:
        gather = _gather("/voice/process")
        gather.say(result["speech"], voice="Polly.Joanna")
        response.append(gather)
        response.redirect("/voice/no-input")

    return _twiml(response)


@app.route("/voice/no-input", methods=["POST"])
def no_input():
    if not _validate_twilio(request):
        return Response("Forbidden", status=403)

    call_sid = request.form.get("CallSid", "unknown")
    _conversations.pop(call_sid, None)

    response = VoiceResponse()
    response.say(
        "I didn't catch that. Please call us back at (323) 348-6756 "
        "or walk into our store at 3025 Artesia Blvd, Torrance. Goodbye!",
        voice="Polly.Joanna",
    )
    response.hangup()
    return _twiml(response)


@app.route("/messages", methods=["GET"])
def view_messages():
    """Simple endpoint to view logged messages — protect with a reverse proxy in production."""
    from data_manager import DataManager
    dm = DataManager()
    msgs = dm.get_messages()
    lines = ["<h2>Messages</h2><ul>"]
    for m in reversed(msgs):
        lines.append(
            f"<li><b>{m.get('received_at','')}</b> — "
            f"{m.get('name','?')} ({m.get('caller','?')}): {m.get('message','')}</li>"
        )
    lines.append("</ul>")
    return "\n".join(lines)


@app.route("/appointments", methods=["GET"])
def view_appointments():
    from data_manager import DataManager
    dm = DataManager()
    appts = dm.get_appointments()
    lines = ["<h2>Appointments</h2><ul>"]
    for a in reversed(appts):
        lines.append(
            f"<li><b>{a.get('date','')} {a.get('time','')}</b> — "
            f"{a.get('name','?')} ({a.get('phone','?')}) — {a.get('service','')}</li>"
        )
    lines.append("</ul>")
    return "\n".join(lines)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
