

class sqliteProcessor(object):
    def init():
        self.maxRawID = -1
        self.update = True


    def process():
        # loop
        while self.update:
            # if timenow < timelast +10:
            #     sleep(10)
            self.geoData()

        Each function should 
        initially -
          -- load all the raw data
          -- process it, make interesting numbers
          -- store processed results in self
          -- populate the relevant table in sqlite
        on update
          -- fetch raw data that hasn't been seen
          -- add it to / aggregate it with current data
          -- update interesting numbers
          -- update sqlite
          

    def geoData():







