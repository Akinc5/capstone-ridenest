def fake_tool_call(tool, input_args, callback_context) -> dict:
  v = callback_context.variables or {}
  args = input_args or {}
  dest = (args.get("destination") or "human").strip().lower()
  intent = (args.get("intent_tag") or v.get("intent_tag") or "").strip()
  fleet = (args.get("fleet_tag") or v.get("fleet") or "").strip()
  reason = (args.get("reason") or v.get("transfer_reason") or "").strip()
  
  disclaimer = ""
  if dest == "fleet" and not v.get("disclaimer_played", False):
    disclaimer = "Credits and lost items follow the fleet's terms."
    callback_context.variables["disclaimer_played"] = True
    
  callback_context.variables["transfer_reason"] = reason
  return {
      "status": "SUCCESS",
      "data": {
          "destination": dest,
          "intent_tag": intent,
          "fleet_tag": fleet,
          "reason": reason,
          "disclaimer": disclaimer,
          "is_simulated_demo": True,
          "handoff_summary": f"Simulated handoff to {dest}."
      },
      "message": f"Handoff payload built for {dest}."
  }
