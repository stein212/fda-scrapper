class Quarter:
    def __init__(self, fy, id, quarter, url):
        self.fy = fy
        self.id = id
        self.quarter = quarter
        self.url = url
        self.futureRes = None
        self.res = None

    def __repr__(self):
        return f"({self.id}, {self.quarter}, {self.url})"
