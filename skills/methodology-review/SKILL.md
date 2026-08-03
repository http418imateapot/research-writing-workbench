---
name: methodology-review
description: Review research methods, validity threats, reproducibility, comparison fairness, data contracts, and evidence sufficiency for software-engineering and artifact-based studies. Use when users ask for methodology audit, protocol review, peer-review preparation, validity assessment, reproducibility checklist, statistical reporting checks, or design critique; trigger on 方法審查、研究設計檢查、效度威脅、可重現性、methodology review, validity, or reproducibility. Report findings without silently rewriting the study.
---

# Methodology Review

以 Finding 與 Checklist 審查設計，不把審查建議偽裝成已修正或已核准。

## 執行流程

1. 確認研究問題、分析單位、契約、資料來源、版本、執行與預定主張能相互連結。
2. 檢查建構效度、內部效度、外部效度、結論效度、測量誤差與觀測盲點。
3. 檢查選樣、排除、缺值、重複、資料洩漏、比較公平性、並行、逾時與重試。
4. 檢查命令、環境、依賴、隨機性、原始輸出、Trace、Log 與版本是否足以重建。
5. 區分確定性規則結果與 AI 輔助判讀；記錄 method ID、版本、輸入、輸出與限制。
6. 為需要人工處理的 Finding 建立嚴重度與 stable fingerprint；不得自動關閉。
7. 依影響提出 keep、narrow、rework 或 withdraw 建議，保留研究者裁定權。

## 輸出契約

輸出方法摘要、通過項目、Findings、效度威脅、可重現缺口、Checklist 與不得宣稱內容。

先讀取 [prompt-template.md](references/prompt-template.md)。
