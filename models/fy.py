class FY:
    def __init__(self, id, year, url):
        self.id = id
        self.year = year
        self.url = url
        self.futureRes = None
        self.res = None

    def __repr__(self):
        return f"({self.id}, {self.url})"
