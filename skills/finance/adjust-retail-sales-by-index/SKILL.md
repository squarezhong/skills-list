---
name: adjust-retail-sales-by-index
description: Build index-adjusted Chinese social retail sales datasets and workbooks by mapping consumer index constituents to National Bureau of Statistics retail categories. Use when Codex needs to compare NBS year-to-date retail sales such as 1-5月 or 1-6月 across years, fetch or parse 国家统计局社会消费品零售总额 data, classify constituents from indices such as 恒生消费指数 or 上证消费50, drop categories without index companies, compute adjusted totals and YoY growth, or generate Excel outputs with category trend charts.
---

# Adjust Retail Sales By Index

## Workflow

1. **Lock the period.** Determine the target month range from the user request (`1-5月`, `1-6月`, latest release, etc.). If the user asks for latest or a recently released month, browse official NBS sources first; do not rely on memory.
2. **Collect official retail data.** Prefer local `.xls/.xlsx` files when provided. Otherwise search `stats.gov.cn` for each year/month release and capture the official URL. Use only the `1-N月` absolute amount and YoY columns from the main data table.
3. **Extract the index constituents.** Read the user-provided PDF/CSV/XLSX or official index page. If the index is not the previous 恒生消费指数 case, rebuild the constituent-to-category map from the new constituents.
4. **Classify constituents to NBS categories.** Use the rules in `references/category-mapping.md`. Classify by primary consumer-facing mainland China business when possible. Put restaurants/tea chains in `限额以上单位餐饮收入` only if the user allows餐饮口径. Exclude services with no matching NBS retail/餐饮 category unless the user defines an extra category.
5. **Select categories.** Keep only NBS categories with at least one included index constituent. Drop original categories with no index companies. Preserve user-specific exclusions such as companies with mostly non-mainland business.
6. **Compute adjusted totals.** Default formula: for each year, `adjusted_amount = sum(included category amounts)`, `prior_base = sum(amount / (1 + official_yoy))`, `adjusted_yoy = adjusted_amount / prior_base - 1`. Use direct year-over-year division only if the user asks for that sensitivity.
7. **Create the workbook.** Include:
   - `成分股分类`: code/name/weight/category/include/note.
   - `原始限额以上数据`: source year, category, amount, YoY, back-solved prior base, official source.
   - `修正后汇总`: categories as rows; columns as `<YY>年1-N月` and `同比增长`, matching the original NBS table orientation.
   - `折线图`: each kept category plus adjusted total over time; x-axis year, y-axis retail amount, each point labeled with YoY.
8. **Validate before delivery.** Check source coverage, constituent count/weight sum when weights exist, all kept categories have data or are explicitly marked missing, dropped categories are absent from the adjusted total, and chart images are nonblank.

## Script

Use `scripts/adjust_retail_sales.py` for repeatable parsing/calculation/output once sources and a constituent mapping are ready.

Typical command:

```bash
python3 scripts/adjust_retail_sales.py \
  --sources-json sources.json \
  --mapping constituents_mapping.csv \
  --month 6 \
  --start-year 2019 \
  --end-year 2026 \
  --index-name "上证消费50" \
  --output outputs/adjusted_retail_2019_2026_1-6m.xlsx
```

Inputs:
- `sources.json`: JSON object mapping year to a local `.xls/.xlsx/.html/.htm` path or official NBS URL.
- `constituents_mapping.csv`: one row per constituent with `code`, `name`, optional `weight`, `category`, `include`, and optional `note`.
- `category` must be one of the NBS categories in `references/category-mapping.md`, `限额以上单位餐饮收入`, or blank/`不纳入` for excluded firms.

The script can parse NBS HTML tables and Excel releases, normalize common label variants, compute the adjusted total, and generate the workbook/charts. Patch it locally if an official page has a new layout; keep the calculation formula unchanged unless the user changes methodology.

## Data Handling Rules

- Treat NBS categories as official publication categories, not industry taxonomy. If an older year does not publish a category, leave that cell blank and exclude it from that year’s adjusted total unless the user explicitly requests a backfill.
- Cite official URLs or local filenames inside the workbook. For latest data, include concrete dates/month ranges in the final answer.
- Do not force-map travel, hotels, education, online platforms, or other services into goods categories. Add a service category only when the user requests and the NBS table has a matching official line.
- For cross-category companies, choose the dominant consumer-facing category and add a note; if material ambiguity remains, ask the user before finalizing.
- Keep workbook values numeric, with percentages stored as percentages. Build charts from the same data used in the summary table.
