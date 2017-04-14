import time, json, sys, math, urllib.request

class Wallet():

    def __init__(self):
        with open('data.json', 'r+') as file: #open file
            try:
                data = json.load(file) # read file
                self.cash = data["userdata"]["wallet"]
            except ValueError:
                raise ValueError('Cannot read JSON file')

    def buy(self, ID, askPrice):
        obj = ShareObj(ID)
        obj.refresh()

        with open('data.json', 'r+') as file:
            try:
                data = json.load(file) # read file
            except json.decoder.JSONDecodeError:
                print('Error loading JSON - Check your JSON file')
                sys.exit(0)

            if(self.cash > float(askPrice)): #if you have sufficient funds
                movingAvgPercentDifference = (math.fabs(float(obj.getFiftyDay()) - float(obj.getTwoHunDay()))/((float(obj.getFiftyDay()) + float(obj.getTwoHunDay()))/2))*100
                if (float(self.numOwned(obj.getID(), data)) >= math.floor(movingAvgPercentDifference)):
                    print("Number of",obj.getID(),"shares owned is greater than or equal to the percent difference of the 50/200 day moving average and therefore will not be bought.")
                else:
                    file.seek(0)
                    file.truncate()

                    try: #to allow for multiple shares to be done you could like set a variable of percent change in the json, read that. if that *= 0.05 isn't less that the current percent change, don't buy again
                        data["shares"].append({ # add new price to appropriate id
                            "id": obj.getID(),
                            "time": time.strftime("%H:%M:%S"),
                            "change": obj.getChange()
                        })

                    except AttributeError: # uh oh!!! that ID doesnt exist yet!! just create it :)
                        data['shares'].append({
                            "id": obj.getID(),
                            "time": time.strftime("%H:%M:%S"),
                            "change": obj.getChangeFormatted()
                        })

                    data = str(data).replace("'", '"')

                    file.write(data)
                    file.close()

                    self.setCash(self.cash - float(price)) #buy that shit
                    self.writeCash()
            else:
                print("Insufficient funds")

    def sell(self, ID, bidPrice):
        obj = ShareObj(ID)
        obj.refresh()

        with open('data.json', 'r+') as file: # open file
            try:
                data = json.load(file) # read file
            except json.decoder.JSONDecodeError:
                print("Error - Check JSON file!") # error check -- json file error
                sys.exit(0)

            file.seek(0) # wipe file
            file.truncate()

            if (self.numOwned(obj.getID(), data) == 0):
                print("["+time.strftime("%H:%M:%S")+"] ["+ ID +"] [SELL] Share Not Owned")

                data = str(data).replace("'", '"') # clean up json

                file.write(data)# write to json
                file.close() # close json

                return

            shareAmount = [] # list of indexes of items to be removed

            for i in range(self.numOwned(obj.getID(), data)):
                if(data["shares"][i]["id"] == obj.getID()): #c reate list of indexes of shares to be removed and sold
                    shareAmount.insert(0,i)

            for i in range(len(shareAmount)):
                del data["shares"][shareAmount[i]] # sell all shares of id

            data = str(data).replace("'", '"') # clean up json

            file.write(data)# write to json
            file.close() # close json

            self.setCash(self.cash + (float(bidPrice) * int(len(shareAmount))))
            self.writeCash()

    def getCash(self):
        return self.cash

    def setCash(self, value):
        self.cash = value

    def writeCash(self):
        with open('data.json', 'r+') as file: #open file
            try:
                data = json.load(file) # read file
                data["userdata"]["wallet"] = self.cash
            except ValueError:
                raise ValueError('Cannot read JSON file')

            file.seek(0)
            file.truncate()

            data = str(data).replace("'", '"')

            file.write(data)
            file.close()

    def numOwned(self, ID, data):
        numOwned = 0
        with open('data.json', 'r+') as file: # open file
            for i in range(0,len(data["shares"])): #for the amount of shares recorded in json file
                try:
                    if(data["shares"][i]["id"] == ID): #checks if valid id, as in, does this share exist in the JSON?
                        numOwned += 1
                except AttributeError: #if error, report it
                    print("ERROR - numOwned - share ID doesn't exist.")
                    return 0
        return numOwned

class ShareObj(object):
    def __init__(self, ID):
        self.id = ID
        self.refresh()

    def getBuyPrice(self):
        self.refresh()
        while(self.bprice == None):
            self.refresh()
        return self.bprice

    def getSellPrice(self):
        self.refresh()
        while(self.sprice == None):
            self.refresh()
        return self.sprice

    def getFiftyDay(self):
        return self.fiftyDay

    def getTwoHunDay(self):
        self.refresh()
        return self.twoHunDay

    def getChangeFormatted(self):
        self.refresh()
        return self.changeF

    def getID(self):
        return self.id

    def refresh(self):
        urlStr = "https://query.yahooapis.com/v1/public/yql?q=select%20*%20from%20yahoo.finance.quotes%20where%20symbol%20in%20(\""+self.id+"\")&format=json&env=store%3A%2F%2Fdatatables.org%2Falltableswithkeys&callback="
        with urllib.request.urlopen(urlStr) as url:
            data = json.loads(url.read().decode())
            if data["query"]["results"]["quote"]["Ask"] is None:
                self.refresh()
            else:
                self.bprice = float(data["query"]["results"]["quote"]["Ask"])

            if data["query"]["results"]["quote"]["Bid"] is None:
                self.refresh()
            else:
                self.sprice = float(data["query"]["results"]["quote"]["Bid"])

            self.changeF = str(data["query"]["results"]["quote"]["PercentChange"])
            self.fiftyDay = float(data["query"]["results"]["quote"]["FiftydayMovingAverage"])
            self.twoHunDay = float(data["query"]["results"]["quote"]["TwoHundreddayMovingAverage"])

try:
    w = Wallet()
    f = open('output.txt', 'w')
    bought = 0
    stocksToWatch = ["TSLA", "FB", "MSFT", "AMZN", "GOOG"] #shares to cycle through
    reps = 1440
    while(reps > 0):
        for i in stocksToWatch:
            shre = ShareObj(i)
            shre.refresh()

            strToWrite = "["+time.strftime("%H:%M:%S")+"] [WALLET] $%.2f\t" % w.getCash()

            print(strToWrite)
            f.write("\n"+strToWrite)

            strToWrite = "["+time.strftime("%H:%M:%S")+"] [SHARE] ["+shre.getID()+"] [50DAY] "+str(shre.getFiftyDay())+" [200DAY] "+str(shre.getTwoHunDay())

            print(strToWrite)
            f.write("\n"+strToWrite)

            if(shre.getFiftyDay() >= shre.getTwoHunDay()):
                price = shre.getBuyPrice()

                strToWrite = "["+time.strftime("%H:%M:%S")+"] [SHARE] ["+ shre.getID() +"] [BUY] "+str(price)

                print(strToWrite)
                f.write("\n"+strToWrite)
                bought+=price
                w.buy(shre.getID(), price)

            elif(shre.getFiftyDay() <= shre.getTwoHunDay()):
                price = shre.getSellPrice()

                strToWrite = "["+time.strftime("%H:%M:%S")+"] [SHARE] ["+ shre.getID() +"] [SELL] "+str(price)

                print(strToWrite)
                f.write("\n"+strToWrite)

                w.sell(shre.getID(), price)

            else:
                strToWrite = "["+time.strftime("%H:%M:%S")+"] [SHARE] ["+ shre.getID() +"] [N/A] [CHANGE] <"+str(percentChange)
                print(strToWrite)

            print("\n")
        reps -= 1
        time.sleep(60) # wait a minute

    f = open('final.txt', 'w') #i just want to clarify the final total, so therefore am putting final wallet output in a seperate file

    for i in stocksToWatch:
        shre = ShareObj(i)
        shre.refresh()

        price = shre.getSellPrice()
        w.sell(shre.getID(), price)
        print("["+time.strftime("%H:%M:%S")+"] ["+ shre.getID() +"] [SELLING AT] "+str(price))

    strToWrite = "Final total: "+ str(w.getCash())

    print(strToWrite)
    f.write("\n"+strToWrite)

except KeyboardInterrupt: # If i hit control+C and stop the script, It will still write final data
    f = open('final.txt', 'w') #i just want to clarify the final total, so therefore am putting final wallet output in a seperate file
    sold = 0
    for i in stocksToWatch:
        shre = ShareObj(i)
        shre.refresh()

        price = shre.getSellPrice()
        sold +=price
        w.sell(shre.getID(), price)
        print("["+time.strftime("%H:%M:%S")+"] ["+ shre.getID() +"] [SELLING AT] "+str(price))

    strToWrite = "Final total: "+ str(w.getCash())
    print(bought,sold,bought-sold)
    print(strToWrite)
    f.write("\n"+strToWrite)
