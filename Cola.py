# Cola.py
class Cola:
    def __init__(self):
        self.items = []

    def enqueue(self, mission):
        self.items.append(mission)

    def dequeue(self):
        if not self.is_empty():
            return self.items.pop(0)
        return None

    def first(self):
        if not self.is_empty():
            return self.items[0]
        return None

    def is_empty(self):
        return len(self.items) == 0

    def size(self):
        return len(self.items)