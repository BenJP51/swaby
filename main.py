from yahoo_finance import Share
import time, json, sys

class Wallet():

    def __init__(self):
        with open('data.json', 'r+') as file: #open file
            try:
                data = json.load(file) # read file
                self.cash = data["userdata"]["wallet"]
            except json.decoder.JSONDecodeError:
                print("Error - Check JSON file!") #error check -- json file error
                sys.exit(0)

    def buy(self, ID):
        obj = ShareObj(ID)
        obj.refresh()

        if(self.cash > float(obj.getPrice())): #if you have sufficient funds
            self.cash -= float(obj.getPrice()) #buy that shit

            with open('data.json', 'r+') as file:
                try:
                    data = json.load(file) # read file
                except json.decoder.JSONDecodeError:
                    print('Error loading JSON - Check your JSON file')
                    sys.exit(0)

                # wipe file
                file.seek(0)
                file.truncate()


                try: #to allow for multiple shares to be done you could like set a variable of percent change in the json, read that. if that *= 0.05 isn't less that the current percent change, don't buy again
                    highestIDIndex = -1

                    for i in range(0,len(data["shares"])): #iterate through all shares TRY ISNT GOING THROUGH
                        if(data["shares"][i]["id"] == obj.getID()): #get the most recently added share
                            highestIDIndex = i

                    if(highestIDIndex != -1): # if highestIDIndex is -1, it means that the share is not yet owned, so add it w/o comparing change
                        if(float(data["shares"][highestIDIndex]["change"]) < (obj.getChange() - 0.01)):
                                data["shares"].append({ # add new price to appropriate id
                                    "id": obj.getID(),
                                    "price": obj.getPrice(),
                                    "time": time.strftime("%H:%M:%S"),
                                    "change": obj.getChange()
                                })
                        else:
                            print("Change not enough to buy another share!")
                    else:
                        data["shares"].append({ # add new price to appropriate id
                            "id": obj.getID(),
                            "price": obj.getPrice(),
                            "time": time.strftime("%H:%M:%S"),
                            "change": obj.getChange()
                        })

                except AttributeError:
                    # uh oh!!! that ID doesnt exist yet!! just create it :)
                    data['shares'].append({
                        "id": obj.getID(),
                        "price": obj.getPrice(),
                        "time": time.strftime("%H:%M:%S"),
                        "change": obj.getChange()
                    })

                data = str(data).replace("'", '"')

                file.write(data)
                file.close()

    def sell(self, ID):
        obj = ShareObj(ID)
        obj.refresh()

        with open('data.json', 'r+') as file: #open file
            try:
                data = json.load(file) # read file
            except json.decoder.JSONDecodeError:
                print("Error - Check JSON file!") #error check -- json file error
                sys.exit(0)

            file.seek(0) #wipe file
            file.truncate()

            exists = False #checks to see if stock is owned

            for i in range(0,len(data["shares"])): #for the amount of shares recorded in json file
                try:
                    if(data["shares"][i]["id"] == obj.getID()): #checks if valid id, as in, does this share exist in the JSON?
                        exists = True
                except AttributeError: #if error, report it
                    print("ERROR - SELLING - share ID doesn't exist.")
                    sys.exit(0)
            if(exists == False):
                print("ERROR - SELLING - Stock not owned!!")
                sys.exit(0)

            shareAmount = [] #list of indexes of items to be removed
            counter = 0 #

            for i in range(len(data["shares"])):
                if(data["shares"][i]["id"] == obj.getID()): #create list of indexes of shares to be removed and sold
                    shareAmount.insert(0,i)

            for i in range(len(shareAmount)):
                del data["shares"][shareAmount[i]] #sell all shares of id

            data = str(data).replace("'", '"') #clean up json

            file.write(data)#write to json
            file.close() #close json

        self.cash += float(obj.getPrice())*int(len(shareAmount))

    def getCash(self):
        return self.cash

class ShareObj(object):
    def __init__(self, ID):
        self.id = ID
        self.share = Share(self.id)
        self.refresh

    def getPrice(self):
        return self.share.get_price()

    def getOpenPrice(self):
        return self.share.get_open()

    def getChange(self):
        percent = self.share.get_percent_change()
        return float(percent[:-1])

    def getChangeFormatted(self):
        self.share.get_percent_change()

    def getID(self):
        return self.id

    def refresh(self):
        self.share.refresh()

w = Wallet()

stocksToWatch = ["TSLA", "AMZN", "FB", "MSFT", "GOOG"]

percentChange = 0.05

print("Initializing...\n")

while(True):
    for i in stocksToWatch:
        shre = ShareObj(i)
        shre.refresh()

        print("Wallet: %.2f\t\t\t" % w.getCash())
        print("% Change of",shre.getID(),":\t", shre.getChange(),"\n")

        if(float(shre.getChange()) >= percentChange):
            print("Buy")
            print("Wallet before buy: %.2f\t" % w.getCash())

            w.buy(shre.id)

            print("Wallet after buy: %.2f\t" % w.getCash())
        elif(float(shre.getChange()) <= (-1*percentChange)):
            print("Sell")
            print("Waller before sell:%.2f\t" % w.getCash())

            w.sell(shre.id)

            print("Wallet after sell: %.2f\t" % w.getCash())
        else:
            print("Do Nothing")
        print("\n")
    time.sleep(5)
