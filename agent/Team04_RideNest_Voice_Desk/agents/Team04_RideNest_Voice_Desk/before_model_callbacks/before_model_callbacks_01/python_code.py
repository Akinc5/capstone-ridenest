from typing import Optional

def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
  if not callback_context.variables.get("is_initialized"):
    callback_context.set_variable("is_initialized", True)
    if "now_override" not in callback_context.variables:
      callback_context.set_variable("now_override", "2026-11-10T09:00:00")
    if "verified" not in callback_context.variables:
      callback_context.set_variable("verified", False)
    if "verification_attempts" not in callback_context.variables:
      callback_context.set_variable("verification_attempts", 0)
    if "intent_attempts" not in callback_context.variables:
      callback_context.set_variable("intent_attempts", 0)
    if "disclaimer_played" not in callback_context.variables:
      callback_context.set_variable("disclaimer_played", False)
  return None
