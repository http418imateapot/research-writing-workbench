# 使用指南

## 建議流程

1. 用 `$research-planning` 固定研究問題、分析單位、排除範圍、契約、情境與停止條件。
2. 用 `$literature-discovery` 保存檢索式、查詢日期、納入／排除理由與 Source Catalog。
3. 用 `$evidence-extract` 建立具 source ID、SHA-256 與 locator 的 Evidence。
4. 用 `$research-synthesis` 建立 Claim–Evidence 矩陣、衝突與有限主張。
5. 用 `$methodology-review` 建立 Findings 與需要人工處理的 Checklist。
6. 由研究者使用 resolution CLI 逐筆裁定，不讓 AI 自動關閉項目。
7. 用 `$research-writing` 依 reviewed Claim 起草，保留來源、限制與反例。
8. 用 `$research-export` 執行正式輸出閘門與 sidecar。
9. 用 `$research-risk-watch` 依日期重新查核來源狀態與未解風險。

跨多階段任務可從 `$research-writing-workbench` 開始路由。各階段保持同一組 source、evidence、claim、finding 與 checklist ID。

## CLI

```powershell
.\.venv\Scripts\python.exe scripts\research_validate.py --project-dir fixtures\synthetic-study
.\.venv\Scripts\python.exe scripts\research_checklist.py --findings fixtures\synthetic-study\findings.json --source-catalog fixtures\synthetic-study\source-catalog.json --checklist .work\checklist.json --dry-run
.\.venv\Scripts\python.exe scripts\research_export.py --project-dir fixtures\synthetic-study --output .work\claims.md --dry-run
```

寫檔預設拒絕覆寫。需要更新既有 Checklist、Decision Log 或輸出時先 dry-run，再明確使用 `--force`。`--force` 不會核准資料、關閉未解項目或納入不合格 Claim。

## Checklist 閉環

`research_checklist.py` 依 Finding identity、方法版本與受影響 ID 建立 stable fingerprint。重跑相同輸入保持冪等；來源雜湊變更時重開已關閉項目並保留 history。`research_resolve.py` 只處理決策檔明列的 fingerprint，並以原子多檔更新同時寫回 Checklist 與追加式 Decision Log。

## 寫作邊界

只有 active 且 reviewed／confirmed、具來源的 Claim 才能進入正式輸出。`planned`、draft、未驗證引用、缺少 locator、AI Finding 或 `[待研究者裁定]` 內容只能以提案、限制或未解項目呈現。不得補造論文、作者、DOI、頁碼、樣本數、實驗、統計結果、作者經驗或研究效益。
