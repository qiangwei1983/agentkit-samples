import argparse
import json
import sys

from mcp_gateway_client import (
    DEFAULT_MCP_GATEWAY_URL,
    call_mcp_tool,
    load_credentials,
    pretty_print_mcp_result,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Call MCP tool describe_datasource via Volcano Engine MCP Gateway",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/describe_datasource.py --datasource-id all
  python3 scripts/describe_datasource.py --datasource-id enterprise_basic_wide
""",
    )

    parser.add_argument(
        "--datasource-id",
        default="all",
        help="Datasource id, or 'all' (default: all)",
    )
    parser.add_argument(
        "--locale",
        default="zh-CN",
        help="Locale for field descriptions (default: zh-CN)",
    )
    parser.add_argument(
        "--url",
        default=DEFAULT_MCP_GATEWAY_URL,
        help="MCP Gateway URL",
    )
    parser.add_argument(
        "--access-key",
        default=None,
        help="VOLCENGINE_ACCESS_KEY (optional, overrides env var)",
    )
    parser.add_argument(
        "--secret-key",
        default=None,
        help="VOLCENGINE_SECRET_KEY (optional, overrides env var)",
    )
    parser.add_argument(
        "--raw-response",
        action="store_true",
        help="Print full MCP JSON-RPC response",
    )

    args = parser.parse_args()

    try:
        ak, sk = load_credentials(args.access_key, args.secret_key)
        resp = call_mcp_tool(
            url=args.url,
            access_key=ak,
            secret_key=sk,
            tool_name="describe_datasource",
            arguments={"datasource_id": args.datasource_id, "locale": args.locale},
        )

        if args.raw_response:
            print(json.dumps(resp, ensure_ascii=False, indent=2))
        else:
            pretty_print_mcp_result(resp)

    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
