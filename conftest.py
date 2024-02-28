# encoding=utf-8
import pytest, time, logging, os, threading ,json
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


url = 'http://spider.aikonchem.com:48888/'
db = MySQLHelper_cookies()

@pytest.fixture(scope='function')  # 表示这是一个 pytest fixture，作用域为测试函数级别（方法级别）。
def driver(request):
    identity_marker = request.node.get_closest_marker("identity") #获取与测试函数相标记为identity
    if identity_marker is not None:
        username = identity_marker.args[0] # 返回这个元组中的第一个参数，即user2
        cookie_data = db.execute_query(f"SELECT session, token FROM cookies WHERE username = '{username}'")
    else:
        # 如果没有标记，默认使用 'user1' 身份
        cookie_data = db.execute_query("select session,token from cookies where username = 'user1'")

    options = webdriver.ChromeOptions()  # 定义一个 ChromeOptions 对象，可以用来设置启动 Chrome 浏览器的一些参数。
    #options.add_argument('--headless')  # 开启无界面模式（无窗口运行）
    #options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
    # 去掉不安全提示short
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument("--start-maximized")
    #options.add_argument('--window-size=3840,2160')
    driver = webdriver.Chrome(options=options)  # 启动 Chrome 浏览器，并传入上面定义好的 ChromeOptions 对象。
    driver.get(f"{url}")
    driver.implicitly_wait(8)
    cookies = [
        {'name': 'qs_session', 'path': '/', 'value': cookie_data[0]['session']},
        {'name': 'XSRF-TOKEN', 'path': '/', 'value': cookie_data[0]['token']}
    ]
    for i in cookies:
        driver.add_cookie(i)
    driver.refresh()

    request.addfinalizer(driver.quit)  # 将 WebDriver 对象的 quit() 方法注册为测试结束后的清理函数，以确保测试用例结束后关闭浏览器进程。
    return driver  # 将 WebDriver 对象返回，供测试函数使用。



# 配置日志记录 其中%(asctime)s表示日志记录的时间，%(levelname)s表示日志级别，%(message)s表示日志消息内容。
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@pytest.mark.hookwrapper
def pytest_runtest_makereport(item):
    """
    测试失败时获取 WebDriver 对象并在 HTML 报告中嵌入截图。
    """
    # 获取pytest-html插件
    pytest_html = item.config.pluginmanager.getplugin('html')
    # 暂停当前函数的执行，等待测试用例执行完毕后再继续执行 目的：检查测试用例是否通过
    outcome = yield
    # 获取测试用例的执行结果
    report = outcome.get_result()
    # 检查测试报告对象中是否有一个名为 'extra' 的属性，如果有额外则获取其值，如果没有则将其设置为一个空列表 目的：为了确保在没有额外信息的情况下不会出现错误
    extra = getattr(report, 'extra', [])
    # 如果是测试函数的执行阶段（'call'）或者测试用例的准备阶段（'setup'），则执行后续操作
    if report.when == 'call' or report.when == "setup":
        # 检查测试用例是否标记为预期失败
        xfail = hasattr(report, 'wasxfail')
        # 判断执行结果（跳过、失败）以及是否标记为预期失败来决定是否执行后续操作
        if (report.skipped and xfail) or (report.failed and not xfail):
            driver = item.funcargs['driver']  # 获取 driver 对象
            try:
                # 截图
                screenshot = driver.get_screenshot_as_png()
                # 转码base64
                encode_str = base64.b64encode(screenshot)
                encoded_image = str(encode_str, 'utf-8')

                # 将 base64 编码的图片嵌入到 HTML 报告中
                html = f'''
                <div>
                    <img src="data:image/png;base64,{encoded_image}" id="screenshot_img" alt="screenshot" 
                         style="width:304px;height:228px;cursor:pointer;" 
                         onclick="openBase64()" align="right"/>
                </div>
                <script>
                    function openBase64() {{
                        const img = document.getElementById('screenshot_img');
                        const win = window.open('', '_blank');
                        win.document.write('<img src="' + img.src + '" style="width:100%; height:auto;">');
                    }}
                </script>
                '''
                extra.append(pytest_html.extras.html(html))
            except NoSuchElementException as e:
                logging.info("截图失败 无搜索元素异常：%s", e)
            except Exception as e:
                logging.info("截图失败：%s", e)

        report.extra = extra



            
class WebAutomation:
    def __init__(self, driver):
        self.driver = driver

    # 点击，class有多层，示例：.btn_add.mouse
    def selenium_click(self, types, element, index=None):
        if index is None:
            next_btn = self.driver.find_element(types, element)
            self.driver.execute_script("arguments[0].click();", next_btn)
        else:
            next_btn = self.driver.find_elements(types, element)[int(index)]
            self.driver.execute_script("arguments[0].click();", next_btn)

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
            parent_element = self.driver.find_elements(types, element)[int(index)]
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


