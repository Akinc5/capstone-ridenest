def fake_tool_call(tool, input_args, callback_context) -> dict:
  args = input_args or {}
  city = args.get("city", "Delhi")
  return {
      "status": "SUCCESS",
      "city": city,
      "temperature_celsius": 26.5,
      "windspeed_kmh": 8.0,
      "advisory": f"Current weather in {city} is 26.5 degrees Celsius. Ride conditions are normal.",
      "is_public_api": True
  }
