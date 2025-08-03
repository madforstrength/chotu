import json
from llm_interface import ask_llm
from github_utils import call_github_mcp_tool, get_github_mcp_tool_info
from kubectl_utils import run_kubectl_command


def main():
    print("""
   _____ _    _  ____ _______ _    _
  / ____| |  | |/ __ \__   __| |  | |
 | |    | |__| | |  | | | |  | |  | |
 | |    |  __  | |  | | | |  | |  | |
 | |____| |  | | |__| | | |  | |__| |
  \_____|_|  |_|\____/  |_|   \____/
""")
    print("Welcome to Chotu! Type your command (type 'exit' to quit):")
    github_tool_info = get_github_mcp_tool_info()

    def format_param_list(props, param_names):
        return ", ".join(
            [f"{name} ({props[name].get('type', 'unknown')})" for name in param_names]
        )

    def format_tool_entry(tool):
        schema = tool["inputSchema"]
        props = schema.get("properties", {})
        required = schema.get("required", [])
        optional = [name for name in props if name not in required]
        req_str = format_param_list(props, required) if required else "None"
        opt_str = format_param_list(props, optional) if optional else "None"
        return (
            f"- {tool['name']}:\n"
            f"    Description: {tool['description'] or 'No description'}\n"
            f"    Required Params: {req_str}\n"
            f"    Optional Params: {opt_str}"
        )

    github_tool_list = "\n".join([format_tool_entry(tool) for tool in github_tool_info])

    while True:
        user_input = input("> ").strip()
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        system_prompt = (
            "CRITICAL INSTRUCTION:\n"
            "NEVER guess, invent, or use placeholder values for required parameters. "
            "NEVER use values like 'octocat', 'test', 'hello-world', or 'example'.\n\n"
            "If any required parameter is missing, your ONLY valid response is:\n"
            "{'action': 'ask_user_for_missing_params', 'missing_params': ['param1', 'param2']}\n\n"
            "You must not fill in missing required parameters with dummy or fake values. If you do, the response will be REJECTED.\n\n"
            f"You are an agent that can run kubectl commands, call any of the following GitHub MCP tools, or answer questions directly.\n"
            f"Available GitHub MCP tools:\n{github_tool_list}\n\n"
            "IF any required parameters are missing, set 'action' to 'ask_user_for_missing_params' ONLY.\n"
            "NEVER proceed with 'call_github_tool' unless ALL required parameters are truly provided by the user.\n\n"
            "Respond ONLY in JSON with the following schema:\n"
            "{\n"
            "  'action': 'run_kubectl' | 'call_github_tool' | 'answer_directly' | 'ask_user_for_missing_params',\n"
            "  'command': '<kubectl command if applicable>',\n"
            "  'tool_name': '<GitHub MCP tool name if applicable>',\n"
            "  'params': <dict of parameters for the GitHub tool>,\n"
            "  'answer': '<answer if applicable>',\n"
            "  'missing_params': <list of missing parameter names if applicable>\n"
            "}\n\n"
            "Instruction: " + user_input
        )
        llm_response = ask_llm(system_prompt)
        print(f"[LLM Response]: {llm_response}")
        try:
            # Remove code block markers and whitespace
            cleaned = llm_response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.lstrip("`").lstrip("json").strip()
            if cleaned.endswith("```"):
                cleaned = cleaned.rstrip("`").strip()
            # Try to extract JSON from the cleaned response
            json_start = cleaned.find("{")
            json_end = cleaned.rfind("}") + 1
            json_str = cleaned[json_start:json_end]
            action_data = json.loads(json_str)
        except Exception as e:
            print(
                f"[Agent error parsing LLM response]: {e}\nRaw response: {llm_response}"
            )
            continue

        action = action_data.get("action")
        if action == "run_kubectl":
            command = action_data.get("command", "")
            if command:
                print(run_kubectl_command(command))
            else:
                print("[Agent error]: No kubectl command provided by LLM.")
        elif action == "call_github_tool":
            tool_name = action_data.get("tool_name", "")
            params = action_data.get("params", {})
            if tool_name:
                raw_result = call_github_mcp_tool(tool_name, params)
                print(f"[Raw tool result]: {raw_result}")
                # Send the raw result to the LLM for summarization
                summarize_prompt = (
                    "You are an assistant. The user asked: '" + user_input + "'.\n"
                    "The following tool was called: '"
                    + tool_name
                    + "' with parameters: "
                    + json.dumps(params)
                    + ".\n"
                    "Here is the raw result from the tool (as JSON or string):\n"
                    + str(raw_result)
                    + "\n"
                    "Please summarize or present the result in a clear, human-readable way."
                )
                print(f"[Summarizing tool result for LLM]: {summarize_prompt}")
                summary = ask_llm(summarize_prompt)
                print(summary)
            else:
                print("[Agent error]: No GitHub MCP tool name provided by LLM.")
        elif action == "ask_user_for_missing_params":
            missing = action_data.get("missing_params", [])
            if missing:
                print(
                    f"Please provide the following required parameters: {', '.join(missing)}"
                )
            else:
                print(
                    "[Agent error]: LLM says parameters are missing but did not specify which ones."
                )
        elif action == "answer_directly":
            answer = action_data.get("answer", "")
            print(answer or "[Agent error]: No answer provided by LLM.")
        else:
            print(
                f"[Agent error]: Unknown action '{action}'. Raw response: {llm_response}"
            )


if __name__ == "__main__":
    main()
