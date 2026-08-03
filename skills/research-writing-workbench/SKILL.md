---
name: research-writing-workbench
description: Route and govern software-engineering, system-integration, asynchronous, event-driven, open-source-tool, and engineering-artifact-based thesis research through the Contract–Trace–Counterexample–Claim (CTCC) loop. Use when a request spans research planning, evidence capture, failure or concurrency scenarios, trace reconstruction, counterexample review, bounded claims, writing, or release decisions, or when the user asks which research Skill to use. Preserve planned versus executed evidence and researcher authority; never invent sources, executions, traces, metrics, results, approvals, author experience, or effectiveness.
---

# Research Writing Workbench

以「契約—軌跡—反例—主張」（Contract–Trace–Counterexample–Claim, CTCC）管理軟體工程研究。這是領域工作台與路由入口，不是通用論文產生器。

## 路由任務

- 研究問題、契約、情境與里程碑：使用 `$research-planning`。
- 文獻搜尋、書目查證與語料快照：使用 `$literature-discovery`。
- 論文、程式、測試、Trace、Log 或資料證據抽取：使用 `$evidence-extract`。
- Claim–Evidence 比較、衝突與有限主張：使用 `$research-synthesis`。
- 方法、效度、比較公平性與可重現性：使用 `$methodology-review`。
- 章節大綱、草稿、改寫與論證稽核：使用 `$research-writing`。
- 治理閘門、正式產物與 sidecar：使用 `$research-export`。
- 勘誤、撤稿、版本、衝突、隱私與授權風險：使用 `$research-risk-watch`。

任務同時跨越多個階段時，保持同一組 source、evidence、claim、finding 與 checklist ID，依上述順序交接；不要複製或改寫已確認事實。

## 執行 CTCC 控制環

1. **契約**：定義共同輸入、可觀察輸出、完成條件、逾時、錯誤、重試、順序、併發、環境與比較公平性。
2. **軌跡**：保存能重建執行的版本、設定、命令、exit code、測試、事件、時間、Log、Trace、Diff 與產物位置。
3. **反例**：安排會削弱預期解釋的失敗、亂序、重複、斷線、重試、並行覆寫、部分成功與觀測缺口。
4. **主張**：依實際證據由研究者裁定保留、縮小、重做或撤回；不要從實作存在跳到有效、優越或普遍成立。

CTCC 是回饋控制環。反例暴露缺口時回到契約；軌跡不能重建時降低成熟度；主張需要未涵蓋行為時補做情境。

依任務讀取 [領域與 CTCC](references/01-domain-and-ctcc.md)、[契約與比較](references/02-contract-and-comparison.md)、[軌跡與證據](references/03-trace-and-evidence.md)、[反例](references/04-counterexamples.md)、[有限主張](references/05-bounded-writing.md)、[AI 與交付](references/06-ai-audit-and-release.md) 或 [prompt-template.md](references/prompt-template.md)。

需要研究產物時直接使用 [Engineering Question Brief](assets/templates/engineering-question-brief.md)、[Validation Contract](assets/templates/validation-contract.md)、[Scenario Matrix](assets/templates/scenario-matrix.md)、[Execution Record](assets/templates/execution-record.md)、[Trace Index](assets/templates/trace-index.md)、[Counterexample Review](assets/templates/counterexample-review.md)、[Bounded Claim Record](assets/templates/bounded-claim-record.md)、[AI Use Record](assets/templates/ai-use-record.md) 與 [Release Check](assets/templates/release-check.md)。

## 保持正式契約

- 工程產物成熟度限 `planned`、`captured`、`reproduced`、`reviewed`、`invalidated`。
- 主張種類限 `implementation`、`behavior`、`comparison`、`mechanism`、`transfer`。
- 研究者裁定限 `keep`、`narrow`、`rework`、`withdraw`。
- 未解標記限 `[未取得產物]`、`[尚未重現]`、`[執行衝突]`、`[待研究者裁定]`。

不要自行提升成熟度、移除未解標記或把 `planned` 改寫成完成。程式存在只支持實作範圍；測試只支持該版本、環境、輸入與斷言；Log 不自動證明原因；Diff 不自動證明因果；比較必須共享契約。

## 預設輸出

1. 工程研究問題與範圍。
2. 契約缺口與待執行情境。
3. 已取得產物、重現狀態與證據位置。
4. 最強反例與競爭解釋。
5. 可保留的有限主張與不得宣稱內容。
6. 研究者待裁定事項與下一個可重現動作。
