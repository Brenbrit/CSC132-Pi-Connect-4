#fruit has an origin (str) and indicator of frehsness (isFresh -- boolean)
#a fruit can print info (__str__)


#a sale item has a price (float) inventory (int) location (str)
#can be sold(quanitity:int) bought(quantity:int) move (location:str) output (__str__)

class Fruit():
    def __init__(self, origin):
        self.origin = origin
        self.isFresh = True
    @property
    def origin(self):
        return self._origin

    @origin.setter
    def origin(self, origin):
        self._origin = origin

    def __str__(self):
        return (" Fruit is {} and is from {}".format(self.isFresh, self.origin)



class saleItem():
    def __init__(self, price, inventory, location):
        self.price = float(price)
        self.inventory = inventory
        self.location = location

    def


class Banana(Fruit, saleItem):
    def __init__(self, origin, price, location, inventory):
        Fruit.__init(self, origin)
        saleitem.__init(self, price, location, inventory)

        
