from selenium.webdriver.remote.webdriver import WebDriver as wd
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wdw
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains as AC
import selenium
from bs4 import BeautifulSoup as BS
import json
import time
import collections


class WebVPN:
    def __init__(self, opt: dict, headless=False):
        self.root_handle = None
        self.driver: wd = None
        self.userid = opt["username"]
        self.passwd = opt["password"]
        self.headless = headless

    def login_webvpn(self):
        """
        Log in to WebVPN with the account specified in `self.userid` and `self.passwd`

        :return:
        """
        d = self.driver
        if d is not None:
            d.close()
        d = selenium.webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()))
        d.get("https://webvpn.tsinghua.edu.cn/login")
        username = d.find_elements(By.XPATH,
                                   '//div[@class="login-form-item"]//input'
                                   )[0]
        password = d.find_elements(By.XPATH,
                                   '//div[@class="login-form-item password-field" and not(@id="captcha-wrap")]//input'
                                   )[0]
        username.send_keys(str(self.userid))
        password.send_keys(self.passwd)
        d.find_element(By.ID, "login").click()
        self.root_handle = d.current_window_handle
        self.driver = d
        return d

    def access(self, url_input):
        """
        Jump to the target URL in WebVPN

        :param url_input: target URL
        :return:
        """
        d = self.driver
        url = By.ID, "quick-access-input"
        btn = By.ID, "go"
        wdw(d, 5).until(EC.visibility_of_element_located(url))
        actions = AC(d)
        actions.move_to_element(d.find_element(*url))
        actions.click()
        actions.\
            key_down(Keys.CONTROL).\
            send_keys("A").\
            key_up(Keys.CONTROL).\
            send_keys(Keys.DELETE).\
            perform()

        d.find_element(*url)
        d.find_element(*url).send_keys(url_input)
        d.find_element(*url).send_keys(Keys.ENTER)
        time.sleep(1)
        # d.find_element(*btn).click()

    def switch_another(self):
        """
        If there are only 2 windows handles, switch to the other one

        :return:
        """
        d = self.driver
        assert len(d.window_handles) == 2
        wdw(d, 5).until(EC.number_of_windows_to_be(2))
        for window_handle in d.window_handles:
            if window_handle != d.current_window_handle:
                d.switch_to.window(window_handle)
                return

    def to_root(self):
        """
        Switch to the home page of WebVPN

        :return:
        """
        self.driver.switch_to.window(self.root_handle)

    def close_all(self):
        """
        Close all window handles

        :return:
        """
        while True:
            try:
                l = len(self.driver.window_handles)
                if l == 0:
                    break
            except selenium.common.exceptions.InvalidSessionIdException:
                return
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.driver.close()

    def login_info(self):
        """
        TODO: After successfully logged into WebVPN, login to info.tsinghua.edu.cn

        :return:
        """
        self.access("info.tsinghua.edu.cn")
        self.switch_another()
        d = self.driver

        password = d.find_elements(By.XPATH,
                                   '//td[@class="srk"]//input'
                                   )[1]
        username = d.find_elements(By.XPATH,
                                   '//td[@class="srk"]//input'
                                   )[0]
        username.send_keys(str(self.userid))
        password.send_keys(self.passwd)
        d.find_element(By.XPATH, '//td[@class="but"]//input').click()
        return d
        # Hint: - Use `access` method to jump to info.tsinghua.edu.cn
        #       - Use `switch_another` method to change the window handle
        #       - Wait until the elements are ready, then preform your actions
        #       - Before return, make sure that you have logged in successfully
        #raise NotImplementedError

    def get_grades(self):
        """
        TODO: Get and calculate the GPA for each semester.

        Example return / print:
            2020-秋: *.**
            2021-春: *.**
            2021-夏: *.**
            2021-秋: *.**
            2022-春: *.**

        :return:
        """
        ans = collections.OrderedDict()
        d = self.driver
        self.switch_another()
        time.sleep(0.5)
        self.access(
            "zhjw.cic.tsinghua.edu.cn/cj.cjCjbAll.do?m=bks_cjdcx&cjdlx=zw")
        self.access(
            "zhjw.cic.tsinghua.edu.cn/cj.cjCjbAll.do?m=bks_cjdcx&cjdlx=zw")
        # It is quite strange that only by repeat the line above twice can I get the gpa data
        pass
        # print(len(d.window_handles))

        self.driver.switch_to.window(self.driver.window_handles[2])
        #
        table = d.find_elements(By.XPATH, '//table[@id="table1"]//tbody//tr')
        # print(len(table))
        for a in table:
            items_in_line = []
            html_of_the_item = a.get_attribute("innerHTML")
            soup_of_the_item = BS(html_of_the_item, 'lxml')
            # print(html_of_the_item)
            items = soup_of_the_item.find_all("td")
            for b in items:
                items_in_line.append(b.get_text().replace(" ", '').replace(
                    "\n", '').replace("\r", '').replace("\t", ''))
            pass
            if len(items_in_line) > 0 and items_in_line[-2][0] != 'N':
                if(not ans.__contains__(items_in_line[-1])):
                    ans[items_in_line[-1]] = [0, 0]
                ans[items_in_line[-1]][0] += int(items_in_line[2])
                ans[items_in_line[-1]
                    ][1] += int(items_in_line[2]) * float(items_in_line[-2])

        for a in ans:
            gpa = 0.01*(((ans[a][1]/ans[a][0])*100+0.5)//1)
            print(a + ':', gpa)

        # table = d.find_elements(By.XPATH,'//html')
        # print(len(table))
        # pass
        # print(table[0].get_attribute("innerHTML"))
if __name__ == "__main__":
    # TODO: Write your own query process
    with open("settings.json", "r", encoding="utf8") as f:
        opt = json.load(f)  # Load settings
    mywebvpn = WebVPN(opt)
    mywebvpn.login_webvpn()
    mywebvpn.login_info()
    mywebvpn.get_grades()
    #raise NotImplementedError
