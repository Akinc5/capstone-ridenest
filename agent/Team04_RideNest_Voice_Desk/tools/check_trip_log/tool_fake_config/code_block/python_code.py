def fake_tool_call(tool, input_args, callback_context) -> dict:
  v = callback_context.variables or {}
  args = input_args or {}
  ride_id = (args.get("ride_id") or v.get("ride_id") or "R401").strip().upper().replace(" ", "").replace("-", "")
  
  if ride_id == "R410":
    callback_context.variables["transfer_reason"] = "No route recorded for trip"
    return {"status": "NO_ROUTE", "route_recorded": False, "transfer_required": True, "message": "No route was recorded for this trip. Connecting you with a representative."}
  if ride_id == "R409":
    return {"status": "MISSING_DISTANCE", "route_recorded": True, "distance_km": None, "transfer_required": False, "message": "Trip distance is missing due to a technical recording issue. I cannot confirm whether the fare charged was correct or incorrect."}
    
  return {"status": "CONTINUE", "route_recorded": True, "distance_km": 18 if ride_id == "R401" else 12, "transfer_required": False, "message": "Trip log verified."}
