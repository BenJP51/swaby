from yahoo_finance import Share
import time

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

    def refresh(self):
        self.share.refresh()

amazon = ShareObj("AMZN")

while(True):
    if(float(amazon.getChange()) >= 0.25):
        print("Percent Change:", amazon.getChange())
        print("Buy")
    elif(float(amazon.getChange()) <= -0.25):
        print("Percent Change:", amazon.getChange())
        print("Sell")
    else:
        print("Percent Change:", amazon.getChange())
        print("Do Nothing")
    amazon.refresh
    time.sleep(120)
