# coding=utf-8

import logging
import JsonParseDemo
import re
import threading
import traceback
import time
import requests
from CustomDataFromDeepSeek import get_custom_data_from_deepSeek
from threading import Thread
from typing import List
from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By



"""
这是为惠芷清写的一个有关wjx问卷的自动数据收集+分析+填写的脚本
python我不熟悉，代码风格可能会有一股浓浓的java味
此次问卷星的源地址：https://www.wjx.cn/vm/tGWa7U4.aspx
"""

# 日志设置
logging.basicConfig(
    level=logging.INFO,  # 日志级别设为 INFO
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def custom_ip():
    api = "https://service.ipzan.com/core-extract?num=1&no=20251006181613485146&minute=1&pool=quality&secret=chmgpg1f9naiuco"
    ip = requests.get(api).text
    return ip

# test_url = "https://www.wjx.cn/vm/wVtu6Jl.aspx# "
url = "https://www.wjx.cn/vm/tGWa7U4.aspx"

# 校验IP地址合法性
def validate_ip(ip):
    pattern = r"^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?):(\d{1,5})$"
    if re.match(pattern, ip):
        return True
    return False

# 检测题量(每一页的题目数量，应对存在分页的情况)
def detect_every_page(driver: WebDriver) -> List[int]:
    q_list: List[int] = []
    page_num = len(driver.find_elements(By.XPATH, '//*[@id="divQuestion"]/fieldset'))
    for page in range(1, page_num + 1):
        questions = driver.find_elements(By.XPATH, f'//*[@id="fieldset{page}"]/div')
        valid_count = sum(
            1 for question in questions if question.get_attribute("topic").isdigit()
        )
        q_list.append(valid_count)
    return q_list

# 处理单选题
def do_single(driver: WebDriver, current, num):
    driver.find_element(
        By.CSS_SELECTOR, f"#div{current} > div.ui-controlgroup > div:nth-child({num})"
    ).click()

# 处理态度打分题
def do_scale(driver: WebDriver, current, num):
    driver.find_element(
        By.CSS_SELECTOR, f"#div{current} > div.scale-div > div > ul > li:nth-child({num})"
    ).click()

# 获取此次任务的打分数据
def get_data():
    global data_index
    # data_index递增
    content = JsonParseDemo.dict_array[data_index]["desc"]
    # 过滤掉内容比较水的文章，可以去调整这个阈值
    while data_index < len(JsonParseDemo.dict_array) and len(content) < 100:
        content = JsonParseDemo.dict_array[data_index + 1]["desc"]
        data_index += 1
    if data_index == len(JsonParseDemo.dict_array):
        logging.critical("数据源数量不足!!!")
        quit()
    logging.info(f"原始desc - {content}")
    return get_custom_data_from_deepSeek(content)

# 每一次工作实际的处理函数
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
            question_type = driver.find_element(By.CSS_SELECTOR, f'#div{current}').get_attribute("type")
            # 单选题
            if question_type == "3":
                do_single(driver, current, nums[current - 1])
            elif question_type == "5":
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
        # 这里还是把它禁止了，这次背景没有必要，用了太卡了，而且容易失败
        # use_custom_ip = True
    else:
        print("IP设置失败，将使用本机IP")

    #窗口数量 选择单线程执行，因为每次ip一样，以防他对快速提交的ip会做什么事情
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


