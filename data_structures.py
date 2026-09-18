class Node:
    def __init__(self, data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def add(self, data):
        n = Node(data)
        if not self.head:
            self.head = self.tail = n
        else:
            self.tail.next = n
            self.tail = n
        self.size += 1

    def find(self, code):
        p = self.head
        while p:
            if p.data.code == code:
                return p.data
            p = p.next
        return None

    def __iter__(self):
        p = self.head
        while p:
            yield p.data
            p = p.next

class Queue:
    def __init__(self):
        self.first = None
        self.last = None
        self.size = 0

    def enqueue(self, data):
        n = Node(data)
        if not self.last:
            self.first = self.last = n
        else:
            self.last.next = n
            self.last = n
        self.size += 1

    def dequeue(self):
        if not self.first:
            return None
        data = self.first.data
        self.first = self.first.next
        self.size -= 1
        if not self.first:
            self.last = None
        return data

    def __len__(self):
        return self.size

class Stack:
    def __init__(self):
        self.top = None
        self.size = 0

    def push(self, data):
        n = Node(data)
        n.next = self.top
        self.top = n
        self.size += 1

    def pop(self):
        if not self.top:
            return None
        data = self.top.data
        self.top = self.top.next
        self.size -= 1
        return data

    def peek(self):
        return self.top.data if self.top else None

    def __len__(self):
        return self.size
