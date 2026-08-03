# Repository instructions

## 專案目的

本專案提供適用於軟體工程、系統整合、事件驅動系統與工程產物型論文研究的 Agent Skill 工具包。它以來源、工程產物、執行紀錄與研究者裁定支持有限論證，不是通用論文產生器。

## 單一來源與目錄

- `skills/`：九個正式 Skill 的唯一原始碼；不得在 `.agents/`、README 或其他目錄建立第二份正式 `SKILL.md`。
- `shared/`：Schema、共用 Prompt、治理規則與 Checklist 的唯一來源。
- `scripts/`：公開 CLI 與共享 private module；維持既有 CLI flags 與 exit code 相容。
- `dist/`：由 `build.py` 產生、忽略且未追蹤；不得手動編輯。
- `prompts/`：一般聊天介面與可複製指令，不複製完整 Skill reference。
- `fixtures/`、`examples/`：只放合成、未執行資料。
- `docs/`、`toolkit/`：架構、資料契約、安裝、使用、遷移與治理。

建置時只依 `SCRIPT_MAP`、`SCHEMA_MAP`、`REFERENCE_GROUPS`、`ASSET_MAP` 與 `DISTRIBUTION_FILE_MAP` 白名單把共享相依複製進自足 Skill 包。

## 正式方法與治理契約

- 核心控制環限「契約—軌跡—反例—主張」（CTCC）。
- 工程產物成熟度限 `planned`、`captured`、`reproduced`、`reviewed`、`invalidated`。
- 主張種類限 `implementation`、`behavior`、`comparison`、`mechanism`、`transfer`。
- 研究者裁定限 `keep`、`narrow`、`rework`、`withdraw`。
- 未解標記限 `[未取得產物]`、`[尚未重現]`、`[執行衝突]`、`[待研究者裁定]`。
- 來源、Evidence、Finding、Checklist、Decision Log 與正式輸出必須分層。
- 無來源的正式 Claim 必須拒絕；high Checklist 未解時以 exit code 8 阻擋正常匯出。
- `--force` 只能產生警告產物，不得變更審查狀態或納入不合格 Claim。

不得重新引入前身購書附件的流程名稱、欄位、狀態列舉、模板或可辨識措辭。只可概述來源與授權邊界。

## 內容與開發規則

- 使用正體中文與台灣研究、技術用語；Markdown 使用 ATX heading、UTF-8、LF 及相對連結。
- Skill 名稱、frontmatter、reference、`agents/openai.yaml` 與 prompt-template 須符合目前官方格式。
- 不得加入真實秘密、Token、私有程式碼、個資、可識別 Log、未授權全文或真實敏感研究資料。
- 不得捏造來源、執行、Trace、測試、數值、結果、作者經驗、核准或本專案效益。
- 使用者可見變更須同步檢查 Skill、Prompt、reference、模板、Schema、CLI、fixture、測試、README、docs 與 CHANGELOG。
- 所有專案 Python 命令只透過 repository `.venv`；執行期 script 不得自動安裝套件。

## 必跑命令

```powershell
.\.venv\Scripts\python.exe -m compileall -q build.py scripts tests
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
.\.venv\Scripts\python.exe scripts\validate_repository.py
.\.venv\Scripts\python.exe scripts\privacy_scan.py
.\.venv\Scripts\python.exe scripts\check_all.py
.\.venv\Scripts\python.exe build.py --check
.\.venv\Scripts\python.exe build.py
.\.venv\Scripts\python.exe scripts\package_skill.py --output-dir .work\package-smoke
git ls-files dist
git diff --check
```

完整建置後再建置一次，比對所有 ZIP SHA-256。

## Git 與發行

版本採 Semantic Versioning；`VERSION`、`CITATION.cff`、`CHANGELOG.md` 與 ZIP 檔名須一致。正式包不得含前身附件、tests、fixtures、`.work`、cache、私人來源、秘密或非白名單資料。

Commit 前確認 Git 身分、remote、分支、狀態與測試。只有使用者明確要求時才可 commit、push、建立 PR、tag、Release 或公開發布。不得使用 `reset --hard`、`clean`、rebase、amend 或強制推送。

## Code Review Rules

1. 拒絕第二份正式來源、前身附件回流與大段正文複製。
2. 不得弱化 CTCC、來源追溯、實際執行證據、Checklist 閘門或研究者裁定權。
3. 比較缺少共同契約、Trace 無法重建、來源未驗證或反例未處理時，不能提升主張。
4. 檢查 `planned` 是否被誤寫成完成，Finding 是否直接修改核心資料，工程成果是否被誇大為研究效益。
5. 檢查秘密、個資、私有程式碼、可識別 Log、第三方授權與包內容白名單。
6. intentional contract change 必須有相容性分析、migration 與回歸測試。
