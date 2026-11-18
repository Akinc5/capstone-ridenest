from typing import Dict, Any
import datetime
from decimal import Decimal, ROUND_HALF_UP

RIDES_DATA = {
    "R401": {"ends_at": "2026-11-10T08:00:00", "app_fare": 900, "estimate_fare": 200, "already_credited": False},
    "R402": {"ends_at": "2026-11-09T09:00:00", "app_fare": 500, "estimate_fare": 300, "already_credited": False},
    "R403": {"ends_at": "2026-11-07T09:00:00", "app_fare": 500, "estimate_fare": 300, "already_credited": False},
    "R404": {"ends_at": "2026-11-03T09:00:00", "app_fare": 500, "estimate_fare": 300, "already_credited": False},
    "R405": {"ends_at": "2026-12-31T09:00:00", "app_fare": 500, "estimate_fare": 300, "already_credited": False},
    "R406": {"ends_at": "2027-01-01T09:00:00", "app_fare": 500, "estimate_fare": 300, "already_credited": False},
    "R407": {"ends_at": "2027-01-01T09:00:00", "app_fare": 500, "estimate_fare": 300, "already_credited": False},
    "R408": {"ends_at": "2026-11-10T08:00:00", "app_fare": 500, "estimate_fare": 300, "already_credited": False},
    "R409": {"ends_at": "2026-11-10T08:00:00", "app_fare": 500, "estimate_fare": 300, "already_credited": False},
    "R410": {"ends_at": "2026-11-10T08:00:00", "app_fare": 500, "estimate_fare": 300, "already_credited": False},
    "R411": {"ends_at": "2026-11-10T08:00:00", "app_fare": 300, "estimate_fare": 300, "already_credited": False},
    "R412": {"ends_at": "2026-11-10T08:00:00", "app_fare": 200, "estimate_fare": 300, "already_credited": False},
    "R413": {"ends_at": "2026-11-10T08:00:00", "app_fare": 500, "estimate_fare": 300, "already_credited": True},
    "R414": {"ends_at": "2026-11-10T08:00:00", "app_fare": 500, "estimate_fare": 300, "already_credited": False},
    "R415": {"ends_at": "2026-11-06T09:00:00", "app_fare": 502, "estimate_fare": 300, "already_credited": False},
}

# Rides whose trip log cannot support a fare credit (mirrors check_trip_log data).
TRIP_LOG_UNUSABLE = {
    "R409": "Route distance unknown (technical)",
    "R410": "No route recorded for trip",
}


def calculate_adjustment(
    ride_id: str = "",
    intent_type: str = "fare",
    item_recovered: bool = False
) -> dict:
  """Calculates credit adjustment quotes or lost item recovery fees.

  Args:
    ride_id: (REQUIRED) The identifier of the ride.
    intent_type: The issue category: 'fare', 'lost item', or 'complaint'.
    item_recovered: Whether a lost item was recovered (applies only to lost item).

  Returns:
    dict: Exact monetary quote and fee calculations for the academic demo.
  """
  try:
    clean_id = (ride_id or "").strip().upper().replace(" ", "").replace("-", "")

    verified = get_variable("verified", False)
    if not verified:
      return {
          "status": "UNVERIFIED",
          "transfer_required": True,
          "message": "Caller must be verified before calculating adjustments."
      }

    if clean_id not in RIDES_DATA:
      return {
          "status": "LOOKUP_FAILURE",
          "transfer_required": True,
          "message": "Ride record not found for calculation."
      }

    ride = RIDES_DATA[clean_id]
    now_str = get_variable("now_override", "2026-11-10T09:00:00")
    now_dt = datetime.datetime.fromisoformat(now_str)
    ends_dt = datetime.datetime.fromisoformat(ride["ends_at"])
    age_hours = (now_dt - ends_dt).total_seconds() / 3600.0
    set_variable("ride_age_hours", float(age_hours))

    # Negative age = future ride
    if age_hours < 0:
      return {
          "status": "FUTURE_RIDE",
          "credit_quote_rupees": 0,
          "fee_rupees": 0,
          "ride_age_hours": age_hours,
          "transfer_required": False,
          "message": "This ride date is in the future. Future rides are not eligible for monetary adjustments."
      }

    intent_clean = (intent_type or "fare").strip().lower()

    if intent_clean == "complaint":
      return {
          "status": "SUCCESS",
          "intent_type": "complaint",
          "credit_quote_rupees": 0,
          "fee_rupees": 0,
          "ride_age_hours": age_hours,
          "transfer_required": False,
          "message": "Your complaint has been recorded for fleet quality review. No monetary adjustment is required."
      }

    if intent_clean == "lost item" or intent_clean == "lost_item":
      if not item_recovered:
        return {
            "status": "SUCCESS",
            "intent_type": "lost item",
            "item_recovered": False,
            "lost_item_pickup_fee_rupees": 0,
            "ride_age_hours": age_hours,
            "transfer_required": False,
            "message": "Lost item report filed. No pickup fee applies since the item has not been recovered yet."
        }
      else:
        if age_hours < 24:
          fee = 0
        elif age_hours < 72:
          fee = 50
        elif age_hours < 168:
          fee = 100
        else:
          set_variable("transfer_reason", "Ride older than 7 days")
          return {
              "status": "EXPIRED",
              "intent_type": "lost item",
              "lost_item_pickup_fee_rupees": 0,
              "ride_age_hours": age_hours,
              "transfer_required": True,
              "transfer_reason": "Ride older than 7 days",
              "message": "This ride was completed more than seven days ago. Connecting you with a representative."
          }
        return {
            "status": "SUCCESS",
            "intent_type": "lost item",
            "item_recovered": True,
            "lost_item_pickup_fee_rupees": fee,
            "ride_age_hours": age_hours,
            "transfer_required": False,
            "quote_note": "This is an academic demo quote, not a real payment.",
            "message": f"Lost item recovered. The pickup fee is {fee} rupees."
        }

    # Fare dispute: never credit when the trip log cannot support it (rule: unknown distance -> technical message)
    if clean_id in TRIP_LOG_UNUSABLE:
      reason = TRIP_LOG_UNUSABLE[clean_id]
      set_variable("transfer_reason", reason)
      return {
          "status": "TRIP_LOG_UNUSABLE",
          "credit_quote_rupees": None,
          "ride_age_hours": age_hours,
          "transfer_required": True,
          "transfer_reason": reason,
          "message": "I can't work out a credit for this ride because of a technical issue with the trip record, so I'm connecting you with a person."
      }

    if ride["already_credited"]:
      return {
          "status": "ALREADY_CREDITED",
          "credit_quote_rupees": 0,
          "ride_age_hours": age_hours,
          "transfer_required": False,
          "message": "This ride has already been credited. No duplicate credit can be issued."
      }

    extra = max(ride["app_fare"] - ride["estimate_fare"], 0)

    if age_hours < 24:
      raw_credit = min(extra * 1.0, 500.0)
    elif age_hours < 72:
      raw_credit = extra * 0.5
    elif age_hours < 168:
      raw_credit = extra * 0.25
    else:
      set_variable("transfer_reason", "Ride older than 7 days")
      return {
          "status": "EXPIRED",
          "intent_type": "fare",
          "credit_quote_rupees": 0,
          "ride_age_hours": age_hours,
          "transfer_required": True,
          "transfer_reason": "Ride older than 7 days",
          "message": "This ride was completed more than seven days ago. Connecting you with a representative."
      }

    # Round half-up to whole rupee
    credit_rounded = int(Decimal(str(raw_credit)).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

    return {
        "status": "SUCCESS",
        "intent_type": "fare",
        "app_fare": ride["app_fare"],
        "estimate_fare": ride["estimate_fare"],
        "extra_fare": extra,
        "credit_quote_rupees": credit_rounded,
        "ride_age_hours": age_hours,
        "transfer_required": False,
        "quote_note": "This is an academic demo quote, not a real payment.",
        "next_action": "In this same turn, after stating the quote, call build_handoff with destination 'fleet', intent_tag 'fare' and the ride's fleet as fleet_tag.",
        "message": f"Based on our calculation, your credit adjustment quote is {credit_rounded} rupees."
    }
  except Exception as e:
    return {"status": "ERROR", "message": str(e), "transfer_required": True}
