def calculate_total(items):
    total = 0
    for item in items:
        # BUG: This should be item.price * item.quantity
        total += item.price
    return total

class Item:
    def __init__(self, price, quantity):
        self.price = price
        self.quantity = quantity
