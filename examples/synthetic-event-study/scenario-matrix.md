# Scenario Matrix

| scenario ID | 類別 | 前置狀態 | 刺激或故障 | 預期可觀察行為 | 反駁對象 | 成熟度 |
|---|---|---|---|---|---|---|
| SC-001 | normal | 計數器 0 | 一個新事件 | 只更新一次 | 基本契約可觀察性 | planned |
| SC-002 | duplicate | 計數器 0 | 相同 ID 重播兩次 | 仍只更新一次 | 冪等解釋 | planned |
| SC-003 | out-of-order | 兩個具順序的事件 | 後發事件先到 | 依契約處理或拒絕 | 順序處理假設 | planned |
| SC-004 | concurrent-write | 計數器 0 | 兩個寫入者處理相同 ID | 不發生重複更新 | 並行安全解釋 | planned |

本矩陣沒有實際執行結果。
