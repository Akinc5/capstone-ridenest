from typing import Optional, Any

def after_tool_callback(
    callback_context: CallbackContext, tool: Any, function_call: Any, tool_output: Any
) -> Optional[dict]:
  tool_name = ""
  if isinstance(tool, dict):
    tool_name = tool.get("name", "")
  elif hasattr(tool, "name"):
    tool_name = str(getattr(tool, "name", ""))
    
  fn_name = ""
  if isinstance(function_call, dict):
    fn_name = function_call.get("name", "")
  elif hasattr(function_call, "name"):
    fn_name = str(getattr(function_call, "name", ""))
    
  if "build_handoff" in tool_name or "build_handoff" in fn_name:
    data = {}
    if isinstance(tool_output, dict):
      data = tool_output.get("data", {})
    reason = data.get("reason", "") if isinstance(data, dict) else ""
    if reason:
      callback_context.set_variable("transfer_reason", str(reason))
  return None
