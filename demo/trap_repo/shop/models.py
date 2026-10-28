class BillingAddress:
    def __init__(self, street, city, postcode):
        self.street = street
        self.city = city
        self.postcode = postcode

    def format(self):
        return f"{self.street}, {self.city} {self.postcode}"

    def __repr__(self):
        return f"<{type(self).__name__} {self.postcode}>"


class ShippingAddress:
    def __init__(self, line1, town, code):
        self.street = line1
        self.city = town
        self.postcode = code

    def format(self):
        return f"{self.street}, {self.city} {self.postcode}"

    def __repr__(self):
        return f"<{type(self).__name__} {self.postcode}>"
