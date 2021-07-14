import telegram
import datetime
from telegram.ext import Updater
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters
import pymysql

test_token = '1767824468:AAFBSQzCNlzKCKVqYK7HlwqUlzDNqBibVdM'
# prd_token = '1721072898:AAHowGdDffQr-44g0xkHAq_-YlinO9fPtME'
token = test_token

bot = telegram.Bot(token)
updates = bot.getUpdates()


test_db = pymysql.connect(user='admin',
                      passwd='se21121',
                       host = '211.232.156.57',
                      # host='127.0.0.1',
                      db='casereport',
                      charset='utf8')

cursor = test_db.cursor(pymysql.cursors.DictCursor)

def getUserList():
    sql = "SELECT user FROM users;"
    cursor.execute(sql)
    result = cursor.fetchall()
    arr = []
    for item in result :
        arr.append(item['user'])
    return arr

# users = [1381723672, 42114728]
# users = getUserList()
# print(updates[0].message.chat_id)
# for u in updates:
#     if u is not None :
#         # print(u[0].message.chat_id)
#         bot.sendMessage(chat_id = u.message.chat_id, text='서버 점검이 있었습니다. /start 로 시작해 보아요')


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
    print(datetime.datetime.now(), update.effective_chat.id)
    context.bot.send_message(chat_id=update.effective_chat.id, text ="/help : 사용법 보기\n/cases : 이벤트 리스트 보기\n/assets : 자산 리스트 보기")
    
def help(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text ="이벤트 종목 오프셋 최근날자들수 이전날들 이후날들\n(이벤트,종목은 필수입력, 나머지는 기본값 각 0, 6, -3, 2)\n을 타이핑 하시면 차트 이미지가 로드됩니다.\n/cases 와 /assets 에서 이벤트, 종목 참조 가능\n예) 10년입찰 10선 -1")
    
def cases(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text ='\n'.join(caseList))

def assets(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text ='\n'.join(assetList))
    
#message handler
def echo(update, context):
    user_id = update.effective_chat.id
    users = getUserList()
    if user_id not in users:
        return
    
    user_text = ' '.join(update.message.text.split())
    texts= user_text.split(' ')
    
    case = ''
    asset = 'ALL'
    offset = 0
    series = 6
    _prev = -3
    _next = 2
    
    # if len(texts) < 2 :
    #     context.bot.send_message(chat_id=update.effective_chat.id, text="적어도 case와 asset 두 단어는 넣어 주셔야 합니다.")
    
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
        if i == 1 : 
            if item in assetList :
                if item in ['국채3년','3선'] :
                    asset = 'KTBF3Y'
                elif item in ['국채10년','10선'] :
                    asset = 'KTBF10Y'
                elif item in ['스플']:
                    asset = 'SP'
            elif int(item) in [-3,-2,-1,0,1,2,3] :
                asset = 'ALL'
                offset = int(item)
            else :
                context.bot.send_message(chat_id=update.effective_chat.id, text="/assets list에 있는 종목이나 offset을 입력해 주세요")
        if i == 2 and asset != 'ALL':
            offset = int(item)
        elif i == 2 :
            series = int(item)
            # else : 
            #     context.bot.send_message(chat_id=update.effective_chat.id, text="offset 정수를 입력해 주세요(기본값:0)")
        if i == 3 and asset != 'ALL':
            series = int(item)
            # else : 
            #     context.bot.send_message(chat_id=update.effective_chat.id, text="series를 정수로 입력해 주세요(기본값:5)")
        if i == 4 and asset != 'ALL':
            _prev = int(item)
            # else : 
            #     context.bot.send_message(chat_id=update.effective_chat.id, text="prev 정수를 입력해 주세요(기본값:-5)")
        if i == 5 and asset != 'ALL':
            _next = int(item)
            # else : 
                # context.bot.send_message(chat_id=update.effective_chat.id, text="next 정수를 입력해 주세요(기본값:5)")

    if asset == 'ALL' :
        for item in ['KTBF3Y', 'KTBF10Y', 'SP']:
            filename = f'{case}_{item}_{series}series_{offset}off_{_prev}prev_{_next}next.jpg'
            print(datetime.datetime.now(), user_id, filename)
            context.bot.send_photo(chat_id=update.effective_chat.id, photo = open('D:\\dev\\data\\'+filename,'rb'))
    else :
        filename = f'{case}_{asset}_{series}series_{offset}off_{_prev}prev_{_next}next.jpg'
        print(datetime.datetime.now(), user_id, filename)
        # context.bot.send_message(chat_id=update.effective_chat.id, text=filename)
        context.bot.send_photo(chat_id=update.effective_chat.id, photo = open('D:\\dev\\data\\'+filename,'rb'))
    
    # user_text = '사용법은 /start 로 참고해 주세요'
    # # print(user_id, user_text)
    # context.bot.send_message(chat_id=user_id, text=user_text)


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