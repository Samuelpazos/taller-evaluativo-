from models.equipment import Equipment
from models.request import Request
from structures.linked_list import LinkedList
from structures.queue import Queue
from structures.stack import Stack

class LabService:
    def __init__(self, capacity=5, max_hours=4):
        self.capacity = capacity
        self.max_hours = max_hours
        self.inventory = LinkedList()
        self.carts = {k: Stack() for k in ("PORTATIL", "KIT", "MULTIMETRO")}
        self.waiting = {k: Queue() for k in self.carts}
        self.review = Queue()
        self.to_store = Queue()
        self.borrowed = {}
        self.log = []
        self.directed = 0
        self.moves = 0
        self.immediate = 0
        self.queued = 0
        self.wait_times = []
        self.damaged = 0
        self.preventive = 0

    def load_sample(self):
        self.__init__(self.capacity, self.max_hours)
        data = [
            ("PORT-01","PORTATIL"),("PORT-02","PORTATIL"),("PORT-03","PORTATIL"),
            ("PORT-04","PORTATIL"),("KIT-01","KIT"),("KIT-02","KIT"),
            ("KIT-03","KIT"),("MUL-01","MULTIMETRO"),("MUL-02","MULTIMETRO")
        ]
        for code, kind in data:
            self.add_equipment(code, kind)
        self.log.append("Sample data loaded")

    def add_equipment(self, code, kind):
        if self.inventory.find(code):
            return False, "R1: equipment code already exists"
        equipment = Equipment(code, kind)
        self.inventory.append(equipment)
        if len(self.carts[kind]) < self.capacity:
            self.carts[kind].push(equipment)
        else:
            equipment.status = "WAITING_STORAGE"
            self.to_store.enqueue(equipment)
        return True, "Equipment added"

    def remove_equipment(self, code):
        equipment = self.inventory.find(code)
        if not equipment or equipment.status != "IN_CART":
            return False, "Equipment cannot be removed"
        values = self.carts[equipment.kind].values()
        if equipment in values:
            temp = []
            while self.carts[equipment.kind].peek() is not equipment:
                temp.append(self.carts[equipment.kind].pop())
            self.carts[equipment.kind].pop()
            for item in reversed(temp):
                self.carts[equipment.kind].push(item)
        self.inventory.remove(code)
        return True, "Equipment removed"

    def request(self, student, kind, hour):
        for item in self.borrowed.values():
            if item.student == student and item.kind == kind:
                return False, "R1: student already has this equipment type"
        if any(r.student == student for r in self.waiting[kind].values()):
            return False, "R1: student is already in this waiting queue"
        if any(item.student == student and hour - item.start_time > self.max_hours
               for item in self.borrowed.values()):
            return False, "R6: student has an overdue equipment"
        if len(self.carts[kind]):
            equipment = self.carts[kind].pop()
            equipment.status = "BORROWED"
            equipment.loans += 1
            equipment.student = student
            equipment.start_time = hour
            self.borrowed[equipment.code] = equipment
            self.immediate += 1
            return True, f"Loaned {equipment.code}"
        self.waiting[kind].enqueue(Request(student, kind, hour))
        self.queued += 1
        return True, "R3: request added to waiting queue"

    def directed_loan(self, code):
        equipment = self.inventory.find(code)
        if not equipment or equipment.status != "IN_CART":
            return False, "Equipment is not available in a cart"
        cart = self.carts[equipment.kind]
        aux = Stack()
        moves = 0
        while cart.peek() is not equipment:
            aux.push(cart.pop())
            moves += 1
        cart.pop()
        moves += 1
        while len(aux):
            cart.push(aux.pop())
            moves += 1
        equipment.status = "BORROWED"
        equipment.loans += 1
        equipment.student = "TEACHER"
        equipment.start_time = 0
        self.borrowed[equipment.code] = equipment
        self.directed += 1
        self.moves += moves
        return True, f"Directed loan: {equipment.code}, movements: {moves}"

    def return_equipment(self, code, hour):
        equipment = self.borrowed.pop(code, None)
        if not equipment:
            return False, "Equipment is not currently borrowed"
        duration = hour - equipment.start_time
        equipment.status = "IN_REVIEW"
        equipment.student = None
        equipment.start_time = None
        self.review.enqueue((equipment, duration))
        return True, f"Returned {code}; duration: {duration} h"

    def review_next(self, damaged=False):
        item = self.review.dequeue()
        if not item:
            return False, "Review queue is empty"
        equipment, duration = item
        if damaged:
            equipment.status = "MAINTENANCE"
            self.damaged += 1
            return True, f"{equipment.code} sent to maintenance"
        if equipment.loans >= 5:
            equipment.status = "MAINTENANCE"
            self.preventive += 1
            return True, f"{equipment.code} sent to preventive maintenance"
        if len(self.carts[equipment.kind]) < self.capacity:
            equipment.status = "IN_CART"
            self.carts[equipment.kind].push(equipment)
            self.serve_waiting(equipment.kind)
            return True, f"{equipment.code} approved and stored"
        equipment.status = "WAITING_STORAGE"
        self.to_store.enqueue(equipment)
        return True, f"{equipment.code} approved and queued for storage"

    def serve_waiting(self, kind):
        if len(self.carts[kind]) and self.waiting[kind].front:
            request = self.waiting[kind].dequeue()
            equipment = self.carts[kind].pop()
            equipment.status = "BORROWED"
            equipment.loans += 1
            equipment.student = request.student
            equipment.start_time = request.hour
            self.borrowed[equipment.code] = equipment
            return request
        return None

    def search(self, code):
        equipment = self.inventory.find(code)
        if not equipment:
            return None
        position = None
        if equipment.status == "IN_CART":
            values = self.carts[equipment.kind].values()
            position = values.index(equipment) + 1 if equipment in values else None
        return equipment, position

    def report(self):
        states = {}
        for e in self.inventory.values():
            states[e.status] = states.get(e.status, 0) + 1
        most = max(self.inventory.values(), key=lambda x: x.loans, default=None)
        return {
            "states": states,
            "cart_usage": {k: len(v) for k,v in self.carts.items()},
            "immediate": self.immediate,
            "queued": self.queued,
            "directed": self.directed,
            "moves": self.moves,
            "damaged": self.damaged,
            "preventive": self.preventive,
            "most_borrowed": most.code if most else "None"
        }
