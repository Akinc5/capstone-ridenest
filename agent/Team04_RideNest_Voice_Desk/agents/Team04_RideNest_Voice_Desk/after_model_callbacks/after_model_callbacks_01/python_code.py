from typing import Optional

def after_model_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
  if not llm_response or not llm_response.content or not llm_response.content.parts:
    return None
  parts = list(llm_response.content.parts)
  has_end_session = any(p.has_function_call("end_session") for p in parts)
  if not has_end_session:
    return None
  # Check if response already has text or is a crisis message
  full_text = " ".join(p.text_or_transcript() or "" for p in parts).strip()
  if full_text or "Tele-MANAS" in full_text or "14416" in full_text or "112" in full_text:
    return None
  farewell = Part.from_text(text="Thank you for calling RideNest Voice Desk. Have a wonderful day.")
  return LlmResponse.from_parts(parts=[farewell] + parts)
