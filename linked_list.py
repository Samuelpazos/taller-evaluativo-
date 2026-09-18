class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None
        self.size = 0

    def append(self, value):
        node = Node(value)
        if not self.head:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.size += 1

    def remove(self, code):
        prev, cur = None, self.head
        while cur:
            if cur.value.code == code:
                if prev:
                    prev.next = cur.next
                else:
                    self.head = cur.next
                if cur is self.tail:
                    self.tail = prev
                self.size -= 1
                return cur.value
            prev, cur = cur, cur.next
        return None

    def find(self, code):
        cur = self.head
        while cur:
            if cur.value.code == code:
                return cur.value
            cur = cur.next
        return None

    def values(self):
        result, cur = [], self.head
        while cur:
            result.append(cur.value)
            cur = cur.next
        return result
