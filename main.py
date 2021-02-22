import requests
import datetime
import telegram
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def getBSoup(link):
    html = requests.get(link)
    soup = BeautifulSoup(html.text, 'html.parser')
    return soup

class date:
    def __init__(self, year, month, day):
        self.year = year
        self.month = month
        self.day = day
        self.str = year + month + day
    def compare(self, date):
        if int(self.year) > int(date.year):
            return -1
        elif int(self.year) == int(date.year):
            if int(self.month) > int(date.month):
                return -1
            elif int(self.month) == int(date.month):
                if int(self.day) > int(date.day):
                    return -1
                elif int(self.day) == int(date.day):
                    return 0
                else:
                    return 1
            else:
                return 1
        else:
            return 1

class movie:
    dates = []
    def __init__(self, title):
        self.title = title

class theater:
    url = "http://www.cgv.co.kr/common/showtimes/iframeTheater.aspx?areacode=01&theatercode=#&date=@"
    movies = []
    def __init__(self, name, code):
        self.name = name
        self.url = self.url.replace('#', code)
    def add_movie(self, title, date):
        isExist = False
        global movie
        for movie in self.movies:
            if movie.title == title:
                movie.dates.append(date)
                isExist = True
        if not isExist:
            movie = movie(title)
            movie.dates.append(date)
            self.movies.append(movie)
            
class movieManager:
    movies = []
    dates = []
    theaters = []
    
    """ str only """
    def add_movie(self, title):
        self.movies.append(title)

    """ class date only """
    def add_date(self, date):
        if len(self.dates) > 0:
            for mydate in self.dates:
                if mydate.compare(date) != 0:
                    self.dates.append(date)
                    break
        else:
            self.dates.append(date)

    """ class theater only """
    def add_theater(self, theater): 
        self.theaters.append(theater)

    def get_movie_schedule(self):
        for theater in self.theaters:
            slider_dates = self.get_dates_by_slider(theater)
            for date in self.dates:
                is_date_exist = False
                for slider_date in slider_dates:
                    if slider_date.compare(date) == 0:
                        is_date_exist = True
                if is_date_exist:
                    url = theater.url.replace('@', date.str)
                    for movie in self.movies:
                        soup = getBSoup(url)
                        title_list = soup.select('div.info-movie > a > strong')
                        for title in title_list:
                            title = title.text.strip()
                            movie = movie.strip()
                            if title == movie:
                                theater.add_movie(title, date)
        return self.theaters

    def get_dates_by_slider(self, theater):
        """ theater class """
        url = theater.url.replace('@', str(datetime.today().strftime("%Y%m%d")))
        soup = getBSoup(url)
        slider = soup.select_one("div.slider")
        dates = slider.select('div.day > a')
        dateList = []
        for rs_date in dates:
            dateStr = re.search('date=\d\d\d\d\d\d\d\d', rs_date["href"]).group().replace('date=', '')
            dateOb = date(dateStr[0:4], dateStr[4:6], dateStr[6:8])
            dateList.append(dateOb)
        return dateList

    def add_dates_by_slider_arguAfterDate(self, theater, date):
        """ theater class, date class """
        """ date 이후로 slider에 있는 모든 날짜를 추가합니다. """
        slider_date_list = self.get_dates_by_slider(theater)
        for slider_date in slider_date_list:
            if slider_date.compare(date) < 1:
                self.add_date(slider_date)

class telegramBot:
    def __init__(self):
        token_file = open('token', 'r')
        chat_id = open('chat_id', 'r')

        self.chat_id = chat_id.readline()
        self.bot = telegram.Bot(token = token_file.readline())

        token_file.close()
        chat_id.close()

    def send_movie_schedule(self, theaters):
        message_format = "theater에서 movieTitle의 예매가 day일 열렸습니다"
        for theater in theaters:
            for movie in theater.movies:
                message = message_format.replace('theater', theater.name).replace('movieTitle', movie.title)
                days = ""
                for date in movie.dates:
                    days += date.day + ","
                message = message.replace('day', days[0:len(days)-1])
                self.bot.sendMessage(self.chat_id, message)
        
# mm = movieManager()
# mm.add_movie('극장판 귀멸의 칼날-무한열차편')
# mm.add_date(date("2021",'02','25'))
# mm.add_theater(theater('판교CGV', '0181'))

# theaters = mm.get_movie_schedule()

# bot = telegramBot()
# bot.send_movie_schedule(theaters)
