#coding=utf-8
from dannyTumblr import *
import re
from bs4 import BeautifulSoup
import requests
import urllib.request
import os
import sys
import time
import progressbar
from dannyTumblr.Login import Log
from dannyTumblr.DataBase import Mysql_data
from dannyTumblr.Dataplot import DataPlot



class Tumblr:
    def __init__(self):
        self.ori_path= os.getcwd()
        print(self.ori_path)
        ll= Log()
        global driver
        driver = ll.Login()
        # 呼叫sql:
        self.mysqldata = Mysql_data()


    def parse(self):
        info= input(' << 輸入該帳號或網址： >> \n')
        info_all = info
        pat = re.compile('(?:http|https)://.*.tumblr.com')   #   (?: A | B  ) 取Ａ或Ｂ的正則表達式，如果不加？： 會只顯示關鍵字Ａ或Ｂ 而不是要的全部字串
        pat_post= re.compile('.*/post/.*')

    # default variables:
        types = 'full-page'
        page_number='1'
        information=''
    # 給網址
        if pat_post.search(info):
            pat_list= re.split('.tumblr.com/post/|/',info)
            if pat_list[1]=='':
                info=pat_list[2]
            else:
                info=pat_list[0]
            print('輸入的帳號是：{}'.format(info))
            types='post-page'
    # 給帳號
        elif pat.search(info):
            print('輸入的帳號是：{}'.format(info))
        # 讀取先前頁數資料：
            self.mysqldata.Page_mksure(info)
            page_number = input('<<給頁數範圍：page,page >>\n')
            info= pat.search(info).group()
            info= info.split('.tumblr.com')[0]
            info = re.split('(?:http://|https://)',info)[1]
        # 更新頁數資料：
            self.mysqldata.PG(info, page_number)
        else:
            print('輸入的帳號是：{}'.format(info))
        # 讀取先前頁數資料：
            self.mysqldata.Page_mksure(info)
            page_number = input('<<給頁數範圍：page,page >>\n')
            info=info
        # 更新頁數資料：
            self.mysqldata.PG(info, page_number)


        pages=[]
        if types == 'full-page':
            tag_info = input('paste tags or input 0 for none :')
            if tag_info == '0':
                information = 'http://' + info + '.tumblr.com/page/' + page_number
            else:
                information = tag_info + '/page/' + page_number

            if len(page_number.split(',')) > 1:
                # 頁數範圍：
                pages = [int(page_number.split(',')[0]),int(page_number.split(',')[1])]
            else:
                # 單一頁：
                pages = [int(page_number)]


        elif types == 'post-page':
            information = info_all

        # Crawler:
        start = time.time()
        try:
            driver.set_page_load_timeout(30)
            driver.get(information)
        except :
            print(' \n~~~~連線太久啦~~~~\n ')
            sys.exit()

        soup = BeautifulSoup(driver.page_source, "html.parser")
        soup_confirm = str(soup)

        print('types:{}'.format(types))
        end = time.time()
        count = round((end-start),3)
        print('啟動瀏覽起耗時：{} 秒'.format(count))


        # 先判斷來源是否錯誤：
        if soup_confirm == '<html><head></head><body></body></html>':   # 網址key錯
            print('404 Not Found1')
        elif str(soup.find('title')) == '<title>Not found.</title>':      # 查無此帳號
            print('404 Not Found2')
        #  http://ekilsekilsekilsdaliuchiachum.tumblr.com

        else:
            self.download(info,info_all,types,information,pages)  # info_all 改為list


    def download(self,info,info_all,types,information,pages):
        print('')
        print('<<<<<<<< Loading  >>>>>>>>')
        print('')
        list_photo = []
        if types== 'post-page':
            urllist = [info_all]
            self.download_post_page(info,urllist)

        elif types == 'full-page':
            self.download_post_page(info,self.download_full_page(info,information,pages))


    def download_post_page(self,info,urls):

        # 設定資料夾大小：
        Check = self.mysqldata.Default_for_folder_size(info)

        # 更新資料夾檔案大小：
        folder_size = self.file_size(info)
        if Check == False:
            self.mysqldata.update_folder_size(info, self.file_size(info))

        # 進入download 回圈：
        pat_jpg = re.compile('(?:http|https)://78.media.tumblr.com/.*/tumblr_.*?\.(?:png|jpg|gif)')  # ? 匹配0次或一次
        # print(urls)
        list_photo = []
        minus_article_count = 0 # 文章計數器

        for adress in urls:
            bool_for_tomeout = True

            while bool_for_tomeout == True:
                try:
                    driver.get(adress)   # 之後加個try 以防之後網路問題crash
                    soups = BeautifulSoup(driver.page_source, "html.parser")

                    # 找tag裡的meta 和 img：
                    photo_meta = soups.find_all('meta')  # 圖藏在 content 裡面
                    photo_imgsrc = soups.find_all('img')  # 圖存在tag img 裡的 src

                    # 把找到的url 丟進ist裡去：
                    photo_meta_url_list = [pat_jpg.search(str(i)).group() for i in photo_meta if pat_jpg.search(str(i))]
                    photo_imgsrc_ = [i.get('src') for i in photo_imgsrc]
                    photo_imgsrc_list = [pat_jpg.search(str(i)).group() for i in photo_imgsrc_ if pat_jpg.search(str(i))]


                    # print('photo_meta_url_list :{}'.format(photo_meta_url_list))
                    # print ('')
                    # print('photo_imgsrc_list :{}'.format(photo_imgsrc_list))
                    # print('')
                    #pat_compare = re.compile('(?<=_)\d+\.(?:png|jpg|gif)')  # _abc7abc    向後斷言：(?<=_)abc  ：找abc開頭的字串，且該字串前面有＿ ，所以只會找到：abc

                    pat1 = re.compile('tumblr.*\.(?:png|jpg|gif)') # 只裁出 tumblr_亂碼＿解析度.jpg:
                    pat2 = re.compile('(?<=_).*\.(?:png|jpg|gif)') # 再裁出 亂碼＿解析度.jpg
                    pat3 = re.compile('(.*)_(\d+)')    # 最後把亂碼跟解析度分出

                    # tumblr:
                    tumblr_first_stage_url = re.findall('"https://www.tumblr.com/video/.*/"',
                                                        str(soups))  # 第一階段：取出轉載網址，但這還不是影片網址
                    # Instgram;
                    pat_insta = re.compile('https://www.instagram.com/')



                    # 如果在 meta,img 都找到 就看誰的解析度高 ：
                    if photo_meta_url_list != [] and photo_imgsrc_list != []:

                        # meta:
                        meta_list_get_from_return = self.meta_solution(photo_meta_url_list, pat1, pat2, pat3)    #[0]:resolution ; [1]: url_list ; [2]: smallest resolution position

                        # img:
                        imgsrc_list_get_from_return = self.imgsrc_solution(photo_imgsrc_list, pat1, pat2, pat3)   #[0]:resolution ; [1]: url_list ; [2]: smallest resolution position


                        # 總解析度：
                        meta_all_resolution = 0
                        for i in meta_list_get_from_return[0]:
                            meta_all_resolution = meta_all_resolution + int(i)

                        imgsrc_all_resolution = 0
                        for i in imgsrc_list_get_from_return[0]:
                            imgsrc_all_resolution = imgsrc_all_resolution + int(i)


                        # 比較 @1 ~ @4：
                        if meta_list_get_from_return[2] == [] and imgsrc_list_get_from_return[2] != []: # @1
                            list_photo= meta_list_get_from_return[1]
                            #print('@1 :list_photo= photo_imgsrc_list:{}'.format(list_photo))
                            print('@1')
                        elif meta_list_get_from_return[2] == [] and imgsrc_list_get_from_return[2] !=[]: #@2
                            list_photo= imgsrc_list_get_from_return[1]
                            #print('@2 :list_photo= photo_imgsrc_list:{}'.format(list_photo))
                            print('@2')
                        else:

                            if meta_all_resolution >= imgsrc_all_resolution:
                                list_photo= meta_list_get_from_return[1]
                                #print('@3: list_photo= photo_meta_url_list:{}'.format(list_photo)) #@3
                                print('@3')
                            elif meta_all_resolution < imgsrc_all_resolution:
                                list_photo = imgsrc_list_get_from_return[1]
                                #print('@4: list_photo= photo_imgsrc_list:{}'.format(list_photo)) #@4
                                print('@4')

                        if tumblr_first_stage_url != []:
                            # print(vodeo_first_stage_url)
                            print('Tumblr Video \n')
                            self.savevideo_tumblr(info, tumblr_first_stage_url)  # 第二階段丟入分析

                        elif pat_insta.search(str(soups)):
                            # Instgram;
                            # https://stem-stims.tumblr.com/
                            print('Instagram Video \n')
                            ig_url = (soups.find_all('iframe'))
                            self.savevideo_instagram(info, ig_url)


                    # 不然就看找到誰的格式：
                    else:
                        if photo_meta_url_list != []:
                            print('meta有找到圖片檔')
                            print('meta:{}'.format(photo_meta_url_list))
                            # meta:
                            meta_list_get_from_return = self.meta_solution(photo_meta_url_list, pat1, pat2,pat3)  # [0]:resolution ; [1]: url_list ; [2]: smallest resolution position
                            list_photo = meta_list_get_from_return[1]

                            if tumblr_first_stage_url != []:
                                # print(vodeo_first_stage_url)
                                print('Tumblr Video \n')
                                self.savevideo_tumblr(info, tumblr_first_stage_url)  # 第二階段丟入分析

                            elif pat_insta.search(str(soups)):
                                # Instgram;
                                # https://stem-stims.tumblr.com/
                                print('Instagram Video \n')
                                ig_url = (soups.find_all('iframe'))
                                self.savevideo_instagram(info, ig_url)

                        elif photo_imgsrc_list != []:
                            print('imgsrc有找到圖片檔')
                            photo_imgsrc_list = [pat_jpg.search(i).group() for i in photo_imgsrc_list if pat_jpg.search(i)]
                            print('src:{}'.format(photo_imgsrc_list))
                            # img:
                            imgsrc_list_get_from_return = self.imgsrc_solution(photo_imgsrc_list, pat1, pat2,pat3)  # [0]:resolution ; [1]: url_list ; [2]: smallest resolution position
                            list_photo = imgsrc_list_get_from_return[1]

                            if tumblr_first_stage_url != []:
                                # print(vodeo_first_stage_url)
                                print('Tumblr Video \n')
                                self.savevideo_tumblr(info, tumblr_first_stage_url)  # 第二階段丟入分析

                            elif pat_insta.search(str(soups)):
                                # Instgram;
                                # https://stem-stims.tumblr.com/
                                print('Instagram Video \n')
                                ig_url = (soups.find_all('iframe'))
                                self.savevideo_instagram(info, ig_url)

                        else:

                            if tumblr_first_stage_url!=[]:
                                #print(vodeo_first_stage_url)
                                print('Tumblr Video \n')
                                self.savevideo_tumblr(info,tumblr_first_stage_url)  # 第二階段丟入分析

                            elif pat_insta.search(str(soups)):
                                # Instgram;
                                # https://stem-stims.tumblr.com/
                                print('Instagram Video \n')
                                ig_url = (soups.find_all('iframe'))
                                self.savevideo_instagram(info,ig_url)

                            else:
                                print('  !!  可能該Post沒東西抓  !!  ')
                                print('')
                    bool_for_tomeout = False

                    if len(list_photo) != 0:
                        self.savephoto(info,list_photo)
                        list_photo = []
                    minus_article_count += 1
                    try:
                        len(self.all_articles)
                        print('剩下 {} posts'.format(int(len(self.all_articles)) - int(minus_article_count)))
                    except:
                        break
                except:
                    bool_for_tomeout = True
                    print('掉線 重新啟動虛擬瀏覽器試試')

        after_size = self.file_size(info)
        self.mysqldata.DL(info,folder_size,after_size)
        T= True
        while T==True:
            tof = input('下載完畢，是否需要查看 Data庫的數據？ 1.Yes 2.No : ')

            if tof == '1':
                T = True
                # 呼叫 dataplot:
                self.myplot = DataPlot()
                keyin = input('1. 查看Login資料 2. 查看每日流量 3. 查看每月流量  4. 離開 : ')
                if keyin == '1':
                    self.myplot.LoginPlot()
                elif keyin == '2':
                    self.myplot.Month_PerDaily_Stream_Plot()
                elif keyin == '3':
                    self.myplot.Year_PerMonthly_Stream_Plot()
                else:
                    print('Quit')
                    T = False
            elif tof == '2':
                T = False
            else:
                T = True


    def download_full_page(self, info, information,pages):  # 在full-page 找到每則po文的url 最後會丟回到 post-page 去載資料

        # pat_information_cut = re.compile('http://.*.tumblr.com/page/' )
        pat_information_cut = re.compile('http://.*./page/')
        information_cut_for_crawler = pat_information_cut.search(information).group()
        article_post_filelist_for_loop = []
        #print('pages:{}'.format(pages))
        if len(pages) == 1:
            pages.append(pages[0])

        for pg in range(pages[0],pages[1]+1):
            bool_for_now_loading = True
            while bool_for_now_loading == True:
                try:
                    # Crawler for list pages:
                    driver.implicitly_wait(20)  # seconds  每則讀取設定等待最多20秒 不設定讀到後面會報錯
                    driver.get(information_cut_for_crawler+str(pg))
                    soup = BeautifulSoup(driver.page_source, "html.parser")

                    print('正在讀取第{}頁 💬 '.format(pg))

                    if soup.find_all('article'):
                        print('##### Situation 1: Post文章編號 藏在article  #####')

                        article_post_num = []
                        article_post = soup.find_all('article')
                        for i in article_post:
                            if i.get('id'):
                                notcut = i.get('id')
                                cut = notcut.split('post-')[1]
                                article_post_num.append(cut)
                            elif i.get('data-post-id'):
                                article_post_num.append(i.get('data-post-id'))
                            else:
                                if soup.find('div'):
                                    print('##### Situation 例外: Post文章編號 其實藏在div #####')

                                    article_post = soup.find_all('div')
                                    article_post_num = [i.get('data-post-id') for i in article_post]
                                    article_post_num = [i for i in article_post_num if i != None]
                                else:
                                    print('article fond id wrong')
                        article_post_filelist = ['https://' + info + '.tumblr.com/post/' + i for i in article_post_num]
                        #print('所有網址:{}'.format(article_post_filelist))
                        print('')
                        #return article_post_filelist

                    elif soup.find('div'):
                        print('##### Situation 2: Post文章編號 藏在div #####')
                        article_post = soup.find_all('div')
                        article_post_num = [i.get('data-post-id') for i in article_post]
                        article_post_num = [i for i in article_post_num if i != None]
                        article_post_filelist = ['https://' + info + '.tumblr.com/post/' + i for i in article_post_num]
                        if article_post_filelist != []:
                            print('所有網址:{}'.format(article_post_filelist))
                            print(len(article_post_filelist))
                            #return article_post_filelist
                        else:
                            article_post_num = []
                            article_post_filelist = []
                            print('New 隱藏位置＿new version: 2018/01/29')
                            print('↓↓↓↓↓↓↓')
                            try:
                                again= soup.find_all('a')
                                # print(again)
                                for i in again:
                                    g= i.get('href')
                                    article_post_num.append(g)
                                # print(article_post_num)

                                pat20180129 = re.compile('.*/post/.*')
                                for i in article_post_num:
                                    if pat20180129.search(i) :
                                        temp_c= pat20180129.search(i).group()
                                        # print(temp_c)
                                        article_post_filelist.append(temp_c)
                                print(article_post_filelist)

                            except:
                                print(damn)

                            print('↑↑↑↑↑↑↑')
                    else:
                        print('##### Situation else #####')

                    [article_post_filelist_for_loop.append(af) for af in article_post_filelist]
                    bool_for_now_loading = False
                except:
                    print('正在讀取 但是掉線正在重新啟動虛擬瀏覽器')
                    bool_for_now_loading = True

        print('所有網址共{}則'.format(len(article_post_filelist_for_loop)))
        self.all_articles = article_post_filelist_for_loop
        print('第{}~{}頁 的所有網址:{}'.format(pages[0],pages[1],article_post_filelist_for_loop))
        return article_post_filelist_for_loop


    def find_same_garbled_position(self,l): # l: list

        aa = [[i for i, v in enumerate(l) if v == x] for x in l]
        ap = [i for i in aa if len(i) > 1]
        ape = [str(i) for i in ap]
        l2 = []
        l3 = []
        [l2.append(i) for i in ape if not i in l2]
        for i in l2:
            yup = re.split(']|\[|,', i)
            a = [ii for ii in yup if ii != '']
            l3.append(a)
        return l3
        #print(l3)


    def meta_solution(self,photo_meta_url_list,pat1,pat2,pat3):
        # meta:
        # 只裁出 tumblr_亂碼＿解析度.jpg:
        temp_meta1 = [pat1.search(i).group() for i in photo_meta_url_list]
        # 再裁出 亂碼＿解析度.jpg
        temp_meta2 = [pat2.search(i).group() for i in temp_meta1]

        meta_garbled = [pat3.search(i).group(1) for i in temp_meta2]  # 亂碼
        meta_resolution = [pat3.search(i).group(2) for i in temp_meta2]  # 解析度

        # 找重複亂碼的位置：
        find_same_garbled_position = self.find_same_garbled_position(meta_garbled)

        not_just_zero = 10000  # 寫個很大的解析度
        smallest_resolution_position = []
        if find_same_garbled_position == []:
            pass
        else:
            print('meta find_same_garbled_position:{}'.format(find_same_garbled_position))
            for ii in find_same_garbled_position:
                ipis = 0
                for ipis in ii:
                    if int(meta_resolution[int(ipis)]) < not_just_zero:
                        not_just_zero = int(meta_resolution[int(ipis)])

                smallest_resolution_position.append(int(ipis))
                print('meta Not just zero最低解析度:{}'.format(not_just_zero))
            print('meta 最低解析度位置:{}'.format(smallest_resolution_position))

            meta_resolution = [ii for i, ii in enumerate(meta_resolution) if i != smallest_resolution_position]

            photo_meta_url_list = [ii for i, ii in enumerate(photo_meta_url_list) if i not in smallest_resolution_position]
            print('meta 刪除重複的url list後:{}'.format(photo_meta_url_list))

        meta_list_for_return=[meta_resolution,photo_meta_url_list,smallest_resolution_position]
        return meta_list_for_return


    def imgsrc_solution(self,photo_imgsrc_list,pat1,pat2,pat3):
        # img:
        # 只裁出 tumblr_亂碼＿解析度.jpg:
        temp_src1 = [pat1.search(i).group() for i in photo_imgsrc_list]
        # 再裁出 亂碼＿解析度.jpg
        temp_src2 = [pat2.search(i).group() for i in temp_src1]

        imgsrc_garbled = [pat3.search(i).group(1) for i in temp_src2]  # 亂碼
        imgsrc_resolution = [pat3.search(i).group(2) for i in temp_src2]  # 解析度

        # 找重複亂碼的位置：
        find_same_garbled_position2 = self.find_same_garbled_position(imgsrc_garbled)

        not_just_zero2 = 10000
        smallest_resolution_position2 = []
        if find_same_garbled_position2 == []:
            pass
        else:
            print('imgsrc find_same_garbled_position2:{}'.format(find_same_garbled_position2))
            for ii in find_same_garbled_position2:
                ipis=0
                for i in ii:
                    if int(imgsrc_resolution[int(ipis)]) < not_just_zero2:
                        not_just_zero2 = int(imgsrc_resolution[int(ipis)])
                smallest_resolution_position2.append(int(ipis))
                print('imgsrc Not just zero2最低解析度:{}'.format(not_just_zero2))
            print('imgsrc 最低解析度位置:{}'.format(smallest_resolution_position2))

            imgsrc_resolution = [ii for i, ii in enumerate(imgsrc_resolution) if i != smallest_resolution_position2]

            photo_imgsrc_list = [ii for i, ii in enumerate(photo_imgsrc_list) if i not in smallest_resolution_position2]
            print('imgsrc 刪除重複的url list後:{}'.format(photo_imgsrc_list))

        imgsrc_list_for_return =[imgsrc_resolution,photo_imgsrc_list,smallest_resolution_position2]
        return imgsrc_list_for_return


    def savephoto(self,info,list_photo):

        # <<<<<PHOTO>>>>>>>
        if list_photo != []:
            if not os.path.exists(self.ori_path + '/' + 'dannyTumblr' + '/' + 'Download' + '/' + info+ '/' + 'Photos'):
                os.makedirs(self.ori_path + '/' + 'dannyTumblr' + '/' + 'Download' + '/' + info+ '/'  + 'Photos')
            os.chdir(self.ori_path + '/' + 'dannyTumblr' + '/' + 'Download' + '/' + info+ '/'  + 'Photos')
            pat_photoname = re.compile('tumblr_.*?\.(png|jpg|gif)')
            for index, i in enumerate(list_photo):
                url_photo = urllib.request.urlopen(i).read()

                try:
                    tumblr_name = pat_photoname.search(i).group()
                    garbled_name=re.split('_|\.', tumblr_name)

                    print('file_name:{}'.format(tumblr_name))

                    if os.path.exists( self.ori_path + '/' + 'dannyTumblr' + '/' + 'Download' + '/' + info+ '/'  + 'Photos' + '/'+ tumblr_name):
                        print('Already Downloaded :(')

                    else:
                        print('New :)')
                        with open(tumblr_name, 'wb') as pics:
                            pics.write(url_photo)
                            pics.close()
                except:
                    print('Write Wrong')
                    pass
            print('')
            print('CYCLE DONE_ "爬完一則貼文了" _CYCLE DONE ')
            os.chdir(self.ori_path)


    def save_continue_progress(self,info,videofilename,url):

        dl = True
        path01 = os.getcwd()
        while_counter = 0
        slice = 1024 * 1  # 讀取影片串流區塊大小

        while dl == True:
            iterator = 0
            clist = []
            piece_count = 0
            print('讀取資料中.........')

            with open(videofilename + '.mp4', 'wb')as f:
                try:
                    print('start')

                    r = requests.get(url, stream=True,timeout=15)
                    file_size = int(r.headers['Content-Length'])
                    size = str(file_size)
                    piece = int(int(size) / 1024)
                    print('piece:{}'.format(piece))

                    bar = progressbar.ProgressBar(maxval=file_size, widgets=[progressbar.Percentage(), ' : ',
                                                                             progressbar.Counter(), ' of ',
                                                                             progressbar.FormatCustomText(size),
                                                                             ' bytes',
                                                                             ' [', progressbar.AdaptiveTransferSpeed(),
                                                                             '] ',
                                                                             # progressbar.ETA(),
                                                                             # ' [',progressbar.Timer(), '] ',
                                                                             progressbar.Bar(marker='■'),
                                                                             ]).start()

                    for chunk in r.iter_content(chunk_size=slice):
                        try:
                            def gen():
                                yield chunk

                            ge = gen()
                            if len(chunk) == 1024:
                                f.write(ge.__next__())

                                clist.append(len(chunk))

                                # f.write(chunk)
                                iterator += slice
                                bar.update(iterator)
                                piece_count += 1
                                if int(piece_count) == int(piece):
                                    dl = False
                                    break
                            elif int(piece_count) == int(piece):
                                dl = False
                                break
                            else:
                                print('piece_count :{}'.format(piece_count))
                                print(' 不到 1MB 重抓')
                                f.write(ge.__next__())

                        except:
                            print('來此走一遭的 黑人問號')


                except requests.exceptions.ConnectionError:
                    print('\n  掉線拉 ')
                    dl = True
                    while_counter += 1
                    if while_counter == 10:
                        print('Give up...')
                        dl = False
                except:
                    print('黑人問號')

                finally:
                    if dl:
                        print(piece_count)
                        print(' ======Disconnect ======')
                        print('  Close file ;(')
                        os.remove(self.ori_path + '/' + 'dannyTumblr' + '/' + 'Download' + '/' + info+ '/' + 'Videos')
                    else:
                        print('  Download Done')
                        print('  Close file :>')
                        # print(clist)
                        for i in clist:
                            if i < 1024:
                                print(i)
                        print('影片總:{}字串'.format(len(clist)))
                    f.close()
        return

    # Tumblr:
    def savevideo_tumblr(self,info,tumblr_first_stage_url):

        if not os.path.exists(self.ori_path + '/' + 'dannyTumblr' + '/' + 'Download' + '/' + info+ '/' + 'Videos'):
            os.makedirs(self.ori_path + '/' + 'dannyTumblr' + '/' + 'Download' + '/' + info+ '/' + 'Videos')
        os.chdir(self.ori_path + '/' + 'dannyTumblr' + '/' + 'Download' + '/' + info+ '/' + 'Videos')


        pat_tumblr = re.compile('".*"')
        pat_tumblr_for_temp = re.compile('tumblr_.*')
        pat_tumblr_video_r1 = re.compile('.*r1')
        pat_tumblr_video_r2 = re.compile('.*r2')

        for i in tumblr_first_stage_url:
            dic_tumblr = (pat_tumblr.search(i).group()).split('"')[1]
            print(dic_tumblr)
            # 第二階段： 將第一階段的網址再進行分析
            driver.get(dic_tumblr)
            soup = BeautifulSoup(driver.page_source, "html.parser")


            temp_url = soup.find('video').get('poster')  # 第二階段： 在chrome 的media 觀察後會發現，影片的資訊會在這裡出現
            url = pat_tumblr_for_temp.search(temp_url).group()
            print('url:{}'.format(url))

            if pat_tumblr_video_r1.search(url) or pat_tumblr_video_r2.search(url):
                if len(url.split('_smart1.jpg')) > 1:
                    url = url.split('_smart1.jpg')
                else:
                    url = url.split('_frame1.jpg')

            else:
                temp_url = soup.find('source').get('src')  # 第二階段： 在chrome 的media 觀察後會發現，影片的資訊會在這裡出現
                url = pat_tumblr_for_temp.search(temp_url).group()
                url = url.split('/')  # 有時其網址會多個 /數字 ，所以要踢掉，或轉 _  不然影片網址會錯

            tumblr_url = 'https://vt.media.tumblr.com/' + url[0] + '.mp4'  # .mp4 file
            print(tumblr_url)

            videofilename = url[0]

            if os.path.exists(self.ori_path + '/' + 'dannyTumblr' + '/' + 'Download' + '/' + info+ '/' + 'Videos'+ '/' + videofilename + '.mp4'):
                    print('Video Already Downloaded x(')
            else:
                print(' NEW :P')
                start = time.time()
                # try:
                #     data = urllib.request.urlopen(tumblr_url).read()
                # except:
                #     continue
                # with open(url[0] + '.mp4','wb') as video:
                #     video.write(data)
                #     video.close()

                self.save_continue_progress(info,videofilename,tumblr_url)

                end = time.time()
                count_time = round((end - start), 3)
                print('Finish in ：{} sec'.format(count_time))



        print('CYCLE DONE_ "爬完一則貼文了" _CYCLE DONE ')
        os.chdir(self.ori_path)

    # Instagram
    def savevideo_instagram(self,info,ig_url):

        if not os.path.exists(self.ori_path + '/' + 'dannyTumblr' + '/' + 'Download' + '/' + info+ '/' + 'Videos'):
            os.makedirs(self.ori_path + '/' + 'dannyTumblr' + '/' + 'Download' + '/' + info+ '/' + 'Videos')
        os.chdir(self.ori_path + '/' + 'dannyTumblr' + '/' + 'Download' + '/' + info+ '/' + 'Videos')


        pat_insta = re.compile('https://www.instagram.com/')
        pat_insta_videourl = re.compile(' ".*"')
        filename=''
        for index, content in enumerate(ig_url):
            # print(content)
            if pat_insta.search(str(content.get('src'))):
                # print (  str(content.get('src'))  )
                driver.get(content.get('src'))  # 利用爬到的ig網址去 instagram個人網站再爬其原始影片檔
                soup = BeautifulSoup(driver.page_source, "html.parser")
                ss = soup.find_all('script')  # find 是找tag的頭
                # print(ss[1])
                # ss找到的script list 第0個 不是我要的資訊，而第一個裡面有video的資訊，所以從第一個篩選：
                dic = re.findall(' "video_url": ".*?", ', str(ss[1]))
                insta_url = str(pat_insta_videourl.search(dic[0]).group())
                insta_url = insta_url.split('"')
                print(insta_url[3])  # 找到 .mp4 file
                try:
                    filename = insta_url[3].split('https://instagram.ftpe7-1.fna.fbcdn.net/t50.2886-16/')[1]
                except:
                    print('可能是IG的影片檔網址版本又改了 導致下載有誤')
                #print(filename)

                videofilename = filename.split('.mp4')[0]

                if os.path.exists(self.ori_path + '/' + 'dannyTumblr' + '/' + 'Download' + '/' + info+ '/' + 'Videos' + '/' + filename):
                    print('Video Already Downloaded x(')
                else:
                    print(' NEW :P')
                    start = time.time()

                    self.save_continue_progress(info, videofilename, insta_url[3])

                    # data_insta = urllib.request.urlopen(insta_url[3]).read()
                    # with open(filename, 'wb') as video_insta:
                    #     video_insta.write(data_insta)
                    #     video_insta.close()
                    end = time.time()
                    count_time = round((end - start), 3)
                    print('Finish in ：{} sec'.format(count_time))
            else:
                print('instagram wrong? 很有可能是IG的影片檔網址版本又改了 ')
                break
        print('CYCLE DONE_ "爬完一則貼文了" _CYCLE DONE ')
        os.chdir(self.ori_path)

        # # Youtube :（尚未碰到tumblr要用youtube,所以暫時不寫進去  ）
        # import json
        # req = requests.get(input("輸入網址："))
        # # 向一網頁做請求
        # #print (req.text)
        #
        # dic = re.findall("ytplayer.config = ({.*?});", req.text)
        # # 擷取網頁來源中的字典
        #
        # js = json.loads(dic[0])
        # # json 編譯
        # #print (js)
        # urls = urllib.parse.parse_qs(js['args']['url_encoded_fmt_stream_map'])
        # #print (urls)
        #
        # for index,url in enumerate(urls['url']):
        #     print (urls['url'][index])

    # 計算檔案大小
    def file_size(self,info):
        if not os.path.exists(self.ori_path + '/' + 'dannyTumblr' + '/' + 'Download' + '/' + info):
            os.makedirs(self.ori_path + '/' + 'dannyTumblr' + '/' + 'Download' + '/' + info)
        os.chdir(self.ori_path + '/' + 'dannyTumblr' + '/' + 'Download' + '/' + info + '/' )

        total_size = 0
        for dirpath, dirname,filename in os.walk(os.getcwd()):
            # print(filename)
            for f in filename:
                single = os.path.join(dirpath,f)
                #print('file path :{}'.format(single))
                total_size += os.path.getsize(single)
        dl_size = round(total_size/(1000*1000),1)  # MB
        # print('{} MB '.format(dl_size))
        os.chdir(self.ori_path)
        return float(dl_size)

