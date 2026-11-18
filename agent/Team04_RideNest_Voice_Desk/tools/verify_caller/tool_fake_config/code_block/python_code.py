def fake_tool_call(tool, input_args, callback_context) -> dict:
  v = callback_context.variables or {}
  args = input_args or {}
  
  rider_id = (args.get("rider_id") or v.get("rider_id") or "RN4001").strip().upper().replace(" ", "").replace("-", "")
  
  if rider_id == "RN4003":
    callback_context.variables["verified"] = False
    callback_context.variables["rider_id"] = "RN4003"
    callback_context.variables["transfer_reason"] = "Account is blocked"
    return {"status": "BLOCKED", "verified": False, "is_blocked": True, "transfer_required": True, "message": "Account is blocked. Connecting to representative."}
    
  callback_context.variables["verified"] = True
  callback_context.variables["rider_id"] = rider_id
  callback_context.variables["verification_attempts"] = 0
  return {"status": "SUCCESS", "verified": True, "rider_id": rider_id, "transfer_required": False, "message": f"Verification successful for {rider_id}."}
