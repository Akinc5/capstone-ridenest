from typing import Dict, Any

RIDES_LOGS = {
    "R401": {"distance_km": 18, "route_recorded": True},
    "R402": {"distance_km": 12, "route_recorded": True},
    "R403": {"distance_km": 12, "route_recorded": True},
    "R404": {"distance_km": 12, "route_recorded": True},
    "R405": {"distance_km": 12, "route_recorded": True},
    "R406": {"distance_km": 12, "route_recorded": True},
    "R407": {"distance_km": 12, "route_recorded": True},
    "R408": {"distance_km": 12, "route_recorded": True},
    "R409": {"distance_km": None, "route_recorded": True},
    "R410": {"distance_km": 12, "route_recorded": False},
    "R411": {"distance_km": 12, "route_recorded": True},
    "R412": {"distance_km": 12, "route_recorded": True},
    "R413": {"distance_km": 12, "route_recorded": True},
    "R414": {"distance_km": 12, "route_recorded": True},
    "R415": {"distance_km": 14, "route_recorded": True},
}

def check_trip_log(ride_id: str = "") -> dict:
  """Verifies route logs and telemetry distance for fare dispute investigations.

  Args:
    ride_id: (REQUIRED) The identifier of the ride being disputed.

  Returns:
    dict: Trip log status (CONTINUE, NO_ROUTE, or MISSING_DISTANCE).
  """
  try:
    clean_id = (ride_id or "").strip().upper().replace(" ", "").replace("-", "")

    verified = get_variable("verified", False)
    if not verified:
      return {
          "status": "UNVERIFIED",
          "transfer_required": True,
          "message": "Caller must be verified before accessing trip logs."
      }

    if clean_id not in RIDES_LOGS:
      return {
          "status": "LOOKUP_FAILURE",
          "transfer_required": True,
          "transfer_reason": "Trip log record not found",
          "message": "Trip log could not be retrieved due to a system lookup failure. Connecting you with a representative."
      }

    log = RIDES_LOGS[clean_id]

    if not log["route_recorded"]:
      set_variable("transfer_reason", "No route recorded for trip")
      return {
          "status": "NO_ROUTE",
          "route_recorded": False,
          "transfer_required": True,
          "transfer_reason": "No route recorded for trip",
          "message": "No route was recorded for this trip. Connecting you with a representative."
      }

    if log["distance_km"] is None:
      return {
          "status": "MISSING_DISTANCE",
          "route_recorded": True,
          "distance_km": None,
          "transfer_required": False,
          "message": "Trip distance is missing due to a technical recording issue. Please note that I cannot confirm whether the fare charged was correct or incorrect."
      }

    return {
        "status": "CONTINUE",
        "route_recorded": True,
        "distance_km": log["distance_km"],
        "transfer_required": False,
        "message": f"Trip log verified. Recorded distance is {log['distance_km']} kilometers."
    }
  except Exception as e:
    return {"status": "ERROR", "message": str(e), "transfer_required": True}
