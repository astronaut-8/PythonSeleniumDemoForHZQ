import requests
from bs4 import BeautifulSoup

'''
问卷的内容会作为我的prompt中的一部份，用爬虫把问题全都爬出来，不是项目工作流的一部分，但还是做一个记录
'''
url = "https://www.wjx.cn/vm/tGWa7U4.aspx"

# 模拟header
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36",
    "Referer": "https://www.wjx.cn/",  # 表示从问卷星首页跳转过来
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3"
}

try:
    # 携带请求头发送 GET 请求
    response = requests.get(url, headers=headers)
    response.raise_for_status()  # 检查请求是否成功
    response.encoding = response.apparent_encoding  # 自动匹配编码

    soup = BeautifulSoup(response.text, "html.parser")

    print("页面标题：", soup.title.get_text() if soup.title else "未获取到标题")

    # 查找 class 为 "topichtml" 的 div 标签
    topic_divs = soup.find_all("div", class_="topichtml")

    if topic_divs:
        print(f"找到 {len(topic_divs)} 个 class='topichtml' 的 div：")
        for idx, div in enumerate(topic_divs, 1):
            content = div.get_text().strip()
            print(f"{idx}，{content}")
    else:
        print("ERROR!!! Please Check!!!")

except requests.exceptions.RequestException as e:
    print(f"请求出错：{e}")
except Exception as e:
    print(f"解析或其他错误：{e}")