import ccxt
from ccxt.base import precise

from ccxt.binance import binance
from ccxt.upbit import upbit
from ccxt.coinbasepro import coinbasepro
from ccxt.bithumb import bithumb
from ccxt.ftx import ftx

import re
import random
import time

from matplotlib.pyplot import pause

upbit = ccxt.upbit({'enableRateLimit': False})
binance = ccxt.binance({'enableRateLimit': False})
coinbasepro = ccxt.coinbasepro({'enableRateLimit': False})
bithumb = ccxt.bithumb({'enableRateLimit': False})
ftx = ccxt.ftx({'enableRateLimit': False})

upbitmarkets = list()
binancemarkets = list()
coinbasepromarkets = list()
bithumbmarkets = list()
ftxmarkets = list()

upbitmarkets.append(upbit.load_markets())
binancemarkets.append(binance.load_markets())
coinbasepromarkets.append(coinbasepro.load_markets())
bithumbmarkets.append(bithumb.load_markets())
ftxmarkets.append(ftx.load_markets())

#빗썸 ftx

SymbolList = {}
RefinedMarkets = {}
MarketList = ['Upbit_KRW','Binance_USDT','Binance_BUSD','Coinbasepro_USDT','Bithumb_KRW','Ftx_USD']
Ticker_Exception = ['XNO']
            
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
                
            elif index == 'Binance_BUSD':
                for mktName in market.keys() :
                    if mktName.endswith("/BUSD") :
                        name = re.sub("/BUSD", "", mktName)
                        argsList.append(name)
                    SymbolList[index] = argsList

def Get_Coinbasepro_Markets() : 
    for market in coinbasepromarkets :
        argsList = list()
        for index in MarketList :
            if index == 'Coinbasepro_USDT':
                for mktName in market.keys() :
                    if mktName.endswith("/USDT") :
                        name = re.sub("/USDT", "", mktName)
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

def Get_Ftx_Markets():
    for market in ftxmarkets :
        argsList = list()
        for index in MarketList :
            if index == 'Ftx_USD':
                for mktName in market.keys() :
                    if mktName.endswith("/USD") :
                        name = re.sub("/USD", "", mktName)
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

def Fetch_Market_Ticker(MarketTicker) :
    if len(RefinedMarkets[MarketTicker]) > 2 :
        resultDict[MarketTicker] = {}
        for MarketName in RefinedMarkets[MarketTicker] :
            try :
                if MarketName == 'Upbit_KRW' :
                    resultDict[MarketTicker]['Upbit_KRW'] = upbit.fetch_ticker(MarketTicker + '/KRW')['close'] / TetherPrice
                        
                elif MarketName == 'Binance_USDT' :
                    resultDict[MarketTicker]["Binance_USDT"] = binance.fetch_ticker(MarketTicker + '/USDT')['close']
                        
                elif MarketName == 'Binance_BUSD' :
                    resultDict[MarketTicker]["Binance_BUSD"] = binance.fetch_ticker(MarketTicker + '/BUSD')['close']

                elif MarketName == 'Coinbasepro_USDT' :
                    resultDict[MarketTicker]["Coinbasepro_USDT"] = coinbasepro.fetch_ticker(MarketTicker + '/USDT')['close']
                
                elif MarketName == 'Bithumb_KRW' :
                    resultDict[MarketTicker]['Bithumb_KRW'] = bithumb.fetch_ticker(MarketTicker + '/KRW')['close'] / TetherPrice
                
                elif MarketName == 'Ftx_USD' :
                    resultDict[MarketTicker]["Ftx_USD"] = ftx.fetch_ticker(MarketTicker + '/USD')['close']
                    
                else :
                    continue
            except :
                continue
            

Get_Upbit_Markets()
Get_Binance_Markets()
Get_Coinbasepro_Markets()
Get_Bithumb_Markets()
Get_Ftx_Markets()
Refine_Market()

while True :
    start = time.time()
    print("-----------------------------------------")
    resultDict = {}
    
    TetherPrice = Get_Tether_Price()
    
    for MarketTicker in RefinedMarkets :
        Fetch_Market_Ticker(MarketTicker)
    
    for ticker, valueList in resultDict.items() :
        #Ticker exception
        if ticker in Ticker_Exception :
            continue
        
        #remove nonetype data in valuelist
        for x in list(valueList) :
            if valueList[x] == None :
                valueList.pop(x)
        
        maxValue = max(valueList.values())
        maxValue_key = max(valueList, key=valueList.get)
        minValue = min(valueList.values())
        minValue_key = min(valueList, key=valueList.get)
        
        if maxValue-minValue ==  0 or minValue == 0 :
            gap = 0
        
        else :
            gap = ((maxValue/minValue) - 1) * 100
         
        if abs(gap) > 5 :
            print(ticker, " 5% 이상 차이", "(",round(gap, 3), " %)" + " | " + minValue_key + " <-> " + maxValue_key)
        elif abs(gap) > 3 :
            print(ticker, " 3% 이상 차이 ", "(",round(gap, 3), " %)" + " | " + minValue_key + " <-> " + maxValue_key)
        elif abs(gap) > 1 :
            print(ticker, " 1% 이상 차이 ", "(",round(gap, 3), " %)" + " | " + minValue_key + " <-> " + maxValue_key)
        
    
    print("\n시행 완료, 소요시간 (", round(time.time() - start, 1), "초)")
    now = time.localtime()
    print ("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))

   