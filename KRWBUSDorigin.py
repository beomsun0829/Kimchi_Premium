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

markets = list()
markets.append(upbit.load_markets())
markets.append(binance.load_markets())
USDTMarkets = {}
marketList = ['upbit','binance']

i = 0 
for market in markets :
    argsList = list()
    if i == 1:
        for mktName in market.keys() :
            if '/BUSD' in mktName :
                name = re.sub("/BUSD", "", mktName)
                argsList.append(name)
        USDTMarkets[marketList[i]] = argsList
        for mktName in market.keys() :
            if '/USDT' in mktName :
                name = re.sub("/USDT", "", mktName)
                argsList.append(name)
        USDTMarkets[marketList[i]] = argsList
    elif (i == 0) : 
        for mktName in market.keys() :
            if '/KRW' in mktName :
                name = re.sub("/KRW", "", mktName)
                argsList.append(name)
        USDTMarkets[marketList[i]] = argsList
    i = i+1

TickerNumDict = {}
for marketNAME, marketTickerList in USDTMarkets.items() :
    for TickerName in marketTickerList :
        if TickerName in TickerNumDict :
            TickerNumDict[TickerName] = TickerNumDict[TickerName] + 1
        else :
            TickerNumDict[TickerName] = 1

refinedUSDTMarkets = {}
for marketName, marketTickerList in USDTMarkets.items() :
    argsList = list()
    for TickerName in marketTickerList :
        if(TickerNumDict[TickerName] >= 2) :
            argsList.append(TickerName)
    refinedUSDTMarkets[marketName] = argsList



upbitMT = list()
binanMT = list()
upbitMT = refinedUSDTMarkets['upbit']
binanMT = refinedUSDTMarkets['binance']

Market_Ticker_List = list()
for i in range(0, len(upbitMT)) :
    MarketTicker = list()
    MarketTicker = ['upbit', upbitMT[i]]
    Market_Ticker_List.append(MarketTicker)
    MarketTicker = ['binance', binanMT[i]]
    Market_Ticker_List.append(MarketTicker)

print(Market_Ticker_List)

while True :
    start = time.time()
    print("-----------------------------------------")
    print("\n")
    resultDict = {}
    
    for marketTicker in Market_Ticker_List :
        if(marketTicker[0] == 'upbit') :
            ticker = upbit.fetch_ticker(marketTicker[1]+'/KRW')
            print(marketTicker[1])
            tickerDict = {}
            name = marketTicker[1]
            if name in resultDict :
                tickerDict = resultDict[name]
                tickerDict[marketTicker[0]] = ticker['close'] * 0.000818
                resultDict[name] = tickerDict
            else :
                resultDict[name] = {marketTicker[0] : ticker['close'] * 0.000818}
            time.sleep(0.1)
        elif(marketTicker[0] == 'binance') :
            ticker = binance.fetch_ticker(marketTicker[1]+'/BUSD')
            tickerDict = {}
            name = marketTicker[1]
            if name in resultDict :
                tickerDict = resultDict[name]
                tickerDict[marketTicker[0]] = ticker['close']
                resultDict[name] = tickerDict
            else :
                resultDict[name] = {marketTicker[0] : ticker['close']}
        elif(marketTicker[0] == 'binance') :
            ticker = binance.fetch_ticker(marketTicker[1]+'/USDT')
            tickerDict = {}
            name = marketTicker[1]
            if name in resultDict :
                tickerDict = resultDict[name]
                tickerDict[marketTicker[0]] = ticker['close']
                resultDict[name] = tickerDict
            else :
                resultDict[name] = {marketTicker[0] : ticker['close']}

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
