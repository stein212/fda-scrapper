from functools import total_ordering


@total_ordering
class Account:
    def __init__(self, text, value):
        self.text = text
        self.value = value

    def __repr__(self):
        return f"({self.text.quarter.id}, {self.text.date}, {self.value})"

    def __eq__(self, other):
        if not isinstance(other, Account):
            return NotImplemented
        return self.text.date == other.text.date and self.value == other.value

    def __lt__(self, other):
        if not isinstance(other, Account):
            return NotImplemented
        return self.text.date < other.text.date
