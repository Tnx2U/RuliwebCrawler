import requests
from bs4 import BeautifulSoup as bs
import sys
import re
import threading
import time #소모시간 출력용

class ruliweb_used_searcher:

    def __init__(self):
        self.price_list = []
        self.title_list = []
        self.login_INFO = {
            'user_id': 'pluxlight',
            'user_pw': 'dgdh49@ruli'
        }

    # 최저가 찾는 함수
    def low_price(self, price_list):
        small_price = 999999999
        cnt = 0
        list_position = 0
        for i in price_list:
            if i < small_price and i > 1000:
                small_price = i
                list_position = cnt
            cnt += 1
        return list_position

    # 검색할 게시글 번호만 찾는 함수
    def search_post_num(self, s, url):
        list_page = s.get(url)
        html = list_page.text
        soup = bs(html, 'html.parser')
        num = soup.find_all('span', class_='market_num')
        list_num = []
        for t in num:
            t = t.get_text()
            t = t.strip()
            list_num.append(t)
        # 불필요한 첫번째 리스트 요소 '번호'를 제거
        del list_num[0]
        # print(list_num)

        # 취소선이 적용된 글은 제외하는 부분
        strike_title = soup.find_all('strike')
        strike_num_list = []
        for i in strike_title:
            i = str(i)
            i = i.split('find')[0]
            i = i.split('num')[1]
            i = str(int(re.findall('\d+', i)[0]))  # 문자와 숫자가 섞여있어 숫자만 필터링을 거쳐서 리스트에 저장
            strike_num_list.append(i)
        for i in strike_num_list:
            list_num.remove(i)

        return list_num

    # 게시글 개별로 접속해서 가격정보, 게시글 제목 리스트에 저장하는 함수
    def post_search(self, list_num, list_url, s):

        for i in list_num:
            url = list_url + str(i)
            page_in = s.get(url)
            html = page_in.text
            soup = bs(html, 'html.parser')
            price = soup.find_all('td', attrs={'style': 'background-color: #ffffff;'})
            td_list = []
            for p in price:
                p = p.get_text() #텍스트 요소만 가져오기
                p = p.strip() #앞, 뒤 공백제거
                p = p.replace("\xa0", '') #불필요한 문자열 제거
                td_list.append(p) #리스트에 p 삽입
            try:  # 가격을 적어놓지 않은 경우에는 최저가 필터에서 걸러지게 99999999로 표시
                # 그냥 제외시켜버리니 검색 후 결과 표시에서 게시글 출력이랑 주소 출력이 엇갈려버림
                # TO-DO : 엇갈리는 원인 파악
                td_list_int = int(re.findall('\d+', td_list[4])[0])  # 문자와 숫자가 섞여있어 숫자만 필터링을 거쳐서 리스트에 저장
                self.price_list.append(td_list_int)
                self.title_list.append(td_list[0])
            except:
                self.price_list.append(999999999)
                self.title_list.append(td_list[0])


    def main(self):
        with requests.Session() as s:  # 로그인 세션이 계속 유지됨

            login_req = s.post('https://user.ruliweb.com/member/login_proc', data=self.login_INFO)

            if login_req.status_code == 200 and login_req.ok:
                print('Login Ok')
            else:
                print('Error')
                sys.exit(1)

            while (1):
                search_group = input('검색할 유형을 고르세요\n1. PS3/4 2.XBOX 3.스위치/Wii 4.3DS/NDS q 입력시 프로그램 종료 : ')

                # base_url은 게시글 리스트에 접속하기 위한 url
                # list_url은 게시글에 직접 접속하기 위한 url

                if search_group == '1':
                    print('PS3/4를 검색')
                    base_url = 'http://market.ruliweb.com/list.htm?table=market_ps&find=subject&ftext='
                    list_url = 'http://market.ruliweb.com/read.htm?table=market_ps&page=1&num='
                elif search_group == '2':
                    print('XBOX를 검색')
                    base_url = 'http://market.ruliweb.com/list.htm?table=market_xbox&find=subject&ftext='
                    list_url = 'http://market.ruliweb.com/read.htm?table=market_xbox&page=1&num='
                elif search_group == '3':
                    print('스위치/Wii를 검색')
                    base_url = 'http://market.ruliweb.com/list.htm?table=market_ngc&find=subject&ftext='
                    list_url = 'http://market.ruliweb.com/read.htm?table=market_ngc&page=1&num='
                elif search_group == '4':
                    print('3DS/NDS를 검색')
                    base_url = 'http://market.ruliweb.com/list.htm?table=market_nds&find=subject&ftext='
                    list_url = 'http://market.ruliweb.com/read.htm?table=market_nds&page=1&num='
                elif search_group == 'q' or search_group == 'ㅂ':
                    print('Program Shutdown')
                    sys.exit()
                else:
                    print('잘못된 선택지 입니다')

                search_word = input('검색할 단어를 입력하세요 : ')
                start_time = time.time()  # 검색시작시간
                url = base_url + search_word + '&ftext2=&ftext3=3' #선택한 게시판과 단어를 합친 url

                # 아래 변수는 위 선택과정 생략용 url
                # 예시는 스위치 게시판의 레츠고를 검색
                # base_url은 생략용 url 사용안할시 제거바람
                # url = 'http://market.ruliweb.com/list.htm?table=market_ngc&find=subject&ftext=%EB%A0%88%EC%B8%A0%EA%B3%A0&ftext2=&ftext3=3'
                # base_url = 'http://market.ruliweb.com/read.htm?table=market_ngc&page=1&num='

                list_num = self.search_post_num(s, url)

                list_num_1 = list_num[0:int(len(list_num) / 2)]
                list_num_2 = list_num[int(len(list_num) / 2):]


                # t1 = threading.Thread(target=self.post_search, args=(list_num_1, list_url, s))
                # t1.start()
                # t1.join() #쓰레드가 끝날때까지 대기
                # t2 = threading.Thread(target=self.post_search, args=(list_num_2, list_url, s))
                # t2.start()
                # t2.join()  # 쓰레드가 끝날때까지 대기

                self.post_search(list_num_2, list_url, s)

                title_cnt = self.low_price(self.price_list)

                print(str(self.price_list[title_cnt]) + '원')
                print(self.title_list[title_cnt])
                print(list_url + list_num[title_cnt])

                print("--- %s seconds ---" % (time.time() - start_time))  # 검색끝난시간 - 검색시작시간
                print('\n')

                #리스트 초기화
                self.price_list = []
                self.title_list = []


if __name__=="__main__":
    r = ruliweb_used_searcher()
    r.main()
