from yahoo_finance import Share
import time, json

class Wallet():

    def __init__(self):
        self.cash = 10000 #digital fake cash for simulation purposes

    def checkIfIn(self, ID):
        with open('data.json', 'r+') as file:
            data = json.load(file) # load in json file

            try:
                str = data["shares"][ID]
                return True #if ID exists in json file, return True
            except KeyError:
                return False# if ID does not exist in json file, return False

    def buy(self, ID):
        obj = ShareObj(ID)
        obj.refresh() # update prices

        if(self.checkIfIn(ID) == False): # if share is not already in portfolio
            self.cash -= float(obj.getPrice()) #subtract from digital wallet
            with open('data.json', 'r+') as file: #and update json to reflect stock purchase
                # read file
                data = json.load(file)
                # wipe file
                file.seek(0)
                file.truncate()

                # add new price to appropriate id
                data["shares"].append({
                    "id": obj.getID(),
                    "price": obj.getPrice()
                })

                data = str(data).replace("'", '"')

                file.write(data) #write
                file.close()

    def sell(self, ID):
        obj = ShareObj(ID)
        obj.refresh()

        self.cash += float(obj.getPrice())

    def getCash(self):
        return self.cash

class ShareObj(object):
    def __init__(self, ID):
        self.id = ID
        self.share = Share(self.id)

    def getPrice(self):
        return self.share.get_price()

    def getOpenPrice(self):
        return self.share.get_open()

    def getChange(self):
        percent = self.share.get_percent_change()
        return percent[:-1]

    def getChangeFormatted(self):
        self.share.get_percent_change()

    def getID(self):
        return self.id

    def setID(self, newID):
        self.id = newID
        self.refresh()

    def refresh(self):
        self.share.refresh()

w = Wallet()
shr = ShareObj("TSLA")

percentChange = 0.15

print("Initializing...\n")

while(True):
    print("Wallet:\t\t\t",w.getCash())
    print("Percent Change:\t\t", shr.getChange(),"\n")

    if(float(shr.getChange()) >= percentChange):
        print("Buy")
        print("Wallet before buy:\t",w.getCash())
        w.buy(shr.getID())
        print("Wallet after buy:\t",w.getCash())
    elif(float(shr.getChange()) <= (-1*percentChange)):
        print("Sell")
        print("Waller before sell:\t",w.getCash())
        w.sell(shr.getID())
        print("Wallet before sell:t\t",w.getCash())
    else:
        print("Do Nothing")
    print("\n")
    shr.refresh
    time.sleep(10)
