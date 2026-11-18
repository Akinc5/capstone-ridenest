def fake_tool_call(tool, input_args, callback_context) -> dict:
  v = callback_context.variables or {}
  mc = v.get("mock_context") if isinstance(v.get("mock_context"), dict) else {}
  args = input_args or {}
  
  ride_id = (args.get("ride_id") or v.get("ride_id") or "R401").strip().upper().replace(" ", "").replace("-", "")
  verified = v.get("verified", False)
  rider_id = v.get("rider_id", "RN4001")
  
  # Check if mock_context has specific ride override
  custom_rides = mc.get("rides") or v.get("rides") or {}
  if isinstance(custom_rides, dict) and ride_id in custom_rides:
    ride_data = custom_rides[ride_id]
    callback_context.variables["fleet"] = ride_data.get("fleet", "CityGo Cabs")
    callback_context.variables["ride_id"] = ride_id
    return {"status": "SUCCESS", "ride_id": ride_id, **ride_data}
    
  # Standard mocked database
  if not verified:
    return {"status": "UNVERIFIED", "transfer_required": True, "message": "Verification is required."}
    
  if ride_id == "R414" and rider_id != "RN4002":
    return {"status": "LOOKUP_FAILURE", "transfer_required": True, "transfer_reason": "Ride does not belong to verified rider", "message": "System lookup failure. Connecting to representative."}
  if ride_id not in ["R401", "R402", "R403", "R404", "R405", "R406", "R407", "R408", "R409", "R410", "R411", "R412", "R413", "R414"]:
    return {"status": "LOOKUP_FAILURE", "transfer_required": True, "transfer_reason": "Ride not found", "message": "System lookup failure. Connecting to representative."}
    
  fleet_map = {
      "R401": "CityGo Cabs", "R402": "AutoMitra", "R403": "CityGo Cabs", "R404": "CityGo Cabs",
      "R405": "MetroRide Pool", "R406": "MetroRide Pool", "R407": "AutoMitra Plus",
      "R408": "QuickKite Bikes", "R409": "CityGo Cabs", "R410": "CityGo Cabs",
      "R411": "CityGo Cabs", "R412": "CityGo Cabs", "R413": "CityGo Cabs", "R414": "CityGo Cabs"
  }
  display_fleet = fleet_map.get(ride_id, "CityGo Cabs")
  supported = ride_id not in ["R406", "R408"]
  transfer_req = not supported
  
  callback_context.variables["fleet"] = display_fleet
  callback_context.variables["ride_id"] = ride_id
  
  return {
      "status": "SUCCESS",
      "ride_id": ride_id,
      "fleet": display_fleet,
      "supported": supported,
      "app_fare": 900 if ride_id == "R401" else (300 if ride_id == "R411" else (200 if ride_id == "R412" else 500)),
      "estimate_fare": 200 if ride_id == "R401" else 300,
      "distance_km": None if ride_id == "R409" else 12,
      "route_recorded": False if ride_id == "R410" else True,
      "already_credited": True if ride_id == "R413" else False,
      "transfer_required": transfer_req,
      "message": f"Ride {ride_id} retrieved successfully."
  }
