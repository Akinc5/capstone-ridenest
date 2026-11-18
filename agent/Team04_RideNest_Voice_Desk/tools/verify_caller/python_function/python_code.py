from typing import Dict, Any
import re

RIDERS_DB = {
    "RN4001": {"dob": "2000-04-12", "last4": "4101", "status": "ACTIVE"},
    "RN4002": {"dob": "1998-08-21", "last4": "4102", "status": "ACTIVE"},
    "RN4003": {"dob": "1995-02-15", "last4": "4103", "status": "BLOCKED"},
}

WORD_TO_DIGIT = {
    "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
    "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9"
}

ORDINALS = {
    "first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7,
    "eighth": 8, "ninth": 9, "tenth": 10, "eleventh": 11, "twelfth": 12, "thirteenth": 13,
    "fourteenth": 14, "fifteenth": 15, "sixteenth": 16, "seventeenth": 17, "eighteenth": 18,
    "nineteenth": 19, "twentieth": 20, "thirtieth": 30,
}
TEENS = {"ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
         "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19}
TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
        "eighty": 80, "ninety": 90}
UNITS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9}
_U = "|".join(UNITS)
_T = "|".join(TENS)
_TEEN = "|".join(TEENS)


def _two_digit(tens, unit):
  return TENS.get(tens, 0) + UNITS.get(unit or "", 0)


def normalize_text_digits(text: str) -> str:
  res = str(text or "").lower().replace(",", " ")
  _d = r"(zero|oh|one|two|three|four|five|six|seven|eight|nine|\d)"
  res = re.sub(r"\btriple " + _d + r"\b", r"\1 \1 \1", res)
  res = re.sub(r"\bdouble " + _d + r"\b", r"\1 \1", res)
  res = re.sub(r"\b(\d{1,2})(st|nd|rd|th)\b", r"\1", res)
  # Ordinal days: "twenty first", "twelfth"
  res = re.sub(r"\b(twenty|thirty)[ -](first|second|third|fourth|fifth|sixth|seventh|eighth|ninth)\b",
               lambda m: str(TENS[m.group(1)] + ORDINALS[m.group(2)]), res)
  for w, n in ORDINALS.items():
    res = re.sub(r"\b" + w + r"\b", str(n), res)
  # Years: "nineteen ninety eight", "two thousand", "two thousand and five"
  res = re.sub(r"\bnineteen (" + _T + r")(?:[ -](" + _U + r"))?\b",
               lambda m: str(1900 + _two_digit(m.group(1), m.group(2))), res)
  res = re.sub(r"\btwo thousand(?: and)?(?: (" + _U + "|" + _TEEN + r"))?\b",
               lambda m: str(2000 + (UNITS.get(m.group(1) or "", 0) or TEENS.get(m.group(1) or "", 0))), res)
  res = re.sub(r"\b(" + _T + r")[ -](" + _U + r")\b", lambda m: str(_two_digit(m.group(1), m.group(2))), res)
  for w, n in TEENS.items():
    res = re.sub(r"\b" + w + r"\b", str(n), res)
  res = re.sub(r"\b(" + _T + r")\b", lambda m: str(TENS[m.group(1)]), res)
  res = re.sub(r"\boh\b", "0", res)
  for w, d in WORD_TO_DIGIT.items():
    res = re.sub(r"\b" + w + r"\b", d, res)
  return res

def normalize_dob(dob_raw: str) -> str:
  s = normalize_text_digits(dob_raw).replace("/", "-").replace(".", "-").strip()
  m = re.search(r"(\d{4})[- ](\d{1,2})[- ](\d{1,2})", s)
  if m:
    return f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}"
  m2 = re.search(r"(\d{1,2})[- ](\d{1,2})[- ](\d{4})", s)
  if m2:
    return f"{m2.group(3)}-{int(m2.group(2)):02d}-{int(m2.group(1)):02d}"
  months = {"jan": "01", "feb": "02", "mar": "03", "apr": "04", "may": "05", "jun": "06",
            "jul": "07", "aug": "08", "sep": "09", "oct": "10", "nov": "11", "dec": "12"}
  for mname, mnum in months.items():
    if mname in s:
      nums = re.findall(r"\d+", s)
      if len(nums) >= 2:
        year = next((n for n in nums if len(n) == 4), "")
        day = next((n for n in nums if len(n) <= 2), "")
        if year and day:
          return f"{year}-{mnum}-{int(day):02d}"
  return s

def normalize_last4(last4_raw: str) -> str:
  s = normalize_text_digits(last4_raw)
  digits = re.findall(r"\d", s)
  if len(digits) >= 4:
    return "".join(digits[-4:])
  return "".join(digits)

def verify_caller(
    rider_id: str = "",
    dob: str = "",
    last4: str = ""
) -> dict:
  """Verifies the caller identity using 3-factor authentication: rider ID, DOB, and phone last 4 digits.

  Args:
    rider_id: (REQUIRED) Rider ID (e.g. RN4001).
    dob: (REQUIRED) Date of birth (YYYY-MM-DD or spoken format).
    last4: (REQUIRED) Last four digits of registered phone number.

  Returns:
    dict: Verification outcome, status, and retry or transfer recommendation.
  """
  try:
    clean_id = normalize_text_digits(rider_id).strip().upper().replace(" ", "").replace("-", "").replace(".", "")
    clean_dob = normalize_dob(dob)
    clean_last4 = normalize_last4(last4)

    attempts = int(get_variable("verification_attempts", 0)) + 1
    set_variable("verification_attempts", attempts)

    if clean_id not in RIDERS_DB:
      if attempts >= 3:
        set_variable("verified", False)
        set_variable("transfer_reason", "Verification failed after maximum attempts")
        return {
            "status": "FAILED",
            "verified": False,
            "attempts": attempts,
            "transfer_required": True,
            "transfer_reason": "Verification failed after maximum attempts",
            "message": "We could not verify your details after multiple attempts. Connecting you to a representative."
        }
      return {
          "status": "RETRY",
          "verified": False,
          "attempts": attempts,
          "transfer_required": False,
          "message": "The details provided could not be verified. Please provide your rider ID, date of birth, and the last four digits of your registered phone number."
      }

    rider = RIDERS_DB[clean_id]

    if rider["status"] == "BLOCKED" and rider["dob"] == clean_dob and rider["last4"] == clean_last4:
      set_variable("verified", False)
      set_variable("rider_id", clean_id)
      set_variable("transfer_reason", "Account is blocked")
      return {
          "status": "BLOCKED",
          "verified": False,
          "is_blocked": True,
          "attempts": attempts,
          "transfer_required": True,
          "transfer_reason": "Account is blocked",
          "message": "Your account requires administrative review. Connecting you to a representative now."
      }

    if rider["dob"] == clean_dob and rider["last4"] == clean_last4:
      set_variable("verified", True)
      set_variable("rider_id", clean_id)
      set_variable("verification_attempts", 0)
      return {
          "status": "SUCCESS",
          "verified": True,
          "rider_id": clean_id,
          "attempts": attempts,
          "transfer_required": False,
          "message": f"Verification successful for rider {clean_id}."
      }

    if attempts >= 3:
      set_variable("verified", False)
      set_variable("transfer_reason", "Verification failed after maximum attempts")
      return {
          "status": "FAILED",
          "verified": False,
          "attempts": attempts,
          "transfer_required": True,
          "transfer_reason": "Verification failed after maximum attempts",
          "message": "We could not verify your details after multiple attempts. Connecting you to a representative."
      }

    return {
        "status": "RETRY",
        "verified": False,
        "attempts": attempts,
        "transfer_required": False,
        "message": "The details provided could not be verified. Please provide your rider ID, date of birth, and the last four digits of your registered phone number."
    }
  except Exception as e:
    return {"status": "ERROR", "message": str(e), "transfer_required": True}
