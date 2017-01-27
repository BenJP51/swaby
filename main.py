from yahoo_finance import Share
import time, json, sys

class Wallet():

    def __init__(self):
        self.cash = 10000

    def buy(self, ID):
        obj = ShareObj(ID)
        obj.refresh()

        self.cash -= float(obj.getPrice())

        with open('data.json', 'r+') as file:
            try:
                data = json.load(file) # read file
            except json.decoder.JSONDecodeError:
                print('check your json file')
                sys.exit(0)

            # wipe file
            file.seek(0)
            file.truncate()

            try:
                data['shares'].append({ # add new price to appropriate id
                    "id": obj.getID(),
                    "price": obj.getPrice()
                })
            except AttributeError:
                # uh oh!!! that ID doesnt exist yet!! just create it :)
                print(data['shares'])
                data['shares'].append({
                    "id": obj.getID(),
                    "price": obj.getPrice()
                })

            data = str(data).replace("'", '"')

            file.write(data)
            file.close()

    def sell(self, ID):
        obj = ShareObj(ID)
        obj.refresh()

        self.cash += float(obj.getPrice())

        with open('data.json', 'r+') as file: #open file
            try:
                data = json.load(file) # read file
            except json.decoder.JSONDecodeError:
                print("Error - Check JSON file!") #error check -- json file error
                sys.exit(0)

            file.seek(0) #wipe file
            file.truncate()

            for index in range(0,len(data["shares"])): #for the amount of shares recorded in json file
                try:
                    isValid = data["shares"][index]["id"] #checks if valid id
                except AttributeError: #if error, report it
                    print("ERROR - SELLING - share ID doesn't exist.")

                if(data["shares"][index]["id"] == ID): #if valid, check if IDs match
                    del data["shares"][index] #if match, delete

                index += 1 #add one to index

            data = str(data).replace("'", '"') #clean up json

            file.write(data)#write to json
            file.close() #close json

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
shre = ShareObj("AMZN")

percentChange = 0.15

print("Initializing...\n")

while(True):
    print("Wallet:\t\t\t",w.getCash())
    print("Percent Change:\t\t", shre.getChange(),"\n")

    if(float(shre.getChange()) >= percentChange):
        print("Buy")
        print("Wallet before buy:\t",w.getCash())

        w.buy(shre.id)

        print("Wallet after buy:\t",w.getCash())
    elif(float(shre.getChange()) <= (-1*percentChange)):
        print("Sell")
        print("Waller before sell:\t",w.getCash())

        w.sell(shre.id)

        print("Wallet before sell:t\t",w.getCash())
    else:
        print("Do Nothing")
    print("\n")

    shre.refresh
    time.sleep(5)
