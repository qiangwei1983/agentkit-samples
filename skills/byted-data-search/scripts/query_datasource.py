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
        description="Call MCP tool query_datasource via Volcano Engine MCP Gateway",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 scripts/query_datasource.py \
    --datasource-id enterprise_basic_wide \
    --filters 'company_name:like:字节跳动' \
    --page 1 --page-size 10

  # Aggregation
  python3 scripts/query_datasource.py \
    --datasource-id enterprise_basic_wide \
    --filters 'company_name:like:字节跳动' \
    --aggregation 'count'
""",
    )

    parser.add_argument("--datasource-id", required=True, help="Datasource id")
    parser.add_argument(
        "--select-fields",
        default=None,
        help="Comma-separated fields to return (optional)",
    )
    parser.add_argument("--filters", default=None, help="Filters string (optional)")
    parser.add_argument(
        "--aggregation",
        default=None,
        help="Aggregation string, e.g. 'count' or 'company_id:count' (optional)",
    )
    parser.add_argument(
        "--group-by",
        default=None,
        help="Group by fields, comma-separated (optional)",
    )
    parser.add_argument("--sort-field", default=None, help="Sort field (optional)")
    parser.add_argument(
        "--sort-order",
        default="desc",
        choices=["asc", "desc"],
        help="Sort order (default: desc)",
    )
    parser.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    parser.add_argument(
        "--page-size",
        type=int,
        default=10,
        help="Page size (default: 10, max: 50)",
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

    if args.page < 1:
        raise SystemExit("--page must be >= 1")
    if args.page_size < 1 or args.page_size > 50:
        raise SystemExit("--page-size must be within [1, 50]")

    try:
        ak, sk = load_credentials(args.access_key, args.secret_key)
        arguments = {
            "datasource_id": args.datasource_id,
            "select_fields": args.select_fields,
            "filters": args.filters,
            "aggregation": args.aggregation,
            "group_by": args.group_by,
            "sort_field": args.sort_field,
            "sort_order": args.sort_order,
            "page": args.page,
            "page_size": args.page_size,
        }
        arguments = {k: v for k, v in arguments.items() if v is not None}

        resp = call_mcp_tool(
            url=args.url,
            access_key=ak,
            secret_key=sk,
            tool_name="query_datasource",
            arguments=arguments,
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
