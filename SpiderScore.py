#!/usr/bin/python
# -*- coding: utf-8 -*-

import getpass
import re
import time
import tkinter
from tkinter import ttk

import execjs
import requests


class SpiderScore(object):
    def __init__(self):
        self.__cookies = None
        self.__data = []
        self.__len = 0

    def __init_cookies(self, user, pwd):
        # 通过《智慧华中大——统一身份认证系统》的核心代码
        # 目的是通过登陆，获取 JSESSIONID 值，后续利用该 cookies 访问《研究生教育管理信息系统》
        print("exe __init_cookies")

        login_url = 'https://pass.hust.edu.cn/cas/login?service=http://yjs.hust.edu.cn/ssfw/login_cas.jsp'
        page1 = requests.get(login_url)
        cookies = page1.cookies
        
        with open('rsa.js', 'r') as j:
            rsa_js = execjs.compile(j.read())
        
        UserPwd = rsa_js.call('getUserPwd', user, pwd)

        data = {
            "username": UserPwd[0],
            "password": UserPwd[1],
            "code": "code",
            "lt": "LT-NeusoftAlwaysValidTicket",
            "execution": "e1s1",
            "_eventId": "submit"
        }
        page2 = requests.post(login_url, data=data, cookies=cookies, allow_redirects=False)

        ticket_url = page2.headers['Location']
        page3 = requests.get(ticket_url, allow_redirects=False)
        self.__cookies = page3.cookies

    def __spider(self):
        print("exe __spider")
        
        if self.__cookies is None:
            self.__init_cookies(input('username:'), getpass.getpass('password:'))

        url = "http://yjs.hust.edu.cn/ssfw/pygl/cjgl/cjcx.do"
        page = requests.get(url, cookies=self.__cookies)
        data_re = r'<td style=.+?>(.+?)</td>\s+?<td>(.+?)</td>\s+?<td>(.+?)</td>\s+?<td>(.+?)</td>'
        re_results = re.findall(data_re, page.text)
        print("考试成绩\t学分\t课程")
        avg = 0
        sum_score = 0
        self.__data = []
        for re_result in re_results:
            data = []
            data.append(re_result[0])
            data.append(re_result[1])
            data.append(re_result[3])
            print("%s\t\t%s\t%s" % (data[2], data[1], data[0]))
            self.__data.append(data)
            sum_score += float(data[1])
            avg += float(data[1]) * int(data[2])
        avg /= sum_score
        self.__data.append(["加权", sum_score, avg])
        print("加权\t\t%.1f\t%.2f" % (sum_score, avg))
        if (self.__len):
            if (self.__len != len(self.__data)):
                return True
        else:
            self.__len = len(self.__data)
        return False
        
    def __remind(self):
        print("exe __remind")
        main_window = tkinter.Tk()
        main_window.title("成绩提醒")
        main_window.geometry("400x220")
        main_window.resizable(False, False)

        tree = ttk.Treeview(main_window, columns=[
                            "课程", "学分", "考试成绩"], show='headings')
        tree.column("课程", width=250)
        tree.column("学分", width=50)
        tree.column("考试成绩", width=100)

        tree.heading("课程", text="课程")
        tree.heading("学分", text="学分")
        tree.heading("考试成绩", text="考试成绩")

        for i in range(len(self.__data)):
            tree.insert("", i, values=self.__data[i])

        tree.grid()
        main_window.mainloop()

    def run(self):
        while True:
            if(self.__spider()):
                self.__remind()
                break
            print("exe sleep")
            time.sleep(300)
            print(time.ctime())


if __name__ == "__main__":
    SpiderScore().run()
