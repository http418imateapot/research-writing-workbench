# ADR 0001：Skill 作為唯一正式來源

狀態：Superseded by ADR 0003

## 決策

原決策以 `.agents/skills/research-writing-workbench/` 作為唯一正式技能來源。1.0.0 起由 ADR 0003 的 `skills/` 工具包原始碼取代；README、docs 與 prompts 仍不複製完整方法正文。

## 理由與影響

單一來源降低規則漂移與發布誤收風險。代價是一般 Prompt 需要人工同步其介面契約，因此驗證與 review 必須檢查兩者關鍵防護是否一致。
