# gmaps_search
使用方法: 在存放的資料夾下運行 gmaps_search.py 文件即可 
需輸入引數，指令範例如下: python gmaps_search.py 桌游(arg1) 花蓮縣 台北市(arg2)
- arg1:需輸入一種店家類型:如桌游店、寵物店..等等
- arg2:需輸入至少一個以上的縣市名稱，如花蓮縣、台北市...等等
有使用到 requests 和 googlemaps 函式庫，需自行安裝，指令如下
``` python
- pip install requests
- pip install googlemaps
```

## gmaps_search.py
目的:利用google map的API獲取一座城市中某類店家的相關資料及客戶評論，方便進行篩選
輸出格式為json格式

### 定義引數
定義引數的部分
``` python
parser = argparse.ArgumentParser()
parser.add_argument("arg1", nargs = 1, help = "請輸入1種商店類型 Ex:寵物店、桌游店...等")
parser.add_argument("arg2", nargs = '+', help = "請輸入至少1個縣市名稱")
args = parser.parse_args()
```

### 連接API
API連接設定的部分
``` python
API_key = "你的API key"
gmaps = googlemaps.Client(key = API_key)
```

### 實作部分

#### 接收引數
處理收進來得引數
``` python
store = args.arg1[0]

cities = []
for item in args.arg2:
    cities.append(item)
```

#### 利用API獲取資料
因為API回傳資料有上限，所以最多可以得到60筆店家資料
``` python
data = {}
ids = []
for city in cities:
    results = []
    # 利用 Geocode 的 API 獲取城市的地理資料
    geocode_result = gmaps.geocode(city)
    loc = geocode_result[0]['geometry']['location']
    result = gmaps.places_nearby(keyword = store, location = loc, radius=10000)

    # 因為 places_nearby 一次只會回傳20筆資料，所以要用 next_page_token 繼續抓資料，最多可以抓到60筆
    results.extend(result['results'])    
    while result.get('next_page_token'):
        time.sleep(2)
        result = gmaps.places_nearby(page_token = result['next_page_token'])
        results.extend(result['results'])

    # API 上限提供60間
    print("找到以" + city + "為中心，半徑10000公尺內的" + store + "店家數量: "+str(len(results)))
    #將 place_id 存入 ids list
    for place in results:
        ids.append(place['place_id']) 

    # 去除重複id
    ids = list(set(ids))
```

#### 獲取評論
利用 placeid ，並透過發送 request 來得到店家評論的資料，最多可以得到5筆評論，並按照評論分數來排序
``` python
    key = "https://maps.googleapis.com/maps/api/place/details/json?key="
    placeid = "&placeid="
    lan = "&language=ZH_TW"
    info_list = []

    # 利用 place_id 來取得店家的評論資料， API 最多會回傳5筆資料
    for id in ids:
        # 利用 url 來發出 request
        url = key + API_key + placeid + id + lan
        r = requests.get(url)
        r.encoding = 'utf8'
        # 將回傳的 json 檔轉成 dictionary
        json_to_dict = json.loads(r.text)

        # 將店家資料以及客戶的評論存入 dictionary
        info = {}
        reviews = []
        info["name"] = json_to_dict["result"]["name"]
        info["rating"] = json_to_dict["result"]["rating"]
        info["formatted_address"] = json_to_dict["result"]["formatted_address"]
        for item in json_to_dict["result"]["reviews"]:
            review = {}
            review["author_name"] = item["author_name"]
            review["text"] = item["text"]
            review["rating"] = item["rating"]
            reviews.append(review)
        
        # 按照評價排序
        reviews = sorted(reviews ,reverse = True ,key = lambda d: d["rating"])

        info["reviews"] = reviews
        info_list.append(info)

    # 按照評價排序
    info_list = sorted(info_list ,reverse = True ,key = lambda d: d["rating"])

    # 存完一個城市後將 ids 清空
    data[city] = info_list
    ids.clear()
```

#### 輸出檔案
轉成 json 格式並輸出檔案 output.txt
```python
# 轉成 json 檔並輸出
f = open("output.txt", "w", encoding='UTF-8')
print(json.dumps(data, ensure_ascii=False, indent=2), file = f)
f.close()
```

### 輸出結果
詳細可以看 output.txt
大致結果如下

#### 店家資料:
列出店家名稱、地址和評分
![image](https://github.com/Ashforrd/1071514_Final/blob/master/%E5%BA%97%E5%AE%B6%E5%9F%BA%E6%9C%AC%E8%B3%87%E6%96%99.png)

#### 顧客評論:
顧客評論會放在reviews內，每家店有5筆，按照評分高低來排列
![image](https://github.com/Ashforrd/1071514_Final/blob/master/%E9%A1%A7%E5%AE%A2%E8%A9%95%E8%AB%96.png)