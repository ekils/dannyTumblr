#coding=utf-8

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import datetime
import matplotlib.dates as md
import pymysql as mysql
import os



# plot函數返回一個線的list，比如 line1,line2 = plot(x1,y1,x2,y2)。
# 由於我们只有一條直線，對於長度為1的 list，我们可以用逗號,來得到列表第一個元素

class DataPlot:

# Animation要呼叫用的：

    def __init__(self):
        self.path = os.getcwd()
        os.chdir(self.path + '/' + 'dannyTumblr')
        with open('Calibration_Info.txt')as f:
            yy = (f.readline().split(','))
            f.close()
        self.id = yy[0]

        os.chdir(self.path + '/' + 'dannyTumblr' + '/' + 'data_folder')
        self.db = mysql.connect(host='localhost', user='root', passwd="0000", db='DannyDataBase')
        self.cursor = self.db.cursor()
        os.chdir(self.path)

    def Update_line(self,num, data, line):
        line.set_data(data[..., :num])  # array[...,:num] :第一維全取，第二維依照num數字取到第num排
        return line,

    def LoginPlot(self):
    # x,y 值設定且轉成array 放在data:

     # x:去資料庫抓data:
        self.cursor.execute("SELECT Date FROM LOG_IN_ID WHERE Email='{}' ".format(self.id))
        bobo_sure = self.cursor.fetchall()
        usermail = [i[0] for i in bobo_sure]
        x= []
        for i in usermail:
            year= i[0:4]
            month= i[5:7]
            day= i[-2:]
            dt = datetime.datetime(int(year), int(month),int(day))
            x.append(md.date2num(dt))
        # print(x)
     # y:去資料庫抓data:
        self.cursor.execute("SELECT Count_times FROM LOG_IN_ID WHERE Email='{}' ".format(self.id))
        count_sure = self.cursor.fetchall()
        y = [i[0] for i in count_sure]
        # print(y)
        data = np.array([x,y])
        print(data)
    # 建造圖框：
        fig1 = plt.figure()
    # 先畫一個空圖框,之後animation呼叫到line時[]可以擴充
        line, = plt.plot_date([], [], linestyle='-', marker='o', color='g',alpha= 0.6,lw= 2)
    # 數字轉日期:
        fig1.autofmt_xdate()
    # 設定範圍
        plt.ylim(-1, max(y)+10)
        plt.xlim(min(x), max(x))
    # Label:
        plt.xlabel('Date')
        plt.ylabel('Times')
        plt.title('Login Data')
    # 插入動畫： fargs=(data, line) 傳入呼叫func要用的的參數 , len(y): 要呼叫的num次數
        line_ani = animation.FuncAnimation(fig1, self.Update_line, len(y)+1, fargs=(data, line),interval=50, blit=True,repeat= False)
        plt.fill_between(x, 0, y, color='g', alpha=0.1)
        plt.grid()
        plt.show()



    def Month_PerDaily_Stream(self):
        self.cursor.execute("SELECT Years,Months FROM DOWNLOAD_INFO ")
    # 統計年份,月份
        AYM_sure = self.cursor.fetchall()
        AYM_mksure = [i for i in AYM_sure]
        AYM_mksure = sorted(set(AYM_mksure),key= AYM_mksure.index)
        # print(len(AYM_mksure))
        # print(AYM_mksure[0][0])

        List_for_Days= []
        for i in range(len(AYM_mksure)): # 多少長度＝不論年度共幾個月份                                           # years         # months
            self.cursor.execute("SELECT Days FROM DOWNLOAD_INFO WHERE Years ='{}' AND Months='{}' ".format(AYM_mksure[i][0],AYM_mksure[i][1]))
            ds= self.cursor.fetchall()
            days=[i[0] for i in ds]
            days = sorted(set(days),key= days.index)
            # print('{}年{}月:{}'.format(AYM_mksure[i][0],AYM_mksure[i][1],days))
            List_for_Days.append([AYM_mksure[i][0],AYM_mksure[i][1],days])
        # print(List_for_Days)
        return  List_for_Days


    def Month_PerDaily_Stream_Plot(self):
        T = True
        while T:
            DS = self.Month_PerDaily_Stream()
            print('資料庫內含月份：')
            for i,j in enumerate(DS):
                print("[{}]: {}年{}月".format(i+1,j[0],j[1]),end='  ')
            print('\n')
            keyin = input('Key-in編號來查看當月每日流量: ')
            print('Key-in: {}'.format( DS[int(keyin)-1]))

            TH= [] # 當月每日總流量
            for p in range(len(DS[int(keyin)-1][2])):
                self.cursor.execute("SELECT TotalHourStream FROM DOWNLOAD_INFO WHERE Years ='{}' AND Months='{}'AND Days='{}' ".format(DS[int(keyin)-1][0],DS[int(keyin)-1][1],DS[int(keyin)-1][2][p]))
                TH_sure= self.cursor.fetchall()
                TH_mk_sure= [i[0] for i in TH_sure]
                TH.append(np.sum(TH_mk_sure))

            fig= plt.figure(figsize=(10,4))

        # 先分配出一個月31日：
            y =[0]*31
            k=0
            for i in DS[int(keyin)-1][2]:
                y[int(i)-1] = TH[k]
                k += 1
            y= np.array(y)
            x= np.arange(1,31+1,1)
        # 再轉成2d array:
            data2= np.array([x,y])
            # print(data[...,:1])

            line, = plt.plot([],[], linestyle='-', marker='*', color='navy', alpha=0.6, lw=5) # 不是  plt.plot_date 不然軸會顯示錯誤
        # 設定範圍
            plt.ylim(-1, max(y) + 10)
            plt.xlim(min(x), max(x))

            line_ani = animation.FuncAnimation(fig, self.Update_line, len(y) + 1, fargs=(data2, line), interval=20,blit=True, repeat=False)
        # Label:

            fig.autofmt_xdate()
            plt.title('Daily Stream')
            plt.xlabel('Day')
            plt.ylabel('Mb')
            plt.grid()
            plt.show()

            TT = True
            while TT:
                tof = input('Close?: 1.Yes 2.No  ')
                if tof == '1':
                    T = False
                    TT = False
                elif tof== '2':
                    T= True
                    TT = False
                else:
                    print('北七, 按1 或 2都不會嗎？')
                    TT = True


    def Year_PerMonthly_Stream(self):
        self.cursor.execute("SELECT Years FROM Download_Depot ")
    # 統計年份
        AYM_sure = self.cursor.fetchall()
        AYM_mksure = [i for i in AYM_sure]
        AYM_mksure = sorted(set(AYM_mksure),key= AYM_mksure.index)
        # print(AYM_mksure)
        # print(AYM_mksure[0][0])

        List_for_Months= []
        for i in range(len(AYM_mksure)): # 多少長度＝多少年份                                       # years
            self.cursor.execute("SELECT Monthly FROM Download_Depot WHERE Years ='{}' ".format(AYM_mksure[i][0]))
            ms= self.cursor.fetchall()
            months=[i[0] for i in ms]
            months = sorted(set(months),key= months.index)
            # print('{}年{}月:{}'.format(AYM_mksure[i][0],AYM_mksure[i][1],days))
            List_for_Months.append([AYM_mksure[i][0],months])
            print(List_for_Months)
        return  List_for_Months


    def Year_PerMonthly_Stream_Plot(self):
        T = True
        while T:
            MS= self.Year_PerMonthly_Stream()
            print('資料庫內含年份：')
            for i, j in enumerate(MS):
                print("[{}]: {}年".format(i + 1, j[0]), end='  ')
            print('\n')
            keyin = input('Key-in編號來查看當年每月流量: ')
            print('Key-in: {}'.format(MS[int(keyin) - 1]))

            TH = []  # 當年每月總流量
            for p in range(len(MS[int(keyin) - 1][1])):
                self.cursor.execute(
                    "SELECT MonthlyStream FROM Download_Depot WHERE Years ='{}' AND Monthly='{}' ".format(MS[int(keyin) - 1][0], MS[int(keyin) - 1][1][p] ))
                TH_sure = self.cursor.fetchall()
                TH_mk_sure = [i[0] for i in TH_sure]
                TH.append(np.sum(TH_mk_sure))
            # print(TH)
            fig = plt.figure(figsize=(10,4))

            y = [0] * 12
            k = 0
            for i in MS[int(keyin) - 1][1]:
                y[int(i) - 1] = TH[k]
                k += 1
            y = np.array(y)
            x = np.arange(1, 12 + 1, 1)

            plt.bar(x, y, align='center', alpha=0.5)
            plt.title('Monthly Stream')
            plt.xlabel('Month')
            plt.ylabel('Mb')
            plt.grid()
            plt.show()

            TT = True
            while TT:
                tof = input('Close?: 1.Yes 2.No  ')
                if tof == '1':
                    T = False
                    TT = False
                elif tof == '2':
                    T = True
                    TT = False
                else:
                    print('北七, 按1 或 2都不會嗎？')
                    TT = True



