from yahoo_finance import Share
import time, json

class Wallet():

    def __init__(self):
        self.cash = 10000

    def buy(self, ID):
        obj = ShareObj(ID)
        obj.refresh()

        self.cash -= float(obj.getPrice())

        with open('data.json', 'r+') as file:

            # read file
            data = json.load(file)

            # wipe file
            file.seek(0)
            file.truncate()

            # add new price to appropriate id
            data['shares'][ID].append({
                "price": obj.getPrice()
            })

            data = str(data).replace("'", '"')

            file.write(data)
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

    def refresh(self):
        self.share.refresh()

w = Wallet()
shre = ShareObj("AAPL")

percentChange = 0.15

print("Initializing...\n")

while(True):
    print("Wallet:\t\t\t",w.getCash())
    print("Percent Change:\t\t", shre.getChange(),"\n")

    if(float(shre.getChange()) >= percentChange):
        print("Buy")
        print("Wallet before buy:\t",w.getCash())
        w.buy(shre.getID())
        print("Wallet after buy:\t",w.getCash())
    elif(float(shre.getChange()) <= (-1*percentChange)):
        print("Sell")
        print("Waller before sell:\t",w.getCash())
        w.sell(shre.getID())
        print("Wallet before sell:t\t",w.getCash())
    else:
        print("Do Nothing")
    print("\n")
    shre.refresh
    time.sleep(10)
