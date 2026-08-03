---
name: literature-discovery
description: Design reproducible literature searches and build a verified source catalog for software-engineering research. Use when users ask to search papers, survey prior work, find related work, verify DOI or bibliographic metadata, define inclusion and exclusion criteria, deduplicate sources, or capture a corpus snapshot; trigger on 文獻搜尋、文獻回顧、相關研究、找論文、literature review, prior work, or systematic search. Never invent citations or treat unverified metadata as confirmed.
---

# Literature Discovery

建立可重跑的檢索策略、來源目錄與語料快照；不要把搜尋結果頁或模型記憶當成已驗證來源。

## 執行流程

1. 將研究問題拆成核心概念、同義詞、排除詞、時間範圍、資料庫與來源種類。
2. 在可用檢索工具中執行或記錄精確查詢式；保存資料庫、日期、排序、篩選與結果數。無法執行時只交付待執行策略。
3. 為候選來源建立穩定 `source_id`，保存題名、作者、年份、版本、出版資訊、DOI／URL、本機位置與取得日期。
4. 以出版者、DOI 註冊機構或正式索引查證識別碼；未查證資訊標為 unverified。
5. 使用內容雜湊與書目識別碼去重；版本衝突要並列，不得靜默覆蓋。
6. 記錄納入／排除理由、勘誤、撤稿、授權與可取得範圍，形成特定日期的 corpus snapshot。
7. 回報檢索盲點、資料庫偏差、缺少全文與後續補查項目。

## 邊界

不要複製未獲授權全文，不要猜 DOI、頁碼或作者，不要把「找得到」寫成「支持主張」。

先讀取 [prompt-template.md](references/prompt-template.md)。
