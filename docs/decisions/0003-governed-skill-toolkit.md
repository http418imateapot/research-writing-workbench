# ADR 0003：受治理多 Skill 工具包

狀態：Accepted

## 情境

單一 CTCC Skill 能處理工程研究核心，但無法清楚區分文獻檢索、證據抽取、研究綜整、方法審查、正式寫作、匯出與風險追蹤的不同觸發、輸入、輸出與成功條件。原封裝也缺少共享資料契約、自足依賴白名單與整合包。

## 決策

保留 `research-writing-workbench` 為 CTCC 路由與相容入口，新增八個可獨立觸發的 Skill。以 `skills/` 為唯一 Skill 原始碼、`shared/` 為治理資源單一來源、`scripts/` 為確定性 CLI，並由 `build.py` 依白名單組裝自足包。

## 後果

作者須維護明確 Skill 邊界、跨階段穩定 ID、build maps 與治理回歸測試。Repository 直接發現路徑改為建置後安裝 `dist/agents-skills/`；原 Skill 名稱、CTCC 契約、模板與舊封裝 CLI 保持相容。
