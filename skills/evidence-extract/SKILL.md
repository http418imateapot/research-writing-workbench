---
name: evidence-extract
description: Extract bounded, traceable research evidence from papers, code, tests, traces, logs, datasets, and supplied documents. Use when users ask to read sources, capture quotations or observations, map evidence to claims, verify locators and hashes, distinguish explicit statements from derived values or inference, or create Claim–Evidence records; trigger on 證據抽取、來源摘錄、逐篇閱讀、claim evidence, data extraction, or coding sheet. Do not fill missing values or infer unsupported findings.
---

# Evidence Extract

只從實際提供或已取得的來源抽取可定位證據，並把來源事實、計算、解讀與建議分欄。

## 執行流程

1. 確認每個輸入已有 `source_id`、版本、SHA-256、存取狀態與允許用途。
2. 依研究問題定位頁、章節、段落、表、圖、程式行、測試、Trace 事件或資料欄位。
3. 保存最小必要摘錄、locator、摘錄雜湊與遮蔽狀態；不要複製無關全文。
4. 將條目分類為 `explicit`、`derived`、`inference`、`assumption` 或 `recommendation`。
5. 對 `derived` 條目記錄方法、版本、輸入與可重現計算；數值缺漏不得當成 0。
6. 保留互相衝突的來源與差異，不自動裁決。
7. 把 AI 解讀寫入 Finding 或待審欄位，不要直接改寫來源事實。

## 輸出契約

輸出來源索引、Evidence Record、未解欄位、衝突與待研究者審查事項。沒有可定位來源時拒絕建立正式 Evidence。

先讀取 [prompt-template.md](references/prompt-template.md)。
