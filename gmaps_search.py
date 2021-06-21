import json
import time
import requests
import argparse
import googlemaps

#定義引數
parser = argparse.ArgumentParser()
parser.add_argument("arg1", nargs = 1, help = "請輸入1種商店類型 Ex:寵物店、桌游店...等")
parser.add_argument("arg2", nargs = '+', help = "請輸入至少1個縣市名稱")
args = parser.parse_args()

API_key = "AIzaSyCTWuFvVWyGP6wpGMdOkXQ4UPkZ0US2flA"
gmaps = googlemaps.Client(key = API_key)

# store = "寵物"
store = args.arg1[0]


# 將要搜尋的城市放進 list
# cities_list = ["台北市","新北市","桃園市","臺中市","臺南市","高雄市","基隆市","新竹市","嘉義市","新竹縣","苗栗縣","彰化縣","南投縣","雲林縣","嘉義縣","屏東縣","宜蘭縣","花蓮縣","臺東縣","澎湖縣"]
cities = []
for item in args.arg2:
    cities.append(item)

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

# 轉成 json 檔並輸出
f = open("output.txt", "w", encoding='UTF-8')
print(json.dumps(data, ensure_ascii=False, indent=2), file = f)
f.close()