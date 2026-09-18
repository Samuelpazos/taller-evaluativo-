class QueueNode:
    def __init__(self, value):
        self.value = value
        self.next = None

class Queue:
    def __init__(self):
        self.front = None
        self.rear = None
        self.size = 0

    def enqueue(self, value):
        node = QueueNode(value)
        if not self.rear:
            self.front = self.rear = node
        else:
            self.rear.next = node
            self.rear = node
        self.size += 1

    def dequeue(self):
        if not self.front:
            return None
        value = self.front.value
        self.front = self.front.next
        self.size -= 1
        if not self.front:
            self.rear = None
        return value

    def values(self):
        result, cur = [], self.front
        while cur:
            result.append(cur.value)
            cur = cur.next
        return result
