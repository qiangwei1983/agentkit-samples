import json
import os
from typing import Any, Dict, Optional, Tuple

import requests

DEFAULT_MCP_GATEWAY_URL = (
    "https://sd6k08f59gqcea6qe13vg.apigateway-cn-beijing.volceapi.com/mcp"
)


def load_credentials(
    access_key: Optional[str] = None, secret_key: Optional[str] = None
) -> Tuple[str, str]:
    ak = access_key or os.getenv("VOLCENGINE_ACCESS_KEY") or ""
    sk = secret_key or os.getenv("VOLCENGINE_SECRET_KEY") or ""

    if not ak or not sk:
        raise ValueError(
            "Missing credentials. Set VOLCENGINE_ACCESS_KEY and VOLCENGINE_SECRET_KEY."
        )

    return ak, sk


def call_mcp_tool(
    *,
    url: str,
    access_key: str,
    secret_key: str,
    tool_name: str,
    arguments: Dict[str, Any],
    request_id: int = 1,
    timeout_seconds: int = 30,
) -> Dict[str, Any]:
    payload = {
        "jsonrpc": "2.0",
        "id": request_id,
        "method": "tools/call",
        "params": {"name": tool_name, "arguments": arguments},
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Volc-Access-Key": access_key,
        "Volc-Secret-Key": secret_key,
    }

    response = requests.post(
        url,
        headers=headers,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    return response.json()


def extract_tool_text(mcp_response: Dict[str, Any]) -> Optional[str]:
    if "error" in mcp_response and mcp_response["error"]:
        return None

    result = mcp_response.get("result")
    if isinstance(result, dict):
        content = result.get("content")
        if isinstance(content, list):
            texts = []
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text" and isinstance(
                    item.get("text"), str
                ):
                    texts.append(item["text"])
            if texts:
                return "\n".join(texts)

    if isinstance(result, str):
        return result

    return None


def pretty_print_mcp_result(mcp_response: Dict[str, Any]) -> None:
    if "error" in mcp_response and mcp_response["error"]:
        print(json.dumps(mcp_response, ensure_ascii=False, indent=2))
        return

    tool_text = extract_tool_text(mcp_response)
    if tool_text is None:
        print(json.dumps(mcp_response, ensure_ascii=False, indent=2))
        return

    try:
        parsed = json.loads(tool_text)
        print(json.dumps(parsed, ensure_ascii=False, indent=2))
    except Exception:
        print(tool_text)
