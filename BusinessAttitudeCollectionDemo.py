# coding=utf-8
import logging
from CustomDataFromDeepSeek import get_custom_data_from_deepSeek
import JsonParseDemo
import re
import threading
import traceback
from threading import Thread
import time
from typing import List

import numpy
import requests
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By

"""
这是为惠芷清写的一个有关wjx问卷的自动数据收集+分析+填写的脚本
python我不熟悉，代码风格可能会有一股浓浓的java味
此次问卷星的源地址：https://www.wjx.cn/vm/tGWa7U4.aspx
"""

logging.basicConfig(
    level=logging.INFO,  # 日志级别设为 INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def custom_ip():
    api = "https://service.ipzan.com/core-extract?num=1&no=20251006181613485146&minute=1&pool=quality&secret=chmgpg1f9naiuco"
    ip = requests.get(api).text
    return ip

# url = "https://www.wjx.cn/vm/wVtu6Jl.aspx# "
url = "https://www.wjx.cn/vm/tGWa7U4.aspx"

# 校验IP地址合法性
def validate_ip(ip):
    pattern = r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):(\d{1,5})$"
    if re.match(pattern, ip):
        return True
    return False
# 检测题量
def detect_every_page(driver: WebDriver) -> List[int]:
    q_list: List[int] = []
    page_num = len(driver.find_elements(By.XPATH, '//*[@id="divQuestion"]/fieldset'))
    for i in range(1, page_num + 1):
        questions = driver.find_elements(By.XPATH, f'//*[@id="fieldset{i}"]/div')
        valid_count = sum(
            1 for question in questions if question.get_attribute("topic").isdigit()
        )
        q_list.append(valid_count)
    return q_list

def do_single(driver: WebDriver, current, num):
    xpath = f'//*[@id="div{current}"]/div[2]/div'
    driver.find_element(
        By.CSS_SELECTOR, f"#div{current} > div.ui-controlgroup > div:nth-child({num})"
    ).click()

def do_scale(driver: WebDriver, current, num):
    xpath = f'//*[@id="div{current}"]/div[2]/div/ul/li'
    driver.find_element(
        By.CSS_SELECTOR, f"#div{current} > div.scale-div > div > ul > li:nth-child({num})"
    ).click()
def get_data():
    testContent = "# 创业的真正魅力：超越财富的深层价值 \n 当被问及 “创业的真正魅力是什么”，多数人的第一反应往往是 “钱”—— 但财富只是创业价值中最浅显的一层。真正能驱动人穿越艰难、坚守长期的魅力，藏在更深刻的自我重塑与认知突破里，具体可归结为四个核心维度：\n\n\n## 一、在 “极端真实” 中看清自己 \n 创业会将人推向一个毫无遮蔽的现实环境，让你与世界 “赤膊相见”：你做出的每一个决策、犯下的每一个错误、抓住的每一个机会，都不会被模糊的反馈掩盖，反而会在极短时间内呈现明确结果。在这里，没有 “拖延的余地”，也没有 “逃避的空间”—— 你思考的质量、反应的速度、执行的力度，会直接转化为你的处境：可能是项目的快速增长，也可能是问题的集中爆发。\n\n 正是这种 “结果即时反馈” 的机制，让你第一次真切地认知自己：你真正想要的是什么（是短期收益还是长期价值）？能为目标放弃什么（是休闲时间还是固有舒适区）？自己的底线又在哪里（是坚守原则还是妥协利益）。这种对自我的清晰认知，是任何安稳环境都无法给予的 “镜子”。\n\n\n## 二、重构认知边界，打破 “可能性限制”\n 创业最隐秘的魅力之一，是它会不断推翻你对 “不可能” 的预设 —— 你会逐渐发现，很多你以为 “做不到” 的事，其实只是 “没人尝试过”；很多看似无法突破的 “天花板”，只是因为你站立的视角太低。\n\n 当你一次次推动项目突破自己预设的限制（比如从 0 到 1 做出第一个产品、从 10 到 100 拓展第一批客户），你对 “可能性” 的理解会彻底重构：原来世界不是非黑即白的 “能” 与 “不能”，而是存在无数待挖掘的中间地带。这种认知上的 “扩容”，会让你看待问题、看待世界的方式发生根本改变，从此不再被固有思维束缚。\n\n\n## 三、掌握定义规则的 “创造感”\n 创业更核心的魅力，在于它让你摆脱 “遵循他人规则” 的被动 —— 不是所有事情都要按行业既定的玩法走，你完全可以基于自己的判断，找到属于自己的路径。\n\n 这个过程中，你需要亲手构建一个完整的系统：从打磨产品解决用户需求，到搭建团队凝聚协作力量，再到打通渠道实现价值流转。你会看着这个系统从 “无” 到 “有”、从 “不稳定” 到 “稳步运转”，每一个环节的优化都源于你的决策，每一次成长都出自你的设计。这种 “从 0 到 1 创造并掌控系统” 的体验，会带来极强的成就感与掌控感，让你意识到自己不仅是规则的遵守者，更是规则的制定者。\n\n\n## 四、拥有掌控人生的 “主动权”\n 创业赋予的主动权，不是空洞的 “自由”，而是实实在在的 “分配权”—— 对资源的分配权（知道如何调动资金、人脉解决问题）、对时间的分配权（能自主规划优先级，而非被动应付任务）、对决策的分配权（可以按自己的长期目标做选择，而非受制于他人指令）。\n\n 随着能力的积累，你会逐渐进入一种 “从容应对变化” 的状态：当新的机会出现时，你有足够的资源和判断力立刻接住；当突发风险来临时，你有提前铺垫的退路可走。这种主动权，让你的人生不再只有 “按部就班” 一条轨迹，而是拥有多个 “备选方案”，从此不再被动接受命运的安排，而是主动塑造自己的人生走向。\n\n\n 所以，在我看来，创业的真正魅力从不是赚到多少财富，而是它能给你带来伴随一生的深层改变：在极端真实的反馈中看清自己，在一次次突破中拓宽认知，在创造系统中掌握规则，在积累中拥有人生的主动权。这些看不见的成长，比任何一笔具体的收入都更珍贵，也更能定义一个人的人生高度。"
    global data_index
    content = JsonParseDemo.dict_array[data_index]["desc"]
    while data_index < len(JsonParseDemo.dict_array) and len(content) < 100:
        content = JsonParseDemo.dict_array[data_index + 1]["desc"]
        data_index += 1
    if data_index == len(JsonParseDemo.dict_array):
        quit()
    logging.info(f"原始desc - {content}")
    return get_custom_data_from_deepSeek(content)

def brush_driver(driver: WebDriver):
    logging.info("开始获取数据源")
    # 每一次的数据源
    nums = get_data()
    logging.info(f"数据获取成功 - {nums}")
    current = 0
    questions = detect_every_page(driver)
    for j in questions:
        for k in range(1, j + 1):
            current += 1
            type = driver.find_element(By.CSS_SELECTOR, f'#div{current}').get_attribute("type")
            # 单选题
            if type == "3":
                do_single(driver, current, nums[current - 1])
            elif type == "5":
                do_scale(driver, current, nums[current - 1])
            else:
                logging.error("this type of question isn't supported")
        # 一页结束 -> 下一页 / 提交
        try:
            driver.find_element(By.CSS_SELECTOR, "#divNext").click()  # 点击下一页
            time.sleep(0.5)
        except:
            # 点击提交
            driver.find_element(By.XPATH, '//*[@id="ctlNext"]').click()
    final_submin(driver)

# 提交函数
def final_submin(driver: WebDriver):
    time.sleep(1)
    # 点击对话框的确认按钮
    try:
        driver.find_element(By.XPATH, '//*[@id="layui-layer1"]/div[3]/a').click()
        time.sleep(1)
    except:
        pass
    # 点击智能检测按钮，因为可能点击提交过后直接提交成功的情况，所以智能检测也要try
    try:
        driver.find_element(By.XPATH, '//*[@id="SM_BTN_1"]').click()
        time.sleep(3)
    except:
        pass
    # 滑块验证
    try:
        slider = driver.find_element(By.XPATH, '//*[@id="nc_1__scale_text"]/span')
        sliderButton = driver.find_element(By.XPATH, '//*[@id="nc_1_n1z"]')
        if str(slider.text).startswith("请按住滑块"):
            width = slider.size.get("width")
            ActionChains(driver).drag_and_drop_by_offset(
                sliderButton, width, 0
            ).perform()
    except:
        pass

def runs(xx, yy):
    option = webdriver.ChromeOptions()
    option.add_experimental_option("excludeSwitches", ["enable-automation"])
    option.add_experimental_option("useAutomationExtension", False)
    global cur_success, cur_fail
    while cur_success < target_num:
        if use_custom_ip:
            ip = custom_ip()
            option.add_argument(f"--proxy-server={ip}")
        driver = webdriver.Chrome(options=option)
        driver.set_window_size(550, 650)
        driver.set_window_position(x = xx, y = yy)
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {
                "source": 'Object.defineProperty(navigator, "webdriver", {get: () => undefined})'
            },
        )
        try:
            logging.info(f"第{cur_success + cur_fail}次尝试")
            driver.get(url)
            pre_url = driver.current_url
            brush_driver(driver)
            time.sleep(4)
            cur_url = (
                driver.current_url
            )
            if pre_url != cur_url:
                cur_success += 1
                logging.info(f"已填写{cur_success}份 - 失败{cur_fail}次 - {time.strftime('%H:%M:%S', time.localtime(time.time()))} ")
                driver.quit()
        except:
            traceback.print_exc()
            lock.acquire()
            cur_fail += 1
            lock.release()
            logging.error(f"已失败{cur_fail}次,失败超过{int(fail_threshold)}次(左右)将强制停止")
            # 失败阈值
            if cur_fail >= fail_threshold:
                logging.critical(
                    "失败次数过多，为防止耗尽ip余额，程序将强制停止，请检查代码是否正确"
                )
                quit()
            driver.quit()
            continue



if __name__ == "__main__":
    # 目标数量
    target_num = 1
    # 笔记index
    data_index = 0
    #失败阈值
    fail_threshold = target_num / 4 + 1
    #成功次数
    cur_success = 0
    #失败次数
    cur_fail = 0
    #lock
    lock = threading.Lock()
    #是否使用自定义ip
    use_custom_ip = False
    #是否结束
    stop = False

    if validate_ip(custom_ip()):
        print("IP设置成功，使用代理IP")
        # use_custom_ip = True
    else:
        print("IP设置失败，将使用本机IP")

    #窗口数量
    thread_num = 1
    threads: list[Thread] = []

    for i in range(thread_num):
        x = 50 + i * 60
        y = 50
        thread = Thread(target=runs, args=(x, y))
        threads.append(thread)
        thread.start()

    # thread join
    for thread in threads:
        thread.join()


