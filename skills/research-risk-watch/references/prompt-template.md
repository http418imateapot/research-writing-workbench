# Prompt Template

## Input

- Source Catalog、Corpus Snapshot、Claims、Findings、Checklist 與上次檢查日期。

## Output

- 有時間界線的風險 Findings、差異、Checklist 與後續動作。

## Required

- 保存查詢日期、正式來源、受影響 ID 與未檢查範圍。
- 來源雜湊改變時重開既有項目並保留歷史。

## Forbidden

- 將「未搜尋到」解讀為「沒有風險」。
- 自動關閉、撤回或核准研究主張。

## Positive example

「比對 2026-08-03 snapshot，查核 DOI 狀態並重開雜湊已變更來源的 high item。」

## Negative example

「沒有看到撤稿新聞，所以所有來源都安全。」
