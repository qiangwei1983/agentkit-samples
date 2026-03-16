---
name: byted-data-search
description:
  Public data retrieval service. Use this skill when users need to query public datasets such as
  enterprise/company information and business registration data.
  Supports fuzzy search, exact match, and aggregation queries.
  Trigger: when users ask for information about one or more specific companies (e.g., company profile,
  enterprise details, recent status).
---

# Datasource Query Tools

Query structured datasources via the gateway. Supports retrieving enterprise/business information for one or multiple companies.

## Prerequisites

Required environment variables (scripts will read them automatically; if missing, you will be prompted to set them):
- `VOLCENGINE_ACCESS_KEY`
- `VOLCENGINE_SECRET_KEY`

## Workflow (Execute in Order)

### Step 1: List / Inspect Datasources

Run this first to learn which datasources are available and what fields they expose, then decide how to query.

```bash
# List all available datasources
python3 scripts/describe_datasource.py --datasource-id all

# View a specific datasource’s field definitions
python3 scripts/describe_datasource.py --datasource-id <DATASOURCE_ID>
```

The response includes:
- `datasource_name`, `description`, `notes`
- Field definitions in `dimensions` (field name / type / description / example)

Key: use the returned field info to decide what fields and filters you need, then proceed to Step 2.

### Step 2: Query Data

Build the query command based on the fields discovered in Step 1:

```bash
python3 scripts/query_datasource.py \
  --datasource-id <DATASOURCE_ID> \
  --filters '<FILTERS>' \
  --page 1 \
  --page-size 10
```

Full parameter reference:

| Parameter | Required | Description |
|------|------|------|
| `--datasource-id` | Yes | Datasource ID from Step 1 |
| `--filters` | No | Filters string. See format below |
| `--select-fields` | No | Comma-separated return fields |
| `--aggregation` | No | Aggregation, e.g. `count` or `field:count` |
| `--group-by` | No | Group-by fields, comma-separated |
| `--sort-field` | No | Sort field |
| `--sort-order` | No | `asc` or `desc` (default: desc) |
| `--page` | No | Page number, starting from 1 (default: 1) |
| `--page-size` | No | Page size, 1–50 (default: 10) |

## Filter String Format

Format: `field:operator:value`, multiple conditions separated by `;`.

| Operator | Meaning | Example |
|--------|------|------|
| `eq` | Exact match | `company_name:eq:ByteDance Ltd.` |
| `like` | Fuzzy match | `company_name:like:ByteDance` |
| `in` | Multi-value match | `risk_level:in:High,Medium` |
| `not_in` | Exclude | `risk_level:not_in:Low` |
| `between` | Range (dates) | `risk_date:between:2024-01-01,2025-12-31` |
| `range` | Numeric range | `risk_score:range:50,100` (half-open: `,100` or `50,`) |
| `keyword` | Full-text search | `keyword:keyword:new energy subsidy` |

Example with multiple conditions:
```
company_name:like:ByteDance;risk_level:in:High,Medium;risk_date:between:2024-01-01,2025-12-31
```

## Common Examples

```bash
# Fuzzy search by company name
python3 scripts/query_datasource.py \
  --datasource-id enterprise_basic_wide \
  --filters 'company_name:like:ByteDance'

# Count records
python3 scripts/query_datasource.py \
  --datasource-id enterprise_basic_wide \
  --filters 'company_name:like:ByteDance' \
  --aggregation 'count'

# Select fields + sorting
python3 scripts/query_datasource.py \
  --datasource-id enterprise_basic_wide \
  --filters 'company_name:like:ByteDance' \
  --select-fields 'company_name,registered_capital,establish_date' \
  --sort-field 'establish_date' \
  --sort-order 'desc'

# Group-by aggregation
python3 scripts/query_datasource.py \
  --datasource-id enterprise_basic_wide \
  --filters 'company_name:like:Technology' \
  --group-by 'province' \
  --aggregation 'count'
```

## Rate Limits

- **Rate limit**: up to 5 calls per minute
- **Daily quota**: up to 200 calls per day
- For higher quotas, purchase [Volcano Engine - High Quality Dataset](https://console.volcengine.com/high-quality-dataset)

## Error Handling

- **Auth failure**: verify `VOLCENGINE_ACCESS_KEY` / `VOLCENGINE_SECRET_KEY` are set.
How to obtain credentials:
1. Get Volcano Engine access credentials (AK/SK): see the [User Guide](https://www.volcengine.com/docs/6291/65568?lang=zh)

2. Set the following environment variables:

```bash
export VOLCENGINE_ACCESS_KEY="your-access-key"
export VOLCENGINE_SECRET_KEY="your-secret-key"
export VOLCENGINE_REGION="cn-beijing"  # optional, default is cn-beijing
```

- **Datasource not found**: run `describe_datasource.py --datasource-id all` to list available datasources.
- **Field not found**: run `describe_datasource.py --datasource-id <ID>` to inspect supported fields.
- **No results**: loosen filters (e.g., `eq` → `like`) or verify field values.
- **Timeout**: adjust `timeout_seconds` in the script (default: 30s).
