import datetime
import requests

import json

file = open("SECRET.json")
data = json.load(file)


def fun_home_page(last_time, IDS):
    TOKEN, HOME_ID, HOME_IMAGE_ID = IDS["id"], IDS["database"]["Home"], IDS["database"]["Home_Image"]
    headers = {
        'Authorization': f'Bearer {TOKEN}',
        "accept": "application/json",
        'Content-Type': 'application/json',
        'Notion-Version': '2021-08-16'
    }
    now = datetime.datetime.now().time()
    day_of_year = datetime.datetime.now().timetuple().tm_yday
    url_list = [[
                    "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/26e9a635-1a71-44e0-a8a3-5f4cbebcd305/1-1.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T193420Z&X-Amz-Expires=3600&X-Amz-Signature=2cb561e94b5519d70ef3219de7ed8c29856ee165a9dac3be66c430579e77a78d&X-Amz-SignedHeaders=host&x-id=GetObject",
                    "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/095c13ed-2786-46c5-aab0-1916ae90cb62/3-2.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T192932Z&X-Amz-Expires=3600&X-Amz-Signature=ba72f6e1659b5cc50e148a837a5aa901fe713848d388eb619fc7516b14c16350&X-Amz-SignedHeaders=host&x-id=GetObject",
                    "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/1faa89b9-98a1-4320-8c7a-7613d82959c1/1-3.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T193455Z&X-Amz-Expires=3600&X-Amz-Signature=5c86687a84304253fa76764117130bf7b33aeea9b7f25ba5d2da75cb49b97c4b&X-Amz-SignedHeaders=host&x-id=GetObject",
                    "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/6855024a-e092-4c83-82c5-38a230016cb5/1-4.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T193537Z&X-Amz-Expires=3600&X-Amz-Signature=46b8342c92f14f621abaa54392ae9555861bdffdb2347f3df784c31c87d4cb5e&X-Amz-SignedHeaders=host&x-id=GetObject"],
                [
                    "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/902caecb-6175-4869-907c-aa7093fc1ca4/2-1.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T193656Z&X-Amz-Expires=3600&X-Amz-Signature=71c7ded9bb342c63fab32c559a877beff29357c7d1c11309a88c207814033e1e&X-Amz-SignedHeaders=host&x-id=GetObject",
                    "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/8c810358-78a4-4024-b7d5-0dbfdbf60e64/2-2.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T193934Z&X-Amz-Expires=3600&X-Amz-Signature=5a144ea01ca3e4cc130733c8f5d67d37e6d578420c366734e100565f826dde9c&X-Amz-SignedHeaders=host&x-id=GetObject",
                    "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/7fb9b891-9422-46c4-aac1-9815034568fc/2-3.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T193951Z&X-Amz-Expires=3600&X-Amz-Signature=c167bf7ca9ca4d21e739f290217599f72cbdf0717a3aff32dcdaf6dd54ac78f1&X-Amz-SignedHeaders=host&x-id=GetObject",
                    "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/ca9cbcc3-6665-4218-948b-133834dfe6fd/2-4.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T194016Z&X-Amz-Expires=3600&X-Amz-Signature=e6738d218339f6eaa444d5bf8543390e7135e819ed7dba17e13464a10fe39e51&X-Amz-SignedHeaders=host&x-id=GetObject"]]
    url = f"https://api.notion.com/v1/pages/{HOME_ID}"
    block_url = f"https://api.notion.com/v1/blocks/{HOME_IMAGE_ID}"
    block_url_list = [
        "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/f1cb7ecd-9405-4e66-8772-51802d2823d2/1.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T220535Z&X-Amz-Expires=3600&X-Amz-Signature=e5198c47e5bb3b741161ae20c885e319422a04900bb973563fabc53054ba118a&X-Amz-SignedHeaders=host&x-id=GetObject",
        "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/7d960cca-6136-48c0-9e04-b8a0f69be048/2.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T220604Z&X-Amz-Expires=3600&X-Amz-Signature=a599f15b17b1215f5da8d59d542ec606714c713bac575a9598cc12d42d3154c8&X-Amz-SignedHeaders=host&x-id=GetObject",
        "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/7d960cca-6136-48c0-9e04-b8a0f69be048/2.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T220604Z&X-Amz-Expires=3600&X-Amz-Signature=a599f15b17b1215f5da8d59d542ec606714c713bac575a9598cc12d42d3154c8&X-Amz-SignedHeaders=host&x-id=GetObject",
        "https://s3.us-west-2.amazonaws.com/secure.notion-static.com/e809329e-30c8-4554-9512-ad5b6862e6d6/3.jpg?X-Amz-Algorithm=AWS4-HMAC-SHA256&X-Amz-Content-Sha256=UNSIGNED-PAYLOAD&X-Amz-Credential=AKIAT73L2G45EIPT3X45%2F20230510%2Fus-west-2%2Fs3%2Faws4_request&X-Amz-Date=20230510T220650Z&X-Amz-Expires=3600&X-Amz-Signature=468e5fe9f7759053bc14fae9b748a82d1f664826a65e94293073b88c790b71ed&X-Amz-SignedHeaders=host&x-id=GetObject"]

    def change_home_cover_image(n):
        r1 = requests.patch(url=url, json={"cover": {"external": {"url": url_list[day_of_year % 2][n]}}}, headers=headers)
        r2 = requests.patch(url=block_url, json={"image": {"external": {"url": block_url_list[n]}}}, headers=headers)
        return [r1, r2]

    if datetime.time(hour=5) <= now <= datetime.time(hour=9, minute=30) and last_time != 0:
        change_home_cover_image(0)
        return 0
    elif datetime.time(hour=9, minute=30) <= now <= datetime.time(hour=13, minute=5) and last_time != 1:
        change_home_cover_image(1)
        return 1
    elif datetime.time(hour=13, minute=5) <= now <= datetime.time(hour=19) and last_time != 2:
        change_home_cover_image(2)
        return 2
    elif datetime.time(hour=19) <= now or now <= datetime.time(hour=5) and last_time != 3:
        change_home_cover_image(3)
        return 3
    return last_time


print(fun_home_page(0, data))
