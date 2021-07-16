import telegram
import datetime
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters
import pymysql
import pandas as pd
import logging
import auct_intra
import loadmkt

# test_token = '1767824468:AAFBSQzCNlzKCKVqYK7HlwqUlzDNqBibVdM'
prd_token = '1721072898:AAHowGdDffQr-44g0xkHAq_-YlinO9fPtME'
token = prd_token

logfilename = 'D:\\dev\\log\\prd\\'+str(datetime.datetime.today())[:10] +'.log'
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(logfilename),
        logging.StreamHandler()
    ]
)

def getUserList():
    test_db = pymysql.connect(user='admin',
                      passwd='se21121',
                       host = '211.232.156.57',
                      # host='127.0.0.1',
                      db='casereport',
                      charset='utf8')

    cursor = test_db.cursor(pymysql.cursors.DictCursor)
    sql = "SELECT user FROM users;"
    cursor.execute(sql)
    result = cursor.fetchall()
    arr = []
    for item in result :
        arr.append(item['user'])
    return arr

users = getUserList()

df = pd.DataFrame(columns=(['일자','시간','종가']))
df10 = loadmkt.read_ktb10y()
df3 = loadmkt.read_ktb3y()
dfktbsp = loadmkt.read_ktbsp()
# dfhanmi = loadmkt.read_hanmi()
df10 = loadmkt.update_futures_rt(df10, fut_name='10y')
df3 = loadmkt.update_futures_rt(df3, fut_name='3y')
dfktbsp = loadmkt.update_futures_rt(dfktbsp, fut_name='sp')
#%%
bot = telegram.Bot(token)
updates = bot.getUpdates()

#updater
updater = Updater(token=token, use_context=True)
dispatcher = updater.dispatcher


caseList = ['10년입찰','30년입찰','3년입찰','5년입찰','금통위']
assetList = ['국채3년','국채10년', '3선','10선','스플']
# caseList = ['AUCT30','AUCT10','AUCT5','AUCT3','미국10년입찰','미국5년입찰','분기첫날','금융위','분기첫날']
# assetList = ['KTB3Y','KTB5Y','LKTB','KTB20Y','KTB30Y','통안1년','통안1.5년','통안2년','KRWIRS1년','KRWIRS1.5년','KRWIRS2년','KRWIRS3년','KRWIRS5년','KRWIRS10년','KRWIRS20년','KRWIRS30년',
#              '미국채권2년','미국채권5년','미국채권10년','미국채권30년','금융채AAA1년','금융채AAA1.5년','금융채AAA2년','금융채AA+1년','금융채AA+1.5년','금융채AA+2년',
#              '국채10년-국채3년','국채10년-국채5년','국채30년-국채10년','국채30년-국채20년','2X국채5년-국채3년-국채10년','2X국채10년-국채3년-국채30년','2X국채10년-국채5년-국채30년',
#              'KRWIRS2년-통안증권2년','KRWIRS3년-통안증권3년','KRWIRS5년-통안증권5년','미국채권10년-국채10년','미국채권10년-미국채권2년','미국채권30년-미국채권5년','미국채권30년-미국채권10년',
#              '2X미국채권5년-미국채권2년-미국채권10년','2X미국채권10년-미국채권5년-미국채권30년','금융채AAA1.5년-통안증권1.5년','금융채AAA2년-통안증권2년','금융채AA+1년-통안증권1년','금융채AA+1.5년-통안증권1.5년','금융채AA+2년-통안증권2년']

#command handler
def start(update, context):
    logging.info('/start '+str(update.effective_chat.id))
    context.bot.send_message(chat_id=update.effective_chat.id, text ="/help : 사용법 보기\n/cases : 이벤트 리스트 보기\n/assets : 자산 리스트 보기")
    
def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text ="이벤트 종목 오프셋 최근날자들수 이전날들 이후날들\n(이벤트는 필수입력, 종목은 옵션이되 입력없으면 3선,10선,스플. 나머지는 기본값 각 0, 6, -3, 2)\n을 타이핑 하시면 차트 이미지가 로드됩니다.\n/cases 와 /assets 에서 이벤트, 종목 참조 가능\n예) 10년입찰 10선 -1")
    
def cases(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text ='\n'.join(caseList))

def assets(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text ='\n'.join(assetList))
    
#message handler
def echo(update, context):
    user_id = update.effective_chat.id
    logging.info(f'{user_id} /echo {update.message.text}')
    
    if user_id not in users:
        context.bot.send_message(chat_id=update.effective_chat.id, text="회원 가입을 위해 관리자에게 연락해 주세요")
        return
    
    user_text = ' '.join(update.message.text.split())
    texts= user_text.split(' ')
    
    case = ''
    asset = 'ALL'
    offset = 0
    series = 6
    _prev = -3
    _next = 2
    
    for i, item in enumerate(texts):
        if i == 0 :
            if item in caseList :
                if item in '10년입찰' :
                    case = 'AUCT10'
                elif item in '30년입찰' :
                    case = 'AUCT30'
                elif item in '3년입찰' :
                    case = 'AUCT3'
                elif item in '5년입찰' :
                    case = 'AUCT5'
                elif item in '금통위' :
                    case = 'BOKMPC'
            else :
                context.bot.send_message(chat_id=update.effective_chat.id, text="/cases list에 있는 이벤트를 입력해 주세요")
                return
        if i == 1 : 
            if item in assetList :
                if item in ['국채3년','3선'] :
                    asset = 'KTBF3Y'
                    df = df3
                elif item in ['국채10년','10선'] :
                    asset = 'KTBF10Y'
                    df = df10
                elif item in ['스플']:
                    asset = 'SP'
                    df = dfktbsp
            elif int(item) in [-3,-2,-1,0,1,2,3] :
                asset = 'ALL'
                offset = int(item)
            else :
                context.bot.send_message(chat_id=update.effective_chat.id, text="두번째 매개변수로 /assets list에 있는 종목이나 -3~3사이의 정수 offset을 입력해 주세요")
                return
        if i == 2 and asset != 'ALL':
            offset = int(item)
        elif i == 2 :
            series = int(item)
        if i == 3 and asset != 'ALL':
            series = int(item)
        if i == 4 and asset != 'ALL':
            _prev = int(item)
        if i == 5 and asset != 'ALL':
            _next = int(item)

    if asset == 'ALL' :
        for item in ['KTBF3Y', 'KTBF10Y', 'SP']:
            if item == 'KTBF3Y':
                df = df3
            elif item == 'KTBF10Y':
                df = df10
            elif item == 'SP':
                df = dfktbsp
            filename = f'{case}_{item}_{series}series_{offset}off_{_prev}prev_{_next}next.jpg'
            logging.info(f'{update.effective_chat.id} /echo_all {filename}')
            # logging.info('/echo_all '+str(update.effective_chat.id)+' '+filename)
            auct_intra.setPlot(df, case, item, offset, series, _prev, _next)
            context.bot.send_photo(chat_id=update.effective_chat.id, photo = open('D:\\dev\\case_data\\'+filename,'rb'))
    else :
        filename = f'{case}_{asset}_{series}series_{offset}off_{_prev}prev_{_next}next.jpg'
        logging.info(f'{update.effective_chat.id} /echo {filename}')
        # logging.info('/echo '+str(update.effective_chat.id)+' '+filename)
            
        # context.bot.send_message(chat_id=update.effective_chat.id, text=filename)
        auct_intra.setPlot(df, case, asset, offset, series, _prev, _next)
        context.bot.send_photo(chat_id=update.effective_chat.id, photo = open('D:\\dev\\case_data\\'+filename,'rb'))
  
start_handler = CommandHandler('start',start)
usage_handler = CommandHandler('help',help)
cases_handler = CommandHandler('cases',cases)
assets_handler = CommandHandler('assets',assets)
echo_handler = MessageHandler(Filters.text & (~Filters.command), echo)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(usage_handler)
dispatcher.add_handler(cases_handler)
dispatcher.add_handler(assets_handler)
dispatcher.add_handler(echo_handler)

updater.start_polling()