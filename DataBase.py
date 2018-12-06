#coding=utf-8

import pymysql as mysql
import  os
import datetime

# 更改密码

# 打开一个终端窗口
# 输入 sudo /usr/local/mysql/support-files/mysql.server stop
# 输入 sudo /usr/local/mysql/bin/mysqld_safe --skip-grant-tables
# 这时不要关窗口，再打开一个终端窗口
# 输入 sudo /usr/local/mysql/bin/mysql -u root
# 这时候会出现mysql>了，输入use mysql
# 最后输入 update user set authentication_string=password('新密码') where user='root';
# A temporary password is generated for root@localhost: YNw(KOqjy6uQ

class Mysql_data:

    def __init__(self):

        self.now = datetime.datetime.now()

        self.path = os.getcwd()
        os.chdir(self.path + '/' + 'dannyTumblr' + '/' + 'data_folder')

        self.db = mysql.connect(host='localhost',user='root',passwd="0000",db='DannyDataBase')
        self.cursor = self.db.cursor()

        self.Table_ID = """ SELECT * FROM information_schema.tables WHERE table_name = 'LOG_IN_ID'"""
        self.Table_DL = """ SELECT * FROM information_schema.tables WHERE table_name = 'DOWNLOAD_INFO'"""
        self.Table_DD = """ SELECT * FROM information_schema.tables WHERE table_name = 'Download_Depot'"""
        self.Table_PG = """ SELECT * FROM information_schema.tables WHERE table_name = 'Page_Data'"""

    # 初始化時先創建表格：
        if not self.cursor.execute(self.Table_ID):
            sql = """CREATE TABLE LOG_IN_ID (Email CHAR(50) NOT NULL,
                                             Date CHAR(20),
                                             Count_times INT(100) ,
                                             PRIMARY KEY (Date) )"""
            self.excute(sql)

        if not self.cursor.execute(self.Table_DL):
            sql = """CREATE TABLE DOWNLOAD_INFO (ID INT NOT NULL AUTO_INCREMENT ,
                                                  Post_ID CHAR(50) NOT NULL,
                                                  Last_update_Hours INT(24),
                                                  Years CHAR(20),
                                                  Months CHAR(20),
                                                  Days CHAR (20),
                                                  TotalHourStream FLOAT,
                                                  PRIMARY KEY (ID)
                                                   )"""
            self.excute(sql)


        if not self.cursor.execute(self.Table_DD):
            sql = """CREATE TABLE Download_Depot (ID INT NOT NULL AUTO_INCREMENT ,
                                                  Post_ID CHAR(50) NOT NULL,
                                                  Years INT(20),
                                                  Monthly INT(20),
                                                  MonthlyStream FLOAT,
                                                  PRIMARY KEY (ID)
                                                   )"""
            self.excute(sql)

        if not self.cursor.execute(self.Table_PG):
            sql = """CREATE TABLE Page_Data (ID INT NOT NULL AUTO_INCREMENT ,
                                                  Post_ID CHAR(50) NOT NULL,
                                                  Last_Page_Start INT(10),
                                                  Last_Page_End INT(10),
                                                  PRIMARY KEY (ID)
                                                   )"""
            self.excute(sql)


    # 紀錄data folder位置
        self.path_for_data_folder = self.path + '/' + 'dannyTumblr' + '/' + 'data_folder'
    # 先把位置還回去，跑其他py檔
        os.chdir(self.path)


    def excute(self,sql):
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except:
            # 如果发生错误则回滚
            self.db.rollback()


    def Login_ID(self,usermail):
    # 取用data folder位置:
        os.chdir(self.path_for_data_folder)

    # 確認是否已有資料存在的手法：
    # 空的 或是隔天新的 mydate_size =[]:：
        self.cursor.execute("SELECT Date FROM LOG_IN_ID")
        mdate = self.cursor.fetchall()
        mydate = [i[0] for i in mdate]

        if mydate ==[]:
            sql = """ INSERT INTO LOG_IN_ID (Email , Date , Count_times)
                      VALUES ('{}','{}','{}') """.format(usermail, self.now.strftime('%Y-%m-%d'), 1)
        else:
            a = [i for i in mydate if i== self.now.strftime('%Y-%m-%d')]
            if len(a)== 0:
                sql = """ INSERT INTO LOG_IN_ID (Email , Date , Count_times)
                          VALUES ('{}','{}','{}') """.format(usermail, self.now.strftime('%Y-%m-%d'), 1)

            else:
                sql = """ UPDATE  LOG_IN_ID SET Count_times = Count_times + 1
                          WHERE DATE= '{}' """.format(self.now.strftime('%Y-%m-%d'))
        self.excute(sql)
        os.chdir(self.path)


    def Default_for_folder_size(self,info):
        os.chdir(self.path_for_data_folder)
                                           # 帳號,  日期 , 資料夾大小,   今次下載量
        sql = """ INSERT INTO Download_INFO (ID , Date, FolderSize, Now_Downloaded_MB )
                  VALUES ('{}','{}','{}','{}') """.format(info, self.now.strftime('%Y-%m-%d'),0,0)
        self.excute(sql)
        os.chdir(self.path)
        return False


    def update_folder_size(self, post_ID,fz): # fz=folder_size
        os.chdir(self.path_for_data_folder)
        print('fz:{}'.format(fz))
        sql = """ UPDATE  Download_INFO SET FolderSize = FolderSize + '{}'
                  WHERE DATE= '{}' AND ID='{}' """.format(fz,self.now.strftime('%Y-%m-%d'),post_ID)
        self.excute(sql)
        os.chdir(self.path)


    def Depot_mksure(self,info,now_dl,zone1,zone2):
        self.cursor.execute( "SELECT Post_ID FROM Download_Depot WHERE Post_ID='{}' AND Years='{}' AND Monthly='{}' ".format(info, zone1,zone2) )
        make_sure2 = self.cursor.fetchall()
        Download_Depot_mksure = [i[0] for i in make_sure2]

        if Download_Depot_mksure == []:
            # print('這個月第一次進來 Download_Depot  0///0')
            sql = """ INSERT INTO Download_Depot (Post_ID, Years, Monthly, MonthlyStream  )
                      VALUES ('{}','{}','{}','{}') """.format(info, zone1, zone2, now_dl)
            self.excute(sql)

        else:
            # print('阿就來過了齁 Download_Depot  ＝.,＝')
            sql = """ UPDATE Download_Depot SET  MonthlyStream =  MonthlyStream + '{}'
                              WHERE Post_ID='{}'  AND Years='{}' AND Monthly='{}' """. \
                format(now_dl, info, zone1, zone2, )
            self.excute(sql)



    def DL(self,info,fz,az): # az=after_size
        os.chdir(self.path_for_data_folder)

        Time_zone =self.now.strftime('%Y-%m-%d')
        zone1 = Time_zone.split('-')[0]
        zone2 = Time_zone.split('-')[1]
        zone3 = Time_zone.split('-')[2]

        now_dl = az-fz

        # 確認是否已有資料存在的手法：
        self.cursor.execute(
            "SELECT Post_ID FROM DOWNLOAD_INFO WHERE Post_ID='{}' AND Years='{}' AND Months='{}'AND Days ='{}' ".format(info, zone1, zone2, zone3))
        make_sure = self.cursor.fetchall()
        myid_make_sure = [i[0] for i in make_sure]

        # 確認是否已有資料存在的手法：
        self.cursor.execute(
            "SELECT Post_ID FROM Download_Depot WHERE Post_ID='{}' AND Years='{}' AND Monthly='{}' ".format(info, zone1,zone2))
        make_sure2 = self.cursor.fetchall()
        Download_Depot_mksure = [i[0] for i in make_sure2]

        # 跨日：
        if myid_make_sure == []:
            # print('今天第一次進來  >///<')
            #   帳號 ,        時,                 日期,            小時下載量
            sql = """ INSERT INTO DOWNLOAD_INFO (Post_ID, Last_update_Hours, Years,Months,Days, TotalHourStream )
                      VALUES ('{}','{}','{}','{}','{}','{}') """.format(info, self.now.hour, zone1, zone2, zone3, now_dl)
            self.excute(sql)
            self.Depot_mksure(info, now_dl, zone1, zone2)

        # 已有的話：
        else:
            a = [i for i in myid_make_sure if i == info]
            # 以 Post_ID 計數而尚未建立資料，新增：
            if len(a) == 0:
                # print('新增')
                sql = """ INSERT INTO DOWNLOAD_INFO (Post_ID, Last_update_Hours, Years,Months,Days, TotalHourStream)
                          VVALUES ('{}','{}','{}','{}','{}','{}') """.format(info, self.now.hour, zone1, zone2, zone3, now_dl)
                self.excute(sql)
                self.Depot_mksure(info, now_dl, zone1, zone2)
        # 已建立，更新就好：
            else:
                # print('更新就好 更新就好')
                # 每小時更新
                sql = """ UPDATE DOWNLOAD_INFO SET TotalHourStream = TotalHourStream + '{}', Last_update_Hours ='{}'
                          WHERE Post_ID='{}'  AND Years='{}' AND Months='{}' AND Days ='{}' """.format(now_dl, self.now.hour,info, zone1, zone2,zone3)
                self.excute(sql)
                self.Depot_mksure(info, now_dl, zone1, zone2)
        self.cursor.close()
        self.db.close()
        os.chdir(self.path)


    # 讀取先前頁數資料：
    def Page_mksure(self,info):
        self.cursor.execute("SELECT Last_Page_Start, Last_Page_End FROM Page_Data WHERE Post_ID='{}' ".format(info))
        pg_mk_sure = self.cursor.fetchall()
        page_make_sure = [i for i in pg_mk_sure]

        if pg_mk_sure == ():
            return print('尚未有頁數紀錄')
        else:
            return print('已有紀錄:{}'.format(page_make_sure))


    # 更新頁數資料：
    def PG(self,info,page_number):
        self.cursor.execute("SELECT Last_Page_Start, Last_Page_End FROM Page_Data WHERE Post_ID='{}' ".format(info))
        pg_mk_sure = self.cursor.fetchall()
        page_make_sure = [i for i in pg_mk_sure]

        start = page_number.split(',')[0]
        end = page_number.split(',')[1]

        if page_make_sure == []:
            sql = """ INSERT INTO  Page_Data (Post_ID, Last_Page_Start, Last_Page_End )
                      VALUES ('{}','{}','{}')""".format(info, start, end)
            self.excute(sql)

        else:
            sql = """ UPDATE  Page_Data SET Last_Page_Start='{}' , Last_Page_End ='{}'
                      WHERE Post_ID ='{}' """.format(start, end, info)
            self.excute(sql)
