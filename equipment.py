class Equipment:
    def __init__(self, code, kind):
        self.code = code
        self.kind = kind
        self.status = "IN_CART"
        self.loans = 0
        self.student = None
        self.start_time = None

    def __str__(self):
        return self.code
