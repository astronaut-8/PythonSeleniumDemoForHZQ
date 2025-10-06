import logging
import random
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

url = "https://www.wjx.cn/vm/wVtu6Jl.aspx# "

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
    return [3, 4]
def brush_driver(driver: WebDriver):
    # 每一次的数据源
    nums = get_data()
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


