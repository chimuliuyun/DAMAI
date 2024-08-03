# coding: utf-8
from json import loads
from os.path import exists
from pickle import dump, load
from time import sleep, time
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class Concert(object):
    def __init__(self, date, session, price, real_name, nick_name, ticket_num, viewer_person, damai_url, target_url,
                 driver_path):
        self.date = date  # 日期序号
        self.session = session  # 场次序号优先级
        self.price = price  # 票价序号优先级
        self.real_name = real_name  # 实名者序号
        self.status = 0  # 状态标记
        self.time_start = 0  # 开始时间
        self.time_end = 0  # 结束时间
        self.num = 0  # 尝试次数
        self.ticket_num = ticket_num  # 购买票数
        self.viewer_person = viewer_person  # 观影人序号优先级
        self.nick_name = nick_name  # 用户昵称
        self.damai_url = damai_url  # 大麦网官网网址
        self.target_url = target_url  # 目标购票网址
        self.driver_path = driver_path  # 浏览器驱动地址
        self.driver = None

    def isClassPresent(self, item, name, ret=False):
        try:
            result = item.find_element(by=By.CLASS_NAME, value=name)
            if ret:
                return result
            else:
                return True
        except:
            return False

    # 获取账号的cookie信息
    def get_cookie(self):
        self.driver.get(self.damai_url)
        print("###请点击登录###")
        self.driver.find_element(by=By.CLASS_NAME, value='login-user').click()
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台') != -1:  # 等待网页加载完成
            sleep(1)
        print("###请扫码登录###")
        while self.driver.title == '大麦登录':  # 等待扫码完成
            sleep(1)
        dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
        print("###Cookie保存成功###")

    def set_cookie(self):
        try:
            cookies = load(open("cookies.pkl", "rb"))  # 载入cookie
            for cookie in cookies:
                cookie_dict = {
                    'domain': '.damai.cn',  # 必须有，不然就是假登录
                    'name': cookie.get('name'),
                    'value': cookie.get('value'),
                    "expires": "",
                    'path': '/',
                    'httpOnly': False,
                    'HostOnly': False,
                    'Secure': False}
                self.driver.add_cookie(cookie_dict)
            print("###载入Cookie###")
        except Exception as e:
            print(e)

    def login(self):
        print("###开始登录###")
        self.driver.get(self.target_url)
        WebDriverWait(self.driver, 10, 0.1).until(EC.title_contains('商品详情'))
        self.set_cookie()

    def enter_concert(self):
        print("###打开浏览器，进入大麦网###")
        if not exists('cookies.pkl'):  # 如果不存在cookie.pkl,就获取一下
            service = Service(self.driver_path)
            self.driver = webdriver.Chrome(service=service)
            self.get_cookie()
            print("###成功获取Cookie，重启浏览器###")
            self.driver.quit()

        options = webdriver.ChromeOptions()
        # 禁止图片、js、css加载
        prefs = {"profile.managed_default_content_settings.images": 2,
                 "profile.managed_default_content_settings.javascript": 1,
                 'permissions.default.stylesheet': 2}
        mobile_emulation = {"deviceName": "Nexus 6"}
        options.add_experimental_option("prefs", prefs)
        options.add_experimental_option("mobileEmulation", mobile_emulation)
        # chrome去掉了webdriver痕迹，令navigator.webdriver=false
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument('--log-level=3')
        service = Service(self.driver_path)
        self.driver = webdriver.Chrome(service=service, options=options)
        # 登录到具体抢购页面
        self.login()
        self.driver.refresh()

    def click_util(self, button, locator):
        while True:
            button.click()
            try:
                return WebDriverWait(self.driver, 1, 0.1).until(EC.presence_of_element_located(locator))
            except:
                continue

    # 实现购买函数

    def choose_ticket(self):
        print("###进入抢票界面###")
        # 如果跳转到了确认界面就算这步成功了，否则继续执行此步
        while self.driver.title.find('订单确认') == -1:
            self.num += 1  # 尝试次数加1

            if self.driver.current_url.find("buy.damai.cn") != -1:
                break

            # 判断页面加载情况 确保页面加载完成
            try:
                WebDriverWait(self.driver, 10, 0.1).until(
                    lambda driver: driver.execute_script('return document.readyState') == 'complete'
                )
            except:
                raise Exception(u"***Error: 页面加载超时***")

            # 判断root元素是否存在
            try:
                box = WebDriverWait(self.driver, 1, 0.1).until(
                    EC.presence_of_element_located((By.ID, 'root'))
                )
            except:
                raise Exception(u"***Error: 页面中ID为root的整体布局元素不存在或加载超时***")

            try:
                buybutton = box.find_element(by=By.CSS_SELECTOR, value='.buy-button')
                buybutton_text = buybutton.text
            except Exception as e:
                try:
                    buybutton = box.find_element(by=By.CSS_SELECTOR, value='.buy__button')
                    buybutton_text = buybutton.text
                except Exception as e:
                    raise Exception(f"***Error: 定位购买按钮失败***: {e}")

            if "即将开抢" in buybutton_text:
                self.status = 2
                raise Exception("---尚未开售，刷新等待---")

            if "缺货" in buybutton_text:
                raise Exception("---已经缺货，刷新等待---")

            sleep(0.1)
            # 点击购买按钮
            buybutton.click()
            print("###点击购买按钮###")

            sleep(0.1)
            # 等待弹出框出现
            box = WebDriverWait(self.driver, 1, 0.1).until(
                # EC.presence_of_element_located((By.LINK_TEXT, '立即购买')))
                EC.presence_of_element_located((By.CSS_SELECTOR, '.sku-pop-wrapper')))

            try:
                # 选择日期
                toBeClicks = []
                try:
                    date = WebDriverWait(self.driver, 1, 0.1).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'bui-dm-sku-calendar')))
                except Exception as e:
                    date = None
                if date is not None:
                    date_list = date.find_elements(
                        by=By.CLASS_NAME, value='bui-calendar-day-box')
                    for i in self.date:
                        j = date_list[i - 1]
                        toBeClicks.append(j)
                        break
                    for i in toBeClicks:
                        i.click()
                        sleep(0.05)

                # 选择场次
                session = WebDriverWait(self.driver, 1, 0.1).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'sku-times-card')))  # 日期、场次和票档进行定位
                session_list = session.find_elements(
                    by=By.CLASS_NAME, value='bui-dm-sku-card-item')

                toBeClicks = []
                for i in self.session:  # 根据优先级选择一个可行场次
                    if i > len(session_list):
                        i = len(session_list)
                    j = session_list[i - 1]            

                    k = self.isClassPresent(j, 'item-tag', True)
                    if k:  # 如果找到了带presell的类
                        if k.text == '无票':
                            continue
                        elif k.text == '预售':
                            toBeClicks.append(j)
                            break
                        elif k.text == '惠':
                            toBeClicks.append(j)
                            break
                    else:
                        toBeClicks.append(j)
                        break

                # 多场次的场要先选择场次才会出现票档
                for i in toBeClicks:
                    i.click()
                    sleep(0.05)

                # 选定票档
                toBeClicks = []
                price = WebDriverWait(self.driver, 1, 0.1).until(
                    EC.presence_of_element_located((By.CLASS_NAME, 'sku-tickets-card')))  # 日期、场次和票档进行定位

                price_list = price.find_elements(
                    by=By.CLASS_NAME, value='bui-dm-sku-card-item')  # 选定票档
                for i in self.price:
                    if i > len(price_list):
                        i = len(price_list)
                    j = price_list[i - 1]

                    k = self.isClassPresent(j, 'item-tag', True)
                    if k:  # 存在notticket代表存在缺货登记，跳过
                        continue
                    else:
                        toBeClicks.append(j)
                        break

                for i in toBeClicks:
                    i.click()
                    sleep(0.1)

                buybutton = box.find_element(
                    by=By.CLASS_NAME, value='sku-footer-buy-button')
                # sleep(1.0)
                buybutton_text = buybutton.text
                if buybutton_text == "":
                    raise Exception(u"***Error: 提交票档按钮文字获取为空,适当调整 sleep 时间***")

                try:
                    WebDriverWait(self.driver, 1, 0.1).until(
                        EC.presence_of_element_located((By.CLASS_NAME, 'bui-dm-sku-counter')))
                except:
                    raise Exception(u"***购票按钮未开始***")

            except Exception as e:
                raise Exception(f"***Error: 选择日期or场次or票档不成功***: {e}")

            try:
                ticket_num_up = box.find_element(
                    by=By.CLASS_NAME, value='plus-enable')
            except:
                if buybutton_text == "选座购买":  # 选座购买没有增减票数键
                    buybutton.click()
                    self.status = 5
                    print("###请自行选择位置和票价###")
                    break
                elif buybutton_text == "提交缺货登记":
                    raise Exception(u'###票已被抢完，持续捡漏中...或请关闭程序并手动提交缺货登记###')
                else:
                    raise Exception(u"***Error: ticket_num_up 位置找不到***")

            if buybutton_text == "立即预订" or buybutton_text == "立即购买" or buybutton_text == '确定':
                for i in range(self.ticket_num - 1):  # 设置增加票数
                    ticket_num_up.click()
                buybutton.click()
                self.status = 4
                WebDriverWait(self.driver, 2, 0.1).until(
                    EC.title_contains("确认"))
                break
            else:
                raise Exception(f"未定义按钮：{buybutton_text}")

    def check_order(self, retry=False):
        if self.status in [3, 4, 5]:
            time_to_wait = 0.5 # 如果是重试的话，不需要等待太久
            if not retry: # 重试的时候不需要再次选择
                time_to_wait = 5 # 如果不是重试的话，等待时间长一点
                # 选择观影人
                toBeClicks = []
                WebDriverWait(self.driver, time_to_wait, 0.1).until(
                    EC.presence_of_element_located((By.XPATH, '//*[@id="dmViewerBlock_DmViewerBlock"]/div[2]/div/div')))
                people = self.driver.find_elements(
                    By.XPATH, '//*[@id="dmViewerBlock_DmViewerBlock"]/div[2]/div/div')
                sleep(0.2)

                for i in self.viewer_person:
                    if i > len(people):
                        break
                    j = people[i - 1]
                    j.click()
                    sleep(0.05)

            WebDriverWait(self.driver, time_to_wait, 0.1).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="dmOrderSubmitBlock_DmOrderSubmitBlock"]/div[2]/div/div[2]/div[2]/div[2]')))
            comfirmBtn = self.driver.find_element(
                By.XPATH, '//*[@id="dmOrderSubmitBlock_DmOrderSubmitBlock"]/div[2]/div/div[2]/div[2]/div[2]')
            sleep(0.5)
            comfirmBtn.click()
            # 判断title是不是支付宝
            print("###正在跳转到支付宝付款界面###")

            while True:
                try:
                    WebDriverWait(self.driver, 10, 0.1).until(
                        EC.title_contains('支付宝'))
                    print("###订单提交成功###")
                    self.status = 6
                    break
                except Exception as e:
                    print(f"***Error: 跳转支付宝报错***: {e}")
                    print("尝试重新抢票")
                    return True

if __name__ == '__main__':
    try:
        with open('./config.json', 'r', encoding='utf-8') as f:
            config = loads(f.read())
            # params: 场次优先级，票价优先级，实名者序号, 用户昵称， 购买票数， 官网网址， 目标网址, 浏览器驱动地址
        con = Concert(config['date'], config['sess'], config['price'], config['real_name'], config['nick_name'],
                      config['ticket_num'], config['viewer_person'], config['damai_url'], config['target_url'],
                      config['driver_path'])
        con.enter_concert()  # 进入到具体抢购页面
    except Exception as e:
        print(e)
        exit(1)

    retry_times = 0

    while True:
        try:
            if retry_times > 50: # 重试次数超过50次重新刷新页面，否则大麦会提示“在此页面停留时间过长”错误
                retry_times = 0
                con.enter_concert()
            con.choose_ticket()
            retry = con.check_order(retry_times > 0)
            if not retry:
                break
            retry_times += 1
        except Exception as e:
            con.driver.get(con.target_url)
            print(e)
            continue

    if con.status == 6:
        input("按 Enter 键退出脚本")