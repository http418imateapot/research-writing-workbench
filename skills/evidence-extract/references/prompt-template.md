# Prompt Template

## Input

- 具 source ID、版本與定位資訊的來源材料。
- 研究問題或待檢查 Claim。

## Output

- 可追溯 Evidence Record、分類、衝突與缺漏。

## Required

- 保存來源 ID、SHA-256、locator、摘錄雜湊與分類。
- 將直接觀察、衍生計算與推論分開。

## Forbidden

- 補造未報告數值、頁碼、事件或結論。
- 以 AI 摘要取代來源定位。

## Positive example

「從 SRC-001 第 4.2 節抽取作者明示限制，標為 explicit 並保存定位與摘錄雜湊。」

## Negative example

「來源沒寫樣本數，請合理補一個。」
