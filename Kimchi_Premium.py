import ccxt
from ccxt.base import precise
from ccxt.binance import binance
from ccxt.upbit import upbit
import re
import random
import time

upbit = ccxt.upbit()
binance = ccxt.binance()

upbit = ccxt.upbit({'enableRateLimit': False})
binance = ccxt.binance({'enableRateLimit': False})

upbitmarkets = list()
binancemarkets = list()
upbitmarkets.append(upbit.load_markets())
binancemarkets.append(binance.load_markets())
USDTMarkets = {}
KRWMarkets = {}
marketList = ['Upbit_KRW','Binance_USDT','Binance_BUSD']

for market in upbitmarkets : 
    argsList = list()
    for index in marketList :
        if index == 'Upbit_KRW' : 
            for mktName in market.keys() :
                if '/KRW' in mktName :
                    name = re.sub("/KRW", "", mktName)
                    argsList.append(name)
            KRWMarkets[index] = argsList

for market in binancemarkets :
    argsList = list()
    for index in marketList :
        if index == 'Binance_USDT':
            for mktName in market.keys() :
                if '/USDT' in mktName :
                    name = re.sub("/USDT", "", mktName)
                    argsList.append(name)
                USDTMarkets[index] = argsList
            
        elif index == 'Binance_BUSD':
            for mktName in market.keys() :
                if '/BUSD' in mktName :
                    name = re.sub("/BUSD", "", mktName)
                    argsList.append(name)
                USDTMarkets[index] = argsList

RefinedMarkets = {}
for marketName, marketTickerList in KRWMarkets.items() :
    for TickerName in marketTickerList :
        argsList = list()
        if(TickerName in USDTMarkets['Binance_USDT']) :
            argsList.append('Binance_USDT')
        if(TickerName in USDTMarkets['Binance_BUSD']) :
            argsList.append('Binance_BUSD')
    
        if(argsList != []) :
            RefinedMarkets[TickerName] = argsList


while True :
    start = time.time()
    print("-----------------------------------------")
    print("\n")
    
    resultDict = {"init" : {"init" : "init"}}
    
    KRW_BTC = upbit.fetch_ticker('BTC/KRW')
    BTC_USDT = upbit.fetch_ticker('BTC/USDT')
    TetherPrice = KRW_BTC['last'] / BTC_USDT['last']
    print("Tether Price : ", TetherPrice)
    
    
    for marketTicker in RefinedMarkets :
        if(1) :
            ticker = upbit.fetch_ticker(marketTicker +'/KRW')
            resultDict[marketTicker] = {"Upbit_KRW" : ticker['close']}
            time.sleep(0.03)
        
        if(RefinedMarkets[marketTicker][0] == 'Binance_USDT') :
            try :
                ticker = binance.fetch_ticker(marketTicker+'/USDT')
                resultDict[marketTicker]["Binance_USDT"] = ticker['close']
                time.sleep(0.03)
            except :
                print(marketTicker + "/USDT is not available")
        
        if(len(RefinedMarkets[marketTicker]) == 1):
            continue
        
        if(RefinedMarkets[marketTicker][1] == 'Binance_BUSD') :
            try :
                ticker = binance.fetch_ticker(marketTicker+'/BUSD')
                resultDict[marketTicker]["Binance_BUSD"] = ticker['close']
                time.sleep(0.03)
            except :
                print(marketTicker + "/BUSD is not available")
        
    print(resultDict)
            
    
    for ticker, valueList in resultDict.items() :
        minVal = 10000000.000
        minMarket = ""
        maxVal = -1.000
        maxMarket = ""
        for market, value in valueList.items() :
            if value is not None :
                if value < minVal :
                    minVal = value
                    minMarket = market
                if value > maxVal :
                    maxVal = value
                    maxMarket = market
        
        if maxVal > 1.05 * minVal and minVal != 0:
            print(ticker, " 5% 이상 차이", "(",round((maxVal/minVal - 1)*100, 2), " %)", "| ", minMarket,"(", round(minVal, 2),")",  "| ", maxMarket, "(", round(maxVal, 2),")","\n")
        elif maxVal > 1.03 * minVal and minVal != 0:
            print(ticker, " 3% 이상 차이 ", "(",round((maxVal/minVal - 1)*100, 2), " %)", "| ", minMarket, "(",round(minVal, 2),")",  "| ", maxMarket, "(", round(maxVal, 2),")","\n")
    
    print("시행 완료, 소요시간 (", round(time.time() - start, 1), "초)")
    now = time.localtime()
    print ("%04d/%02d/%02d %02d:%02d:%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec))

   