#coding=utf-8

from selenium import webdriver
import time
import os
import progressbar
from dannyTumblr.DataBase import Mysql_data

class Log:

    def __init__(self):
        self.mysqldata = Mysql_data()

    def Login_progressbar(self,sec):
        bar = progressbar.ProgressBar(max_value=sec, widgets=['►►',progressbar.Bar(marker='■',left='[',right=']'),progressbar.CurrentTime()]).start()
        for i in range(sec+1):
            time.sleep(1)
            bar.update(i)

    def User_information(self):
        self.path= os.getcwd()
        os.chdir(self.path + '/' + 'dannyTumblr')
        with open('Calibration_Info.txt')as f:
            yy= f.readline().split(',')
            f.close()
        self.email = yy[0]
        self.password = yy[1]
        os.chdir(self.path)
        return self.email

    def Login(self):
        self.User_information()
        # 產生虛擬 borwser：
        path = os.getcwd()
        os.chdir(path + '/' + 'dannyTumblr')
        service_args=[]
        service_args.append('--load-images=no')  # 關閉圖片加載
        service_args.append('--disk-cache=yes')  # 開啟緩存
        service_args.append('--ignore-ssl-errors=true') # 忽略https錯誤
        driver = webdriver.PhantomJS(executable_path='/usr/local/Cellar/phantomjs/2.1.1/bin/phantomjs',service_args=service_args)

        # Login:
        print('[使用者登錄中]')
        login_url = 'https://www.tumblr.com/login'
        driver.get(login_url)

        # 輸入 email:
        # email = 'bobobo746@hotmail.com'
        driver.find_element_by_name("determine_email").clear()
        driver.find_element_by_name("determine_email").send_keys(self.email)
        log_in = driver.find_element_by_xpath('//button[span/@class="signup_determine_btn active" ]')
        log_in.click()

        #time.sleep(5)   # click 結束後要給點時間做登陸模擬
        self.Login_progressbar(5)

        # 輸入密碼：
        driver.find_element_by_xpath('//input[@id="signup_password" ]').clear()
        driver.find_element_by_xpath('//input[@id="signup_password" ]').send_keys(self.password)
        log_in = driver.find_element_by_xpath('//button[span/@class="signup_login_btn active" ]')
        log_in.click()

        #time.sleep(5)   # click 結束後要給點時間做登陸模擬
        self.Login_progressbar(5)


        driver.save_screenshot("登錄頁面.png")
        print(' [登錄成功]')
        os.chdir(self.path)
        self.mysqldata.Login_ID(self.User_information())
        # os.chdir(path + '/' + 'dannyTumblr')
        return driver
