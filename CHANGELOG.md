# Changelog

本專案依 [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) 維護變更，版本採 Semantic Versioning。

## [Unreleased]

## [1.0.0] - 2026-08-03

### Added

- 新增研究規劃、文獻盤點、證據抽取、研究綜整、方法審查、論文寫作、正式匯出與風險追蹤八個獨立 Skill；原 `research-writing-workbench` 保留為 CTCC 路由與相容入口。
- 新增 Source Catalog、Research Evidence、Corpus Snapshot、Finding、Checklist 與 Decision Log 六份 JSON Schema，以及驗證、Checklist 同步、人工決策與正式匯出 CLI。
- 新增白名單、暫存 staging、固定 ZIP metadata、SHA-256 manifest 與自足依賴檢查的可重現 `build.py`。
- 新增 Windows／Linux `.venv` CI、合成 fixture、治理與封裝回歸測試、安裝／資料契約／使用／遷移文件與論文研究寫作指令。

### Changed

- 正式 Skill 原始碼由 `.agents/skills/` 遷移到 `skills/`；建置後的 `dist/agents-skills/` 作為自足安裝來源。
- `README.md` 改為英文主檔，新增 `README.zh-TW.md`；`README.en.md` 保留相容入口。
- 專案 Python 開發、測試與建置改為只透過 repository `.venv`。
- 專案授權由 Apache License 2.0 改為 MIT License，並同步更新 `CITATION.cff`、README 與授權治理文件。
- `NOTICE` 改名為 `THIRD_PARTY_NOTICES.md`，繼續說明參考書籍與購書附件不屬於本專案授權範圍。

### Compatibility

- 保留既有 Skill 名稱、CTCC 成熟度、主張種類、研究者裁定、未解標記、Markdown 模板與 `package_skill.py --output-dir`。
- 本版本只建立本機發行候選；未建立 tag 或 GitHub Release，也不代表平台安裝、研究有效或第三方內容授權已通過。

## [0.1.0] - 2026-08-02

### Added

- 從空白 Git 歷史建立軟體工程與事件驅動系統研究工作台。
- 獨立設計契約—軌跡—反例—主張（CTCC）控制環。
- 新增九個工程研究資料格式、六份領域 reference、repository skill 與通用 Prompt。
- 新增方法來源與購書附件隔離政策，以及防止前身架構回流的驗證測試。
- 新增合成事件研究規畫、隱私掃描、可重現封裝、unittest 與 GitHub Actions。
