# 論文研究與寫作指令

下列指令可直接貼到支援 Agent Skills 的介面。請把方括號內容換成實際路徑、ID 與限制；若材料不存在，保留未解標記，不要要求模型補造。

## 規劃研究

```text
使用 $research-planning，根據[問題背景]提出最多三個有界研究問題。每題列出分析單位、排除範圍、可反駁觀察、Validation Contract、Scenario Matrix、證據取得計畫、里程碑與停止條件。所有未執行情境保持 planned。
```

## 盤點文獻

```text
使用 $literature-discovery，為[研究問題]設計可重跑檢索。保存資料庫、完整查詢式、日期、納入／排除理由、版本與驗證狀態；建立 Source Catalog 與 Corpus Snapshot。未查證 DOI 或 URL 標為 unverified。
```

## 抽取證據

```text
使用 $evidence-extract，從[來源 ID 與檔案]抽取回答[研究問題]所需的最小證據。每筆保存 source ID、SHA-256、locator、摘錄雜湊，並分類為 explicit、derived、inference、assumption 或 recommendation。
```

## 綜整主張

```text
使用 $research-synthesis，比較[Evidence IDs]並建立 Claim–Evidence 矩陣。保留衝突、反證與競爭解釋；依 implementation、behavior、comparison、mechanism、transfer 分類，最後提出 keep、narrow、rework 或 withdraw 建議，等待研究者裁定。
```

## 審查方法

```text
使用 $methodology-review，審查[研究計畫或產物路徑]的建構、內部、外部與結論效度，並檢查比較公平性、並行／逾時／重試、資料洩漏、版本與重現資訊。輸出 Findings 與 Checklist，不直接改寫核心資料。
```

## 寫論文章節

```text
使用 $research-writing，依[reviewed Claim IDs]、[Evidence IDs]與[Source IDs]起草[章節]。每段先綁定來源與 locator，再寫解讀、反例、限制及不得外推範圍。缺少資料時保留 [未取得產物] 或 [待研究者裁定]。
```

## 稽核正式匯出

```text
使用 $research-export，先驗證[研究資料目錄]並 dry-run。只有 active、reviewed／confirmed、source-grounded 的 Claim 可納入；high Checklist 未解時以 exit code 8 阻擋，並產生包含輸入雜湊、納入／排除 ID、限制與產物 SHA-256 的 sidecar。
```

## 追蹤研究風險

```text
使用 $research-risk-watch，比對[前次 snapshot]與[目前來源目錄]，查核勘誤、撤稿、版本、來源雜湊、授權與未解 Checklist。保存查核日期與正式來源；未查到結果不得寫成沒有風險。
```

## 跨階段路由

```text
使用 $research-writing-workbench，先盤點本次材料與 CTCC 狀態，再依序路由到需要的研究 Skill。跨階段保持同一組 source、evidence、claim、finding 與 checklist ID，不把 planned 寫成已完成。
```
