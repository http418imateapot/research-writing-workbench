# Repository instructions

## 專案目的

本專案提供適用於軟體工程、系統整合與事件驅動系統研究的 repository skill。它以工程產物與實際執行紀錄支持有限論證，不是通用研究方法，也不是論文產生器。

## 單一來源與目錄

- `.agents/skills/research-writing-workbench/`：唯一正式 Skill。
- Skill 內 `references/`：方法規則；`assets/templates/`：正式資料格式。
- `prompts/`：一般聊天模型介面，不複製完整 reference 正文。
- `docs/`：架構、方法來源、治理與維護。
- `examples/`：只放合成、未執行的工程研究範例。
- `scripts/`、`tests/`：驗證、隱私掃描與封裝。

不得建立第二份正式 `SKILL.md`，不得把 README 或本檔擴張成方法百科。

## 正式方法契約

- 核心控制環限「契約—軌跡—反例—主張」（CTCC）。
- 工程產物成熟度限 `planned`、`captured`、`reproduced`、`reviewed`、`invalidated`。
- 主張種類限 `implementation`、`behavior`、`comparison`、`mechanism`、`transfer`。
- 研究者裁定限 `keep`、`narrow`、`rework`、`withdraw`。
- 未解標記限 `[未取得產物]`、`[尚未重現]`、`[執行衝突]`、`[待研究者裁定]`。

不得重新引入前身購書附件的流程名稱、層級、狀態列舉、模板對應或可辨識措辭。需要說明歷史時，只能概述來源與授權邊界，不收錄附件正文或檔案。

## 內容規則

- 正體中文採台灣研究與技術用語；Markdown 使用 ATX heading、UTF-8、LF 及相對連結。
- 不得加入真實秘密、Token、私有程式碼、個資、客戶資料、可識別 Log 或未獲授權內容。
- 不得捏造來源、執行、Trace、Log、測試結果、數值、作者經驗或本專案效益。
- 程式存在不等於行為正確；測試通過不等於一般可靠；Diff 不等於因果；可建置不等於有效。
- 使用者可見變更須同步檢查 Skill、Prompt、相關 reference、模板、範例、測試、README 與 CHANGELOG。

## 必跑命令

```shell
python -m unittest discover -s tests -v
python scripts/validate_repository.py
python scripts/privacy_scan.py
python scripts/check_all.py
python scripts/package_skill.py --output-dir .work/package-smoke
git diff --check
```

## Git 與發布

版本採 Semantic Versioning；`VERSION`、`CITATION.cff`、`CHANGELOG.md` 與發布 ZIP 檔名須一致。正式 ZIP 只含唯一 Skill 目錄，不得含前身附件、測試 fixture、`.work`、cache 或秘密資訊。

Commit 前確認 Git 身分、remote、分支、狀態與測試。只有使用者明確要求時才可 commit、push、force push 或發布。

## Code Review Rules

1. 拒絕第二份正式來源、前身附件內容回流與大段正文複製。
2. 不得弱化 CTCC、實際執行證據或研究者裁定權。
3. 比較缺少共同契約、Trace 無法重建或反例未處理時，不能提升主張。
4. 檢查 `planned` 是否被誤寫成完成，工程成果是否被誇大為研究效益。
5. 檢查秘密、個資、私有程式碼、可識別 Log 與第三方授權。
6. 使用者可見變更必須更新 CHANGELOG；新模板、腳本與公開介面必須有文件及測試。
