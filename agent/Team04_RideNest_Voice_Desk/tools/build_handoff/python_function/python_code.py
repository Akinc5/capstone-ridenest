from typing import Dict, Any

def build_handoff(
    destination: str = "human",
    intent_tag: str = "",
    fleet_tag: str = "",
    reason: str = ""
) -> dict:
  """Builds structured handoff telemetry for simulated routing to a human or fleet partner.

  Args:
    destination: Target endpoint: 'human' or 'fleet'.
    intent_tag: Best known intent: 'fare', 'lost item', 'complaint', or empty.
    fleet_tag: Identified fleet name or empty.
    reason: Contextual reason for handoff.

  Returns:
    dict: Structured handoff payload and policy disclaimer when applicable.
  """
  try:
    dest_clean = (destination or "human").strip().lower()
    intent_clean = (intent_tag or get_variable("intent_tag", "")).strip()
    fleet_clean = (fleet_tag or get_variable("fleet", "")).strip()
    reason_clean = (reason or get_variable("transfer_reason", "")).strip()

    # Disclaimer rule: exactly once if destination is fleet; no disclaimer for human
    disclaimer = ""
    disclaimer_played = get_variable("disclaimer_played", False)

    if dest_clean == "fleet":
      if not disclaimer_played:
        disclaimer = "Credits and lost items follow the fleet's terms."
        set_variable("disclaimer_played", True)
    else:
      disclaimer = ""

    set_variable("transfer_reason", reason_clean)

    payload = {
        "destination": dest_clean,
        "intent_tag": intent_clean,
        "fleet_tag": fleet_clean,
        "reason": reason_clean,
        "disclaimer": disclaimer,
        "is_simulated_demo": True,
        "handoff_summary": f"Simulated handoff to {dest_clean}. Intent: {intent_clean or 'unspecified'}, Fleet: {fleet_clean or 'unassigned'}, Reason: {reason_clean or 'general'}."
    }

    return {
        "status": "SUCCESS",
        "data": payload,
        "message": f"Handoff payload built for {dest_clean}."
    }
  except Exception as e:
    return {"status": "ERROR", "message": str(e)}
