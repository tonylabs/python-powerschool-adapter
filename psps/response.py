class Response:
    def __init__(self, data):
        self.data = data

    def is_empty(self):
        return not self.data

    def to_dict(self):
        return self.data