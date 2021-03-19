class Text:
    def __init__(self, quarter, date, url):
        self.quarter = quarter
        self.date = date
        self.url = url
        self.futureRes = None
        self.res = None

    def __repr__(self):
        return f"({self.quarter.id}, {self.date}, {self.url})"
