from typing import Dict, Any
import datetime

RIDES_DB = {
    "R401": {"fleet": "CityGo Cabs", "ends_at": "2026-11-10T08:00:00", "app_fare": 900, "estimate_fare": 200, "distance_km": 18, "route_recorded": True, "already_credited": False, "rider_id": "RN4001"},
    "R402": {"fleet": "AutoMitra", "ends_at": "2026-11-09T09:00:00", "app_fare": 500, "estimate_fare": 300, "distance_km": 12, "route_recorded": True, "already_credited": False, "rider_id": "RN4001"},
    "R403": {"fleet": "CityGo", "ends_at": "2026-11-07T09:00:00", "app_fare": 500, "estimate_fare": 300, "distance_km": 12, "route_recorded": True, "already_credited": False, "rider_id": "RN4001"},
    "R404": {"fleet": "CityGo", "ends_at": "2026-11-03T09:00:00", "app_fare": 500, "estimate_fare": 300, "distance_km": 12, "route_recorded": True, "already_credited": False, "rider_id": "RN4001"},
    "R405": {"fleet": "MetroRide Pool", "ends_at": "2026-12-31T09:00:00", "app_fare": 500, "estimate_fare": 300, "distance_km": 12, "route_recorded": True, "already_credited": False, "rider_id": "RN4001"},
    "R406": {"fleet": "MetroRide Pool", "ends_at": "2027-01-01T09:00:00", "app_fare": 500, "estimate_fare": 300, "distance_km": 12, "route_recorded": True, "already_credited": False, "rider_id": "RN4001"},
    "R407": {"fleet": "AutoMitra", "ends_at": "2027-01-01T09:00:00", "app_fare": 500, "estimate_fare": 300, "distance_km": 12, "route_recorded": True, "already_credited": False, "rider_id": "RN4001"},
    "R408": {"fleet": "QuickKite Bikes", "ends_at": "2026-11-10T08:00:00", "app_fare": 500, "estimate_fare": 300, "distance_km": 12, "route_recorded": True, "already_credited": False, "rider_id": "RN4001"},
    "R409": {"fleet": "CityGo", "ends_at": "2026-11-10T08:00:00", "app_fare": 500, "estimate_fare": 300, "distance_km": None, "route_recorded": True, "already_credited": False, "rider_id": "RN4001"},
    "R410": {"fleet": "CityGo", "ends_at": "2026-11-10T08:00:00", "app_fare": 500, "estimate_fare": 300, "distance_km": 12, "route_recorded": False, "already_credited": False, "rider_id": "RN4001"},
    "R411": {"fleet": "CityGo", "ends_at": "2026-11-10T08:00:00", "app_fare": 300, "estimate_fare": 300, "distance_km": 12, "route_recorded": True, "already_credited": False, "rider_id": "RN4001"},
    "R412": {"fleet": "CityGo", "ends_at": "2026-11-10T08:00:00", "app_fare": 200, "estimate_fare": 300, "distance_km": 12, "route_recorded": True, "already_credited": False, "rider_id": "RN4001"},
    "R413": {"fleet": "CityGo", "ends_at": "2026-11-10T08:00:00", "app_fare": 500, "estimate_fare": 300, "distance_km": 12, "route_recorded": True, "already_credited": True, "rider_id": "RN4001"},
    "R414": {"fleet": "CityGo", "ends_at": "2026-11-10T08:00:00", "app_fare": 500, "estimate_fare": 300, "distance_km": 12, "route_recorded": True, "already_credited": False, "rider_id": "RN4002"},
    "R415": {"fleet": "CityGo", "ends_at": "2026-11-06T09:00:00", "app_fare": 502, "estimate_fare": 300, "distance_km": 14, "route_recorded": True, "already_credited": False, "rider_id": "RN4001"},
}

DIGIT_WORDS = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"]
ORDINAL_DAYS = ["", "first", "second", "third", "fourth", "fifth", "sixth", "seventh", "eighth", "ninth", "tenth",
                "eleventh", "twelfth", "thirteenth", "fourteenth", "fifteenth", "sixteenth", "seventeenth",
                "eighteenth", "nineteenth", "twentieth", "twenty-first", "twenty-second", "twenty-third",
                "twenty-fourth", "twenty-fifth", "twenty-sixth", "twenty-seventh", "twenty-eighth",
                "twenty-ninth", "thirtieth", "thirty-first"]
MONTHS = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September",
          "October", "November", "December"]


def spell_id(value: str) -> str:
  """'RN4001' -> 'R N four zero zero one' (voice rule V3)."""
  return " ".join(DIGIT_WORDS[int(c)] if c.isdigit() else c for c in str(value))


def spoken_date(iso: str) -> str:
  """'2026-11-10T08:00:00' -> 'the tenth of November 2026'."""
  d = datetime.datetime.fromisoformat(iso)
  return f"the {ORDINAL_DAYS[d.day]} of {MONTHS[d.month]} {d.year}"


def lookup_ride(ride_id: str = "") -> dict:
  """Retrieves trip information and fleet eligibility for a verified caller.

  Args:
    ride_id: (REQUIRED) The unique identifier of the ride (e.g. R401).

  Returns:
    dict: Ride details including fleet, fare, age, and fleet support status.
  """
  try:
    clean_id = (ride_id or "").strip().upper()
    # Normalize formats like 'r-401' or 'r 401'
    clean_id = clean_id.replace(" ", "").replace("-", "")

    verified = get_variable("verified", False)
    rider_id = get_variable("rider_id", "")

    if not verified or not rider_id:
      return {
          "status": "UNVERIFIED",
          "transfer_required": True,
          "transfer_reason": "Caller is not verified",
          "message": "Verification is required before accessing ride details."
      }

    if clean_id not in RIDES_DB:
      return {
          "status": "LOOKUP_FAILURE",
          "transfer_required": True,
          "transfer_reason": "Ride lookup failed or ride not found",
          "message": "I could not retrieve your ride details due to a system lookup failure. I am connecting you with a representative now."
      }

    ride = RIDES_DB[clean_id]
    if ride["rider_id"] != rider_id:
      return {
          "status": "LOOKUP_FAILURE",
          "transfer_required": True,
          "transfer_reason": "Ride does not belong to verified rider",
          "message": "I could not retrieve your ride details due to a system lookup failure. I am connecting you with a representative now."
      }

    now_str = get_variable("now_override", "2026-11-10T09:00:00")
    now_dt = datetime.datetime.fromisoformat(now_str)
    ends_dt = datetime.datetime.fromisoformat(ride["ends_at"])
    age_hours = (now_dt - ends_dt).total_seconds() / 3600.0

    raw_fleet = ride["fleet"]
    ride_date_str = ride["ends_at"]

    # Fleet rules
    supported = True
    display_fleet = raw_fleet
    transfer_required = False
    transfer_reason = ""

    if "CityGo" in raw_fleet:
      supported = True
      display_fleet = "CityGo Cabs"
    elif "AutoMitra" in raw_fleet:
      supported = True
      if ride_date_str >= "2027-01-01T00:00:00":
        display_fleet = "AutoMitra Plus"
      else:
        display_fleet = "AutoMitra"
    elif "MetroRide" in raw_fleet:
      if ride_date_str <= "2026-12-31T23:59:59":
        supported = True
        display_fleet = "MetroRide Pool"
      else:
        supported = False
        display_fleet = "MetroRide Pool"
        transfer_required = True
        transfer_reason = "MetroRide Pool is unsupported on or after 2027-01-01"
    elif "QuickKite" in raw_fleet:
      supported = False
      display_fleet = "QuickKite Bikes"
      transfer_required = True
      transfer_reason = "QuickKite Bikes is never supported"

    set_variable("fleet", display_fleet)
    set_variable("ride_id", clean_id)
    set_variable("ride_age_hours", float(age_hours))
    if transfer_reason:
      set_variable("transfer_reason", transfer_reason)

    readback = (f"That's rider {spell_id(rider_id)}, ride {spell_id(clean_id)} on {spoken_date(ride['ends_at'])}, "
                f"with {display_fleet}. Is that right?")

    return {
        "status": "SUCCESS",
        "spoken_readback": readback,
        "ride_id": clean_id,
        "fleet": display_fleet,
        "supported": supported,
        "ends_at": ride["ends_at"],
        "app_fare": ride["app_fare"],
        "estimate_fare": ride["estimate_fare"],
        "distance_km": ride["distance_km"],
        "route_recorded": ride["route_recorded"],
        "already_credited": ride["already_credited"],
        "ride_age_hours": age_hours,
        "is_future": age_hours < 0,
        "transfer_required": transfer_required,
        "transfer_reason": transfer_reason,
        "message": f"Ride {clean_id} retrieved successfully for fleet {display_fleet}."
    }
  except Exception as e:
    return {"status": "ERROR", "message": str(e), "transfer_required": True}
