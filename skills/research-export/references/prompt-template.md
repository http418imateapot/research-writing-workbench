# Prompt Template

## Input

- 已驗證的 Source Catalog、Evidence、Checklist 與輸出路徑。

## Output

- 研究交付物、sidecar report、SHA-256 與 exit code。

## Required

- 先驗證治理閘門並列出納入／排除 ID。
- 保持輸出可重現、預設拒絕覆寫。

## Forbidden

- 用 `--force` 關閉 Checklist 或納入不合格資料。
- 把本機候選宣稱為公開 Release。

## Positive example

「先 dry-run；若無 high Checklist，再匯出 reviewed claims 與 audit sidecar。」

## Negative example

「忽略所有錯誤，強制把未審 Claim 都放進正式報告。」
