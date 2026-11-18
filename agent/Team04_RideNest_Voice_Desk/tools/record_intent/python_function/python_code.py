from typing import Dict, Any

VALID = {
    "fare": "fare", "fare dispute": "fare", "one": "fare", "1": "fare",
    "lost item": "lost item", "lost": "lost item", "two": "lost item", "2": "lost item",
    "complaint": "complaint", "driver complaint": "complaint", "three": "complaint", "3": "complaint",
}


def record_intent(intent: str = "") -> dict:
  """Records the caller's intent, or counts an unclear answer (two re-attempts, then a human agent).

  Args:
    intent: 'fare', 'lost item', 'complaint', the spoken choice 'one'/'two'/'three', or 'unclear'.

  Returns:
    dict: SET with the intent tag, RETRY with the attempt count, or TRANSFER after the third unclear answer.
  """
  try:
    key = (intent or "").strip().lower()
    if key in VALID:
      tag = VALID[key]
      set_variable("intent_tag", tag)
      set_variable("intent_attempts", 0)
      return {"status": "SET", "intent_tag": tag, "transfer_required": False}
    attempts = int(get_variable("intent_attempts", 0)) + 1
    set_variable("intent_attempts", attempts)
    if attempts >= 3:
      set_variable("transfer_reason", "Intent unclear after two re-attempts")
      return {"status": "TRANSFER", "attempts": attempts, "intent_tag": "", "transfer_required": True,
              "message": "I'm sorry I couldn't understand. Let me connect you with a person."}
    return {"status": "RETRY", "attempts": attempts, "transfer_required": False,
            "message": "Is this about a fare, a lost item, or a driver complaint? You can also say one, two or three."}
  except Exception as e:
    return {"status": "ERROR", "message": str(e), "transfer_required": True}
