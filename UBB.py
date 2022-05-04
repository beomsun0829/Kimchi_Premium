import ccxt
from ccxt.base import precise

from ccxt.binance import binance
from ccxt.upbit import upbit
from ccxt.bithumb import bithumb
import requests

import re
import random
import time
import os
from dotenv import load_dotenv
load_dotenv(verbose=True)
import telegram
import config

from matplotlib.pyplot import pause
binance = ccxt.binance({'enableRateLimit': False})
upbit = ccxt.upbit({'enableRateLimit': False})
bithumb = ccxt.bithumb({'enableRateLimit': False})

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
CHAT_ID = os.getenv('CHAT_ID')
bot = telegram.Bot(token=TELEGRAM_TOKEN)

binancemarkets = list()
upbitmarkets = list()
bithumbmarkets = list()

binancemarkets.append(binance.load_markets())
upbitmarkets.append(upbit.load_markets())
bithumbmarkets.append(bithumb.load_markets())

SymbolList = {}
RefinedMarkets = {}

MarketList = ['Binance_USDT','Upbit_KRW','Bithumb_KRW']
Ticker_Exception = config.TICKER_EXCEPTION
print(Ticker_Exception)


def Get_Binance_Markets() :
    for market in binancemarkets :
        argsList = list()
        for index in MarketList :
            if index == 'Binance_USDT':
                for mktName in market.keys() :
                    if mktName.endswith("/USDT") :
                        name = re.sub("/USDT", "", mktName)
                        argsList.append(name)
                    SymbolList[index] = argsList

def Get_Upbit_Markets() :
    for market in upbitmarkets : 
        argsList = list()
        for index in MarketList :
            if index == 'Upbit_KRW' : 
                for mktName in market.keys() :
                    if mktName.endswith("/KRW") :
                        name = re.sub("/KRW", "", mktName)
                        argsList.append(name)
                SymbolList[index] = argsList

def Get_Bithumb_Markets() : 
    for market in bithumbmarkets :
        argsList = list()
        for index in MarketList :
            if index == 'Bithumb_KRW':
                for mktName in market.keys() :
                    if mktName.endswith("/KRW") :
                        name = re.sub("/KRW", "", mktName)
                        argsList.append(name)
                    SymbolList[index] = argsList

def Refine_Market() :
    for MarketName , MarketTickerList in SymbolList.items() :
        for ticker in MarketTickerList :
            if ticker in RefinedMarkets.keys() :
                if MarketName in RefinedMarkets[ticker] :
                    continue
                RefinedMarkets[ticker].append(MarketName)
            else :
                RefinedMarkets[ticker] = [MarketName]
                
def Get_Tether_Price() :
    KRW_BTC = upbit.fetch_ticker('BTC/KRW')
    BTC_USDT = upbit.fetch_ticker('BTC/USDT')
    return KRW_BTC['last'] / BTC_USDT['last']

def Get_BTC_Price() :
    return binance.fetch_ticker('BTC/USDT')['close']

def Fetch_Market_Ticker(MarketTicker) :
    BTC_USDT = Get_BTC_Price()
    if len(RefinedMarkets[MarketTicker]) > 1 :
        resultDict[MarketTicker] = {}
        for MarketName in RefinedMarkets[MarketTicker] :
            try :
                if MarketName == 'Binance_USDT' :
                    resultDict[MarketTicker]["Binance_USDT"] = binance.fetch_ticker(MarketTicker + '/USDT')['close']
                elif MarketName == 'Upbit_KRW' :
                    resultDict[MarketTicker]['Upbit_KRW'] = upbit.fetch_ticker(MarketTicker + '/KRW')['close'] / TetherPrice
                elif MarketName == 'Bithumb_KRW' :
                    resultDict[MarketTicker]['Bithumb_KRW'] = bithumb.fetch_ticker(MarketTicker + '/KRW')['close'] / TetherPrice

                else :
                    continue
            except :
                continue

def Send_Telegram(message) :
    bot.send_message(chat_id=CHAT_ID, text=message)

Get_Binance_Markets()
Get_Upbit_Markets()
Get_Bithumb_Markets()

Refine_Market()

while True :
    message = ""
    counter = 0
    start = time.time()
    resultDict = {}
    
    TetherPrice = Get_Tether_Price()
    
    for MarketTicker in RefinedMarkets :
        Fetch_Market_Ticker(MarketTicker)
    
    for ticker, valueList in resultDict.items() :
        #Ticker exception
        if ticker in Ticker_Exception :
            continue
        
        #remove nonetype data in valuelistS
        for x in list(valueList) :
            if valueList[x] == None :
                valueList.pop(x)
                
        if len(valueList) == 0 :
            continue
        
        maxValue = max(valueList.values())
        maxValue_key = max(valueList, key=valueList.get)
        minValue = min(valueList.values())
        minValue_key = min(valueList, key=valueList.get)
        
        if maxValue-minValue ==  0 or minValue == 0 :
            gap = 0
        
        else :
            gap = ((maxValue/minValue) - 1) * 100
        
        if minValue_key[:5] == 'Upbit' and maxValue_key[:7] == 'Bithumb' :
            continue
        elif minValue_key[:7] == 'Bithumb' and maxValue_key[:5] == 'Upbit' :
            continue
        elif abs(gap) > 3 :
            message += (ticker + " | 3% 이상 차이 " + "( " + str(round(gap, 3)) + " % )" + " | " + minValue_key + " -> " + maxValue_key + "\n")
            counter = counter + 1
        elif abs(gap) > 1.5 :
            message += (ticker + " | 1.5% 이상 차이 " + "( " + str(round(gap, 3)) + " % )" + " | " + minValue_key + " -> " + maxValue_key + "\n")
            counter = counter + 1
    
    if counter > 0:
    
        print("\n시행 완료, 소요시간 (" + str(round(time.time() - start, 1)) +  "초)" + "\n")
        now = time.localtime()
        print("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec) + "\n")
        
        message += ("Tether Price : " + str(round(TetherPrice,3)) + "\n")
        Send_Telegram(message)
        print(message)
    
    else :
        print("\n시행 완료, 소요시간 (" + str(round(time.time() - start, 1)) +  "초)" + "\n")
    
   
