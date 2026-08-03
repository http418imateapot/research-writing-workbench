---
name: research-planning
description: Plan bounded, testable thesis and software-engineering research. Use when a user asks to define a research problem, question, scope, protocol, variables, validation contract, scenario matrix, milestone plan, or acceptance criteria before collecting evidence; trigger on 研究規劃、研究問題、論文計畫、研究設計、proposal, protocol, or experiment plan. Do not present planned work as executed evidence.
---

# Research Planning

把題目轉成可反駁、可執行、可追溯的研究計畫。將所有尚未執行的工作保持為 `planned`。

## 執行流程

1. 確認研究對象、版本、觀察到的問題、分析單位、利害關係人與不可變更範圍。
2. 產生最多三個候選研究問題；每題列出可觀察結果、反駁條件、排除範圍與缺少資料。
3. 選定問題後，定義輸入、輸出、完成語意、錯誤、逾時、重試、順序、併發、環境與比較公平性。
4. 建立正常、邊界、故障、反例與觀測缺口情境；不要只列預期成功案例。
5. 將每個情境連到預計取得的來源、程式、測試、Trace、Log、資料或人工裁定。
6. 列出里程碑、前置條件、停止條件、決策點、隱私與授權檢查。
7. 把尚未提供的材料標為 `[未取得產物]`，尚未執行的案例標為 `[尚未重現]`。

## 輸出契約

依序交付研究問題與範圍、驗證契約、情境矩陣、證據取得計畫、反例、里程碑、停止條件及研究者待裁定事項。不得生成結果、效益、樣本數、統計顯著性或已完成敘述。

先讀取 [prompt-template.md](references/prompt-template.md)，並依 Input、Required 與 Forbidden 欄位檢查輸入。
