---
name: research-risk-watch
description: Check and track source conflicts, corrections, retractions, version drift, missing evidence, unresolved checklist items, privacy, licensing, and overclaim risks in an existing research corpus. Use when users ask to refresh source status, monitor research risks, inspect retractions or errata, audit unresolved gaps, compare corpus snapshots, or prepare a risk register; trigger on 研究風險、撤稿檢查、來源衝突、更新追蹤、risk watch, retraction, errata, or gap audit. Time-bound all external checks and never infer safety from missing results.
---

# Research Risk Watch

將風險檢查綁定日期、來源與版本；「未查到」不等於「不存在」。

## 執行流程

1. 讀取現有 Source Catalog、Corpus Snapshot、Evidence、Findings、Checklist 與上次檢查日期。
2. 針對 DOI／URL、勘誤、撤稿、版本、授權與出版狀態查詢正式來源；保存查詢時間與結果位置。
3. 比對來源 SHA-256、識別碼、書目 metadata 與納入狀態；保留衝突，不自動覆蓋。
4. 檢查無來源 Claim、未驗證引用、失效 locator、過強主張、隱私與授權風險。
5. 將結果寫成 Finding；需要人工處理時建立或重開 stable Checklist item 並保留歷史。
6. 回報已檢查範圍、未能檢查的來源、風險嚴重度、影響 Claim 與下一次可執行動作。

## 邊界

不要把搜尋缺席當成安全證明，不要自動撤回或核准 Claim，不要以非正式摘要取代出版者或登錄機構狀態。

先讀取 [prompt-template.md](references/prompt-template.md)。
