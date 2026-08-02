# Maintenance

先閱讀根目錄 [AGENTS.md](../AGENTS.md)。方法與模板只在 `.agents/skills/research-writing-workbench/` 變更；同步檢查 Prompt、README、docs、examples、tests 與 CHANGELOG。

每次變更執行 `python scripts/check_all.py`。發布前另執行 `python scripts/package_skill.py --output-dir .work/package-smoke`，解壓後人工確認只有正式 Skill，沒有前身附件、私有工程材料、tests、`.work`、cache 或秘密資訊。

新增隱私 allowlist 項目時，必須說明它為何是公開且安全的文字；不得用 allowlist 隱藏真正問題。
