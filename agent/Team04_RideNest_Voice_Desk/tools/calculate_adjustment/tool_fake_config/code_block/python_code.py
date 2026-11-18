def fake_tool_call(tool, input_args, callback_context) -> dict:
  v = callback_context.variables or {}
  args = input_args or {}
  ride_id = (args.get("ride_id") or v.get("ride_id") or "R401").strip().upper().replace(" ", "").replace("-", "")
  intent_type = (args.get("intent_type") or v.get("intent_tag") or "fare").strip().lower()
  item_recovered = bool(args.get("item_recovered", False))
  
  if intent_type == "complaint":
    return {"status": "SUCCESS", "intent_type": "complaint", "credit_quote_rupees": 0, "fee_rupees": 0, "message": "Complaint recorded."}
    
  if "lost" in intent_type:
    fee = 0
    if item_recovered:
      fee = 0 if ride_id == "R401" else (50 if ride_id == "R402" else 100)
    return {"status": "SUCCESS", "intent_type": "lost item", "item_recovered": item_recovered, "lost_item_pickup_fee_rupees": fee, "quote_note": "Academic demo quote", "message": f"Lost item fee is {fee} rupees."}
    
  # Fare
  if ride_id == "R413":
    return {"status": "ALREADY_CREDITED", "credit_quote_rupees": 0, "message": "This ride has already been credited. No duplicate credit can be issued."}
  if ride_id in ["R405", "R406", "R407"]:
    return {"status": "FUTURE_RIDE", "credit_quote_rupees": 0, "message": "Future rides are not eligible for monetary adjustments."}
  if ride_id == "R404":
    callback_context.variables["transfer_reason"] = "Ride older than 7 days"
    return {"status": "EXPIRED", "credit_quote_rupees": 0, "transfer_required": True, "message": "Ride older than 7 days. Connecting to representative."}
    
  credit = 500 if ride_id == "R401" else (100 if ride_id == "R402" else (50 if ride_id == "R403" else 0))
  return {
      "status": "SUCCESS",
      "intent_type": "fare",
      "credit_quote_rupees": credit,
      "quote_note": "Academic demo quote",
      "message": f"Credit adjustment quote is {credit} rupees."
  }
