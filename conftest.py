# encoding=utf-8
import base64

import pytest, time, logging, os ,json
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


url = 'http://spider.aikonchem.com:9013'

@pytest.fixture(scope='class')  # 表示这是一个 pytest fixture，作用域为测试函数级别（方法级别）。
def driver(request):
    options = webdriver.ChromeOptions()  # 定义一个 ChromeOptions 对象，可以用来设置启动 Chrome 浏览器的一些参数。
    options.add_argument('--headless')  # 开启无界面模式（无窗口运行）
    #options.add_argument('--blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    # 禁用沙箱
    options.add_argument("--no-sandbox")
    #options.add_argument("--disable-dev-shm-usage")
    # 设置浏览器窗口大小为1366x768,服务器必须设置，否则会报错
    options.add_argument('--window-size=3840,2160')
    #options.add_argument("--start-maximized")
    # 去掉不安全提示short
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    driver = webdriver.Chrome(options=options)  # 启动 Chrome 浏览器，并传入上面定义好的 ChromeOptions 对象。
    driver.get(f"{url}")
    driver.implicitly_wait(8)
    time.sleep(2)
    try:
        driver.find_element(By.XPATH,'//*[@id="__nuxt"]/div/div/header/div/div[3]/div/div/span[1]').click()
        input_email = driver.find_element(By.ID, "form_item_email")
        input_email.clear()
        input_email.send_keys('jingwenshuo@quantaspaces.com')
        input_pwd = driver.find_element(By.ID, "form_item_password")
        input_pwd.clear()
        input_pwd.send_keys('jing.1751')
        time.sleep(2)
        driver.find_element(By.CLASS_NAME,'ant-btn.w-full.h-9.submit-buttom-bg').click()
        time.sleep(1)
        request.addfinalizer(driver.quit)  # 将 WebDriver 对象的 quit() 方法注册为测试结束后的清理函数，以确保测试用例结束后关闭浏览器进程。
    except Exception as e:
        print('driver函数报错:',e)
    return driver  # 将 WebDriver 对象返回，供测试函数使用。

# 配置日志记录 其中%(asctime)s表示日志记录的时间，%(levelname)s表示日志级别，%(message)s表示日志消息内容。
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class WebAutomation:
    def __init__(self, driver):
        self.driver = driver
    def selenium_click(self, by_type, element, index=None):
        if index is None:
            next_btn = self.driver.find_element(by_type, element)
            self.driver.execute_script("arguments[0].click();", next_btn)
        else:
            next_btns = self.driver.find_elements(by_type, element)
            if 0 <= int(index) < len(next_btns):
                next_btn = next_btns[int(index)]
                self.driver.execute_script("arguments[0].click();", next_btn)
            else:
                print(f"selenium_click Error: Index {index} is out of bounds.")

    # 输入
    def selenium_send(self, types, element, text, index=None):
        if index is None:
            next_btn = self.driver.find_element(types, element)
            self.driver.execute_script("arguments[0].value = arguments[1]", next_btn, text)
        else:
            next_btn = self.driver.find_elements(types, element)[index]
            self.driver.execute_script("arguments[0].value = arguments[1]", next_btn, text)

    # 悬停
    def hover(self, types, element, index=None):
        if index is None:
            but = self.driver.find_element(types, element)
            ActionChains(self.driver).move_to_element(but).perform()
        else:
            but = self.driver.find_elements(types, element)[index]
            ActionChains(self.driver).move_to_element(but).perform()

    # 判断元素是否存在
    def check_element_presence(self, types, element, index=None):
        if index is None:
            try:
                self.driver.find_element(types, element)
                return True
            except NoSuchElementException:
                return False
        else:
            try:
                but = self.driver.find_elements(types, element)[index]
                return True
            except (NoSuchElementException, IndexError):
                return False

    # 获取文本内容
    def text_content(self, types, element, index=None):
        if index is None:
            info = self.driver.find_element(types, element).text
            return info
        else:
            info = self.driver.find_elements(types, element)[index].text
            return info

    # 切入ifram框，一般情况
    def cut_in_ifram(self, types, element, index=None):
        if index is None:
            self.driver.switch_to.frame(self.driver.find_element(types, element))
        else:
            self.driver.switch_to.frame(self.driver.find_elements(types, element)[int(index)])

    # 切入ifram框，特殊情况
    def cut_in_ifram_not_unique(self, types, element, index=None):
        if index is None:
            parent_element = self.driver.find_element(types, element)
        else:
            parent_element = self.driver.find_element(types, element)[int(index)]
        self.driver.switch_to.frame(parent_element.find_element(By.TAG_NAME, 'iframe'))

    # 切出ifram
    def cut_out_ifram(self):
        self.driver.switch_to.default_content()

    # 下拉选项框
    def select(self, types, element, index, class_index=None):
        if class_index is None:
            Select(self.driver.find_element(types, element)).select_by_index(int(index))
        else:
            Select(self.driver.find_elements(types, element)[int(class_index)]).select_by_index(int(index))

    # 显示等待
    def wait(self, types, element):
        WebDriverWait(self.driver, 20).until(EC.presence_of_all_elements_located((types, element)))

    # 切换窗口
    def switch_windows(self, index):
        self.driver.switch_to.window(self.driver.window_handles[int(index)])

    # 打开第二个网页
    def opens_new_tab(self, url, index):
        self.driver.execute_script(f"window.open('{url}');")
        self.driver.switch_to.window(self.driver.window_handles[int(index)])

    # 界面上下滑动
    def up_down_slide(self, bili):
        # bili为0表示滑动到页面最上方，1为最下方，0.65为页面从上到下的65%处,范围在0-1
        self.driver.execute_script(f"window.scrollTo(0, document.body.scrollHeight * {bili});")  # 滑动到屏幕57%处

    # 元素滑动
    def element_slide(self, types, element, zuoyou, sahngxia, index=None):
        if index is None:
            # 获取要操作的元素
            ele = self.driver.find_element(types, element)
            # 创建一个ActionChains对象
            '''
                    上滑移动50个像素 move_by_offset( 0,-50)
                    下滑移动50个像素 move_by_offset( 0, 50)
                    左滑移动50个像素 move_by_offset(-50, 0)
                    右滑移动50个像素 move_by_offset( 50, 0)
            '''
            ActionChains(self.driver).move_to_element(ele).move_by_offset(zuoyou, sahngxia).perform()
        else:
            ele = self.driver.find_elements(types, element)[int(index)]
            ActionChains(self.driver).move_to_element(ele).move_by_offset(zuoyou, sahngxia).perform()






