---
name: research-writing-workbench
description: Evidence workbench for software engineering, system integration, asynchronous and event-driven systems, open-source tools, and engineering-artifact-based case or design research. Use when Codex must turn an observed engineering problem into a bounded research question, define fair validation contracts, plan failure and concurrency scenarios, index code/tests/traces/logs/diffs, separate planned work from executed evidence, challenge interpretations with counterexamples, or draft claims that do not exceed the captured evidence. Never invent sources, executions, traces, metrics, results, approvals, author experience, or project effectiveness.
---

# Research Writing Workbench

協助研究者把軟體工程實作轉成可檢查、可反駁且範圍有限的研究論證。這是領域工作台，不是通用研究方法，也不是論文產生器。

## 確認適用範圍

只在下列研究脈絡使用：軟體工程與架構、系統整合、外部 API、事件驅動或非同步系統、開源工具、小型框架、程式測試、故障重現、軌跡重播，以及 AI 生成程式或判斷的證據檢查。

若任務主要屬於臨床、法律、純理論、一般社會調查或其他沒有工程產物與執行行為的研究，說明本 Skill 不能提供完整方法保證，只沿用不捏造與研究者核准邊界。

## 使用 CTCC 控制環

以「契約—軌跡—反例—主張」（Contract–Trace–Counterexample–Claim, CTCC）反覆檢查工程研究：

1. **契約**：先定義待比較或待驗證系統的共同輸入、可觀察輸出、完成條件、逾時、錯誤與環境邊界。
2. **軌跡**：保存能重建一次執行的程式版本、設定、測試、事件、時間、Log、Trace、Diff 與命令結果。
3. **反例**：主動安排會推翻預期解釋的失敗、亂序、重試、斷線、重複、並行覆寫與資源限制案例。
4. **主張**：依實際留下的證據決定保留、縮小、改寫或撤回陳述；不從實作存在直接跳到有效、優越或普遍成立。

CTCC 不是一次性流水線。新反例會迫使契約更新；缺失軌跡會使執行無法採信；主張改變也可能要求補做情境。

詳細定義見 [01-domain-and-ctcc.md](references/01-domain-and-ctcc.md)。

## 執行工程研究 Workflow

1. **定位工程異常**：用 [engineering-question-brief.md](assets/templates/engineering-question-brief.md) 記錄具體系統、事件、可觀察後果、分析單位與排除範圍。
2. **寫驗證契約**：用 [validation-contract.md](assets/templates/validation-contract.md) 定義共同功能、輸入、完成、錯誤、逾時、觀測及比較公平性。
3. **設計情境**：用 [scenario-matrix.md](assets/templates/scenario-matrix.md) 同時列正常、邊界、故障、重試、亂序與並行情境；標記哪些尚未執行。
4. **配置觀測**：在執行前決定需要哪些 Trace、Log、測試輸出、時間戳、識別碼、環境與版本資訊。
5. **執行或重播**：每次執行填 [execution-record.md](assets/templates/execution-record.md)；命令、exit code 與失敗也要保留，不得只抄成功畫面。
6. **組合證據包**：以 [trace-index.md](assets/templates/trace-index.md) 把每個觀察連回檔案、行號、事件、測試或變更。
7. **做反例審查**：用 [counterexample-review.md](assets/templates/counterexample-review.md) 判斷原解釋是否仍成立，以及還有哪些競爭解釋。
8. **裁定有限主張**：用 [bounded-claim-record.md](assets/templates/bounded-claim-record.md) 明列主張種類、支持、反證、範圍與研究者裁定。
9. **成文與交付**：只依已裁定內容起草；完成 AI 使用及隱私檢查，再交付未解問題與重現方式。

## 狀態與標記

- 工程產物成熟度：`planned`、`captured`、`reproduced`、`reviewed`、`invalidated`。
- 主張種類：`implementation`、`behavior`、`comparison`、`mechanism`、`transfer`。
- 研究者裁定：`keep`、`narrow`、`rework`、`withdraw`。
- 缺少實際檔案或輸出：`[未取得產物]`。
- 有產物但未重現：`[尚未重現]`。
- 執行結果互相衝突：`[執行衝突]`。
- 需要研究者選擇：`[待研究者裁定]`。

不得自行提升成熟度、移除標記或把 `planned` 改寫成已完成。

## 工程證據邊界

- 程式存在只支持「已建置到何種範圍」，不等於行為正確、效能改善或研究貢獻成立。
- 單一測試通過只支持該版本、環境、輸入與斷言涵蓋的行為。
- Log 是系統輸出，不自動證明事件原因；Trace 缺段時不得補畫中間事件。
- Commit 或 Diff 可證明版本間變更，不自動證明變更造成觀察結果。
- 架構比較必須共享可檢查契約；功能、負載、環境或觀測不同時，不得直接宣稱優劣。
- 非同步命令必須定義「接受」「產生可觀察效果」「終止或穩定」何者算完成。
- 尚未執行的設計、案例推演與合成資料，只能用未來式或條件式描述。

進一步規則按任務讀取：

- 契約與比較：[02-contract-and-comparison.md](references/02-contract-and-comparison.md)
- 執行與證據包：[03-trace-and-evidence.md](references/03-trace-and-evidence.md)
- 反例與可否證性：[04-counterexamples.md](references/04-counterexamples.md)
- 有限主張與成文：[05-bounded-writing.md](references/05-bounded-writing.md)
- AI、隱私與交付：[06-ai-audit-and-release.md](references/06-ai-audit-and-release.md)

只讀與本次任務相關的 reference。

## AI 可以與不可以做的事

AI 可以整理工程材料、提出契約缺口、產生待執行情境草案、比較實際 Trace、指出競爭解釋及協助有限改寫。AI 不可以冒稱跑過命令、看過不存在的 Log、補造來源或數值、代替研究者接受主張，或把測試成功擴張成系統可靠。

改寫時分成：

- **文字修整**：不改工程事實、數字、版本、證據連結與主張種類。
- **論證重排**：可調整材料順序，但先報告可能改變的因果、時間與比較關係。
- **研究變更提案**：獨立提出契約、情境、分析或主張變更，等待研究者裁定後才納入正文。

## 預設輸出

1. 本次處理的工程研究問題與範圍。
2. 契約缺口及待執行情境。
3. 已取得產物、重現狀態與證據位置。
4. 最強反例及競爭解釋。
5. 可保留的有限主張與不得宣稱內容。
6. 研究者待裁定事項及下一個可重現動作。
