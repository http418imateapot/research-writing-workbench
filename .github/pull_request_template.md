## What and why

Describe the scoped change, affected contracts, and evidence for new research criteria.

## Validation

- [ ] `.venv` Python compileall、pytest、repository validator 與 privacy scan 通過
- [ ] `.venv` Python `build.py --check` 與完整建置通過
- [ ] 連續兩次完整建置的 ZIP SHA-256 相同
- [ ] `git ls-files dist` 無輸出
- [ ] 舊 `package_skill.py --output-dir` 相容測試通過
- [ ] Skill metadata、prompt-template、reference 與自足 private import 通過驗證
- [ ] 來源、Evidence、Finding、Checklist、Decision Log 與正式輸出未混寫
- [ ] `git diff --check`
- [ ] Privacy and identifiable-content review

## Review boundaries

- [ ] No duplicate canonical content, fabricated citations, results, private cases, or unsupported benefits
- [ ] CTCC, actual-execution evidence, bounded claim types, and researcher decision rights remain intact
- [ ] No purchaser-only attachment, private engineering artifact, or identifiable log content is included
- [ ] User-visible changes update documentation, tests, and CHANGELOG where required
