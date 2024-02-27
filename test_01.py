# encoding=utf-8
import time
from selenium.webdriver.common.by import By
from conftest import WebAutomation,url
from selenium.webdriver.common.keys import Keys


# 登录
class TestUi:

    # 搜索
    def test_04(self,driver):
        click_instance = WebAutomation(driver)
        driver.get(f"{url}")
        driver.find_elements(By.CLASS_NAME, 'ant-input')[0].send_keys('Nortriptyline hydrochloride')
        click_instance.selenium_click(By.XPATH, '//*[@id="__nuxt"]/div/div/div/div/div/span/span/img')
        assert click_instance.text_content(By.XPATH,'//*[@id="__nuxt"]/div/div/div[2]/div[2]/div[1]/div/div/div/div/div/table/tbody/tr[2]/td[4]/span') == '894-71-3'
        driver.find_elements(By.CLASS_NAME, 'ant-input')[0].send_keys('894-71-3')
        click_instance.selenium_click(By.XPATH, '//*[@id="__nuxt"]/div/div/header/div[1]/div[1]/div[2]/span/span/img')
        assert click_instance.text_content(By.XPATH,'//*[@id="__nuxt"]/div/div/div[2]/div[2]/div[1]/div/div/div/div/div/table/tbody/tr[2]/td[4]/span') == '894-71-3'






