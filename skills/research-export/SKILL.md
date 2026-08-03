---
name: research-export
description: Validate and export reviewed, active, source-grounded research records into auditable Markdown or structured deliverables with checksums and sidecar reports. Use when users ask to generate a release candidate, final report, governed dataset, citation-ready output, package, or export audit; trigger on 正式匯出、研究交付、報告產出、release candidate, export, package, or sidecar report. Enforce unresolved high-review gates and never use force to approve or include ineligible claims.
---

# Research Export

只從符合治理閘門的資料產生本機交付候選，並保留可重算的輸入與產物雜湊。

## 執行流程

1. 先執行封裝內 `scripts/research_validate.py`，確認 Schema、跨檔引用、來源與狀態。
2. 檢查所有正式 Claim 為 active、reviewed／confirmed、source-grounded，且 derived Evidence 可重現。
3. 檢查 high Checklist；未解項目以 exit code 8 阻擋正常匯出。
4. 使用 `scripts/research_export.py` 產生交付物與 `.report.json` sidecar；先用 `--dry-run` 檢查。
5. 只有使用者明確要求時使用 `--force`；它只能產生醒目警告產物，不得關閉 Checklist 或納入不合格 Claim。
6. 回報輸入版本與雜湊、納入／排除 ID、警告、限制、產物 SHA-256 與實際 exit code。

## 邊界

本機建置完成不等於公開發布、同儕審查、授權通過或研究有效。未經授權不要上傳檔案或建立 Release。

先讀取 [prompt-template.md](references/prompt-template.md)。
