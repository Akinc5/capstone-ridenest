from typing import Dict, Any

def get_ride_day_advisory(
    city: str = "Delhi",
    latitude: float = 28.6139,
    longitude: float = 77.2090
) -> dict:
  """Fetches brief ride-day advisory and weather forecast from institutional public API.

  Args:
    city: Name of the city for advisory.
    latitude: Latitude coordinate for advisory location.
    longitude: Longitude coordinate for advisory location.

  Returns:
    dict: Ride day conditions, temperature, and advisory statement.
  """
  try:
    params = {
        "latitude": str(latitude),
        "longitude": str(longitude),
        "current_weather": "true"
    }
    resp = ces_requests.get("https://api.open-meteo.com/v1/forecast", params=params)
    if resp.status_code == 200:
      data = resp.json()
      curr = data.get("current_weather", {})
      temp = curr.get("temperature", 28.0)
      wind = curr.get("windspeed", 10.0)
      return {
          "status": "SUCCESS",
          "city": city,
          "temperature_celsius": temp,
          "windspeed_kmh": wind,
          "advisory": f"Current weather in {city} is {temp} degrees Celsius. Ride conditions are normal.",
          "is_public_api": True
      }
    return {
        "status": "FALLBACK",
        "city": city,
        "advisory": f"Ride conditions in {city} are clear and operational.",
        "is_public_api": True
    }
  except Exception as e:
    return {
        "status": "FALLBACK",
        "city": city,
        "advisory": f"Ride conditions in {city} are normal. Safe travels.",
        "is_public_api": True
    }
