# 開始使用

## Repository skill

先建置工具包，再從 `dist/agents-skills/` 安裝需要的 Skill。跨階段任務從 `$research-writing-workbench` 開始；單一任務可直接呼叫對應 Skill。呼叫時提供系統與版本、來源或工程產物位置、研究問題、可執行環境及不可變更內容。

```text
使用 $research-writing-workbench，為這個非同步命令建立 validation contract。先區分接受、效果與穩定三種完成語意，再根據我提供的測試與 Trace 建立 scenario matrix；沒有執行過的項目保持 planned。
```

建議先複製 [Engineering Question Brief](../skills/research-writing-workbench/assets/templates/engineering-question-brief.md) 與 [Validation Contract](../skills/research-writing-workbench/assets/templates/validation-contract.md)。缺少檔案時保留 `[未取得產物]`，尚未重現時保留 `[尚未重現]`。

## 一般 Markdown Prompt

不能載入 repository skill 時使用 [master prompt](../prompts/master-prompt.zh-TW.md)。先確認模型的資料保存與隱私政策，不要貼入 Token、私有程式碼、客戶資料或完整可識別 Log。

## 驗收

輸出至少要能回答：契約是什麼、執行能否重建、反例挑戰什麼、證據支持哪種主張、哪些內容不得宣稱，以及哪些項目仍待研究者裁定。
