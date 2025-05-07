# 📂 Urosmart
>UroSmart住院病患尿袋尿量監控警示系統
<p align="center">
  
  <a href="https://github.com/usertracychen/Portfolio/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/usertracychen/Portfolio/ci.yml?branch=main"></a>
  <a href="LICENSE"><img alt="License" src="https://img.shields.io/github/license/usertracychen/Portfolio"></a>
  <a href="https://github.com/usertracychen/Portfolio/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/usertracychen/Portfolio?style=social"></a>
</p>


## 📑 目錄

- [動機與目的](#動機)
- [材料](#材料)
- [系統架構](#系統架構)
- [資料庫規劃](#資料庫規劃)
- [結果展示](#結果展示)
- [未來方向](#未來方向)
- [備註](#備註)


## 💡動機：
1.	難以及時判斷異常排尿情況
2.	滿袋或洩漏時的緊急風險
3.	無法長期保存與分析尿量資料
4.	失能或長期臥床者照護壓力大
5.	人工巡視不定期且易疏漏
   
## 🎯目的：
1.	系統旨在透過 ESP8266 搭配 HX711 與 load cell 進行尿袋重量（或尿量）監控，並藉由後端服務進行數據儲存與警示，最終透過 Web 供護理人員及家屬即時查詢狀態與接收異常通知。
2.	系統主要應用於預防尿液逆流、感染及早期發現排尿異常，提升護理效率。


## 🧰材料：

  - <mark>硬體</mark>
  1.	NodeMCU（ESP8266）
  2.	HX711重量感測模組件
  4.	蜂鳴器
     
  ![456](https://github.com/user-attachments/assets/3b8ecb00-b84a-4455-ba01-ae8000309fb4)  ![1123](https://github.com/user-attachments/assets/2b633bcb-9b08-4f4c-913c-19987f7c24ed) ![7892](https://github.com/user-attachments/assets/9b116d13-5d4c-45ab-b087-6b4503686289)


  - <mark>軟體工具</mark>
  1.	python Django
  2.	html/CSS/bootstrap
  3.	MYSQL Workbench
  4.	VSCODE
  5.	Arduino IDE

## 🌐系統架構：
<img width="600" src="https://github.com/user-attachments/assets/d5f8acfa-1e9a-45dc-8611-e627298a5d01"/>

## 🛢資料庫規劃：

<img width="500" src="https://github.com/user-attachments/assets/3bfcb452-168d-460d-91f6-556e4997f6e4"/>

## 📊結果展示：

[![image](https://github.com/user-attachments/assets/274ad75e-8446-44ce-aa19-f86481de0a4f)](https://www.youtube.com/watch?v=7tiOgXCAmHo)
- <h3>首頁</h3>

<img width="500" alt="圖片1" src="https://github.com/user-attachments/assets/a0748917-020a-4062-adc5-217fd4efdb4a" />  <img width="500" src="https://github.com/user-attachments/assets/88957144-c58b-4c8d-88c9-90096131925d"/>
<img width="500" src="https://github.com/user-attachments/assets/9b1ef12d-f647-4457-9c4f-52b6577fdf77"/> <img width="500" src="https://github.com/user-attachments/assets/a871b000-2c27-4052-849d-44d5a2cd0e69"/>


- <h3>系統管理員/護理人員皆有的功能</h3>
<mark>登入頁面</mark>
|畫面截圖|說明|
|--------|----|
|<img width="500" src="https://github.com/user-attachments/assets/3d187a1d-8607-4b19-b165-1d15a03a71ed"/>|輸入帳號、密碼、驗證碼皆正確以及帳號有啟用才會成功登入|


<mark>儀表板</mark>
|畫面截圖|畫面截圖|
|--------|----|
|<img width="500" src="https://github.com/user-attachments/assets/38732273-60ac-4071-9c45-0f599a7b85f3"/>|<img width="500" src="https://github.com/user-attachments/assets/2cdfb38b-4007-484f-b401-95b556a14528"/>|
|<img width="500" src="https://github.com/user-attachments/assets/66e44b5e-d6bc-4a78-84c0-de6a5d70854e"/>|<img width="500" src="https://github.com/user-attachments/assets/ef206955-6511-4933-b023-616167ec0e64"/>|
|功能說明|技術說明|
| - 可以彈性調整卡片顯示個數(透過病房管理) <br>- 卡片內資料是否顯示，依據當下是否有裝置運行及該病房是否有住<br>人，有則顯示資料;無則不顯示資料。<br>- 資料內容會自動每10秒更新顯示，不用手動點重新整理。<br>- 狀態正常與狀態警示計數卡片內容會依據實際情況動態變化。<br>- 卡片有資料內容，可點選「詳細資訊」進入當日尿量圖表頁面。|<h4>1.	Django Template + Bootstrap</h4> -使用 {% extends %}、{% for %}、{% if %} 動態產生卡片。<br>-Bootstrap grid (.row, .col-md-6, .card) 實現響應式 RWD。<h4>2.CSS 自訂</h4> .room-card 調整圓角、陰影、懸停動畫，提升 UX。<h4>3.AJAX 輪詢</h4>-fetch() 搭配 async/await，每 10s 自動重載 JSON 資料。<br>-用 JavaScript template literals 動態組裝卡片 <br>HTML，減少整頁重載。<h4>4.分離關注點</h4>- 一開始 Server‐side render 出初始畫面<br>（cards、normal_count、warning_count）。<br>-之後純粹靠前端呼叫 JSON API 做局部更新。|

<mark>歷史紀錄</mark>
|畫面截圖|畫面截圖|
|--------|----|
|![image](https://github.com/user-attachments/assets/a7403e11-f0b8-4aad-a3e1-401d759104e4)|![image](https://github.com/user-attachments/assets/cda62169-ad55-4d7b-9596-4d9c8cecbbcc)|
|功能說明|技術說明|
|- 可以依病患病歷號or日期區間進行搜尋尿量raw data <br>- 除了raw data也可以查詢以"一天"累計的尿量|<h4>計算某個病患在某天的「總尿量」，透過分析感測裝置回傳的數值變化。</h4>	降幅大於容差 時認定為一次「排尿」，累加其絕對值。<br>	無排尿事件時，以當日最後量測結果當作累積尿量。|

<mark>住出院管理</mark>
|畫面截圖|畫面截圖|
|--------|----|
|![image](https://github.com/user-attachments/assets/d4448310-007d-443a-aa23-cccb51ec83db)|![image](https://github.com/user-attachments/assets/8c074818-819c-429c-b35e-2f18985cbd4b)|
|![image](https://github.com/user-attachments/assets/9fc6873f-640b-47cd-ad44-e6c70aa1a1e8)|![image](https://github.com/user-attachments/assets/0833db65-f87a-42b2-aaea-92b17a9bec8b)|
|![image](https://github.com/user-attachments/assets/c7f5b74a-5aa8-45b6-914e-6b7925ab98ea)|![image](https://github.com/user-attachments/assets/f0c1db40-c238-4b47-b544-acc8c55e5e3e)|
|![image](https://github.com/user-attachments/assets/ee3a4bec-9c4a-4ee2-822e-2b2c539b52a3)||
|功能說明|技術說明|
|-當前住院列表顯示的病房列表是與病房管理設定同步的<br>-當設定了住院病患，歷史入住紀錄便會新增一筆資料，還未出院就不會有出院時間<br>-歷史入住紀錄可以進行日期區間搜尋|利用 Django 的 Signals 機制，<br>讓不同模型之間在「新增／修改／刪除」事件發生時<br>能自動互相同步，而不必硬編碼呼叫彼此的函式。|

- <h3>設定—系統管理員</h3>
<mark>帳號管理</mark>
|畫面截圖|說明|
|--------|----|
|![image](https://github.com/user-attachments/assets/1c4b83de-c2b9-41da-9849-6cd6dcc16940)|-新增/編輯/刪除/搜尋帳號功能<br>-啟用/停用帳號功能(利用Ajax切換)|

<mark>設備管理</mark>
|畫面截圖|畫面截圖|
|--------|----|
|![image](https://github.com/user-attachments/assets/8bb7bb31-81c9-4ff6-8ad1-b3b3b4989aed)|![image](https://github.com/user-attachments/assets/e135dd80-56c3-4df8-899c-ffc429971340)|
|![image](https://github.com/user-attachments/assets/ad141794-a6b9-4d00-90f2-3944c7dd0a90)||


|功能說明|技術說明|
|--------|----|
|-透過裝置連網來新增裝置<br>-設定裝置放置位置、警報閾值、資料傳輸URL<br>-顯示裝置連線狀態<br>-刪除列表中裝置|---裝置連上網後，以”POST”方式，透過API <br>http://XXX.XXX.XXX.XXX:XXXX/devices/register_device/ 進行裝置註冊，<br>傳送資料內容為{”chip_id”: “String”}。若註冊裝置沒有完成不會進行重量資料傳輸。<br>---裝置完成註冊後，開始進行重量資料傳輸，<br>以”POST”方式每5秒，透過API http:// XXX.XXX.XXX.XXX:XXXX /devices/sensor/data/ 傳送，<br>傳送資料內容為x-www-form-urlencoded，例如 chip_id=XXX &value=5.0&location=6651&status=正常&patient_id=P001；response為{"status": "ok","threshold":100,"url":<br>http://XXX.XXX.XXX.XXX:XXXX/devices/sensor/data/ ,"room":6652,"patient_id":p001}<br>---備註：第1次傳輸時location和patient_id為空值、threshold預設為100。在每次傳送重量資料時，用收到response 內容來更新下一次傳送資料內容location和patient_id，並且更新裝置threshold，使其因應新的閾值來進行警報。<br>---status狀態正常or警示是在硬體內做判別。<br>---裝置連線狀態connect或disconnect 是利用APScheduler排程任務：定時(5秒)跑 background job 更新資料庫，這邊的background job是去判斷裝置最新一筆資料的時間戳記與當下時間差，設定小於等於10秒，則更新資料庫狀態為connect，大於10秒則更新為disconnect。|

<mark>病房管理</mark>
|畫面截圖|畫面截圖|
|--------|----|
|![image](https://github.com/user-attachments/assets/e97ea59f-6dc9-4835-b717-09731fa70faa)|![image](https://github.com/user-attachments/assets/51e79fcd-92ad-4fe8-a357-d0794db87d91)|
|功能說明|技術說明|
|--新增/編輯/刪除病房<br>--住出院管理「目前住院列表」之病房欄位與病房管理的病房號碼顯示一致。<br>--儀錶板的病房卡片的房間與與病房管理的病房號碼設定為顯示的一致。|利用 Django 的 Signals 機制，讓不同模型之間在<br>「新增／修改／刪除」事件發生時能自動互相同步，<br>而不必硬編碼呼叫彼此的函式。每當 RoomConfig <br>被刪除（delete）時觸發，自動把對應的 LocationPatient 一併移除<br>; 每當RoomConfig 被儲存（save）時觸發，建立一筆 LocationPatient。|

- <h3>病患列表—護理人員</h3>
|畫面截圖|畫面截圖|
|--------|----|
|![image](https://github.com/user-attachments/assets/60ff9846-1777-47cf-bde9-e34103bf1750)|![image](https://github.com/user-attachments/assets/6ad307cf-e2f8-496e-9b45-4eee180f2f48)|
|功能說明|功能說明|
|-當有住院病患時會顯示於此列表|-護理人員可以治全部病患列表選擇當班負責病患至我的病患|
- <h3>照顧者登入</h3>
|畫面截圖|畫面截圖|
|--------|----|
|![image](https://github.com/user-attachments/assets/9327a911-842e-4821-9815-41bf608f0eb1)|![image](https://github.com/user-attachments/assets/452a6bdd-8f48-40c6-9791-f22cb4aa3bf9)|

## 🌟未來方向：
1.	整合 AI 尿量異常分析模型
蒐集足夠歷史尿量資料後，應用機器學習（如 LSTM）建立個人化的排尿行為預測模型，提早預測脫水、尿滯留、腎功能異常等情況。
2.	結合病歷與護理紀錄系統（EMR/NIS）
提供 API 串接功能，讓 UroSmart 所產生的資料可被醫療院所既有的電子病歷系統整合使用，強化照護流程一致性。

## 備註:
1. esp8266Code 為硬體程式碼，需要填上wifi ssid & password 和正確的url
2. urosmart 為網頁程式，其中setting中的mysql 要設定號帳號密碼








