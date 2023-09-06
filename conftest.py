#encoding=utf-8
import pytest
from selenium import webdriver

@pytest.fixture(scope='function')#表示这是一个 pytest fixture，作用域为测试函数级别（方法级别）。
def driver(request):
    options = webdriver.ChromeOptions()#定义一个 ChromeOptions 对象，可以用来设置启动 Chrome 浏览器的一些参数。
    options.add_argument('--headless')  # 开启无界面模式（无窗口运行）
    options.add_argument("--start-maximized")#将启动参数 "--start-maximized" 添加到 ChromeOptions 中，表示启动浏览器时最大化窗口。
    driver = webdriver.Chrome(options=options)#启动 Chrome 浏览器，并传入上面定义好的 ChromeOptions 对象。
    driver.implicitly_wait(10)
    request.addfinalizer(driver.quit) #将 WebDriver 对象的 quit() 方法注册为测试结束后的清理函数，以确保测试用例结束后关闭浏览器进程。
    return driver #将 WebDriver 对象返回，供测试函数使用。