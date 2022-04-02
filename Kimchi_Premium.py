import ccxt
from ccxt.base import precise
from ccxt.binance import binance
from ccxt.upbit import upbit
import re
import random
import time

from matplotlib.pyplot import pause

upbit = ccxt.upbit()
binance = ccxt.binance()

upbit = ccxt.upbit({'enableRateLimit': False})
binance = ccxt.binance({'enableRateLimit': False})

upbitmarkets = list()
binancemarkets = list()
upbitmarkets.append(upbit.load_markets())
binancemarkets.append(binance.load_markets())


SymbolList = {}
RefinedMarkets = {}
MarketList = ['Upbit_KRW','Binance_USDT','Binance_BUSD']
            
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
                        
                else :
                    continue
            except :
                continue

Get_Upbit_Markets()
Get_Binance_Markets()
Refine_Market()

while True :
    start = time.time()
    print("-----------------------------------------")
    resultDict = {}
    
    TetherPrice = Get_Tether_Price()
    
    for MarketTicker in RefinedMarkets :
        Fetch_Market_Ticker(MarketTicker)
    
    for ticker, valueList in resultDict.items() :
        #search max value in valueList
        maxValue = max(valueList.values())
        maxValue_key = max(valueList, key=valueList.get)
        minValue = min(valueList.values())
        minValue_key = min(valueList, key=valueList.get)
        
        try :
            if(minValue > 0 and minValue != 10000) : 
                gap = (valueList['Upbit_KRW'] - minValue) / minValue * 100
                gapmarket = minValue_key
                
            elif(maxValue > 0 and maxValue != -10000) :
                gap = (valueList['Upbit_KRW'] - maxValue) / maxValue * 100
                gapmarket = maxValue_key
                
            else :
                gap = 0
    
        except (ZeroDivisionError, KeyError) :
            #print("ZeroDivisionError at" + ticker + "  " + str(valueList))
            continue
            
         
        if abs(gap) > 5 :
            print(ticker, " 5% 이상 차이", "(",round(gap, 3), " %)" + " | " + gapmarket)
        elif abs(gap) > 3 :
            print(ticker, " 3% 이상 차이 ", "(",round(gap, 3), " %)" + " | " + gapmarket)
        elif abs(gap) > 1 :
            print(ticker, " 1% 이상 차이 ", "(",round(gap, 3), " %)" + " | " + gapmarket)
        
    
    print("시행 완료, 소요시간 (", round(time.time() - start, 1), "초)")
    now = time.localtime()
    print ("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))

   