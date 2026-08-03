# Contributing

歡迎修正文句、CTCC 方法、工程研究產物、驗證工具與文件。提交前先讀[內容政策](docs/governance/content-policy.md)與[方法來源](docs/method-origin.md)。

## 內容要求

- 新判準要說明適用系統、驗證契約、需要的實際產物、反例及不得外推之處。
- 不接受虛構來源、命令、Trace、Log、測試結果、效益、私人案例或可識別資料。
- 不得從前身購書附件重製 Skill、Prompt、Workflow、模板、欄位或範例。
- 保留工程產物成熟度、有限主張種類與研究者裁定權。
- 使用者可見變更更新 `CHANGELOG.md`；版本變更同步 `VERSION` 與 `CITATION.cff`。

## 驗證

```shell
.venv/bin/python scripts/check_all.py
.venv/bin/python build.py --check
.venv/bin/python scripts/package_skill.py --output-dir .work/package-smoke
git diff --check
```

## Pull request 檢查表

- [ ] `skills/` 是唯一正式來源；Skill 邊界、內部連結與 metadata 有效。
- [ ] 來源、Evidence、Finding、人工決策與正式輸出未混寫。
- [ ] 新工程判準有契約、產物、反例與適用邊界。
- [ ] `planned` 沒有被誤寫成實際執行或結果。
- [ ] 無秘密、私有程式碼、可識別 Log、虛構引用或未授權出版內容。
- [ ] 新增或改動的腳本與模板有測試及文件。
- [ ] CHANGELOG、版本與發布內容一致。
- [ ] 全部品質命令通過；失敗項目已如實說明。
