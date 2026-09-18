class Elevator:
    def __init__(self, code, location, state, emergencies=0):
        self.code = code
        self.location = location
        self.state = state
        self.emergencies = emergencies

class Call:
    def __init__(self, code, elevator, kind, time):
        self.code = code
        self.elevator = elevator
        self.kind = kind
        self.time = time
        self.start = None
        self.end = None
        self.state = "WAITING"
        self.step = 0
        self.stack = None
        self.abort_reason = ""

class Maneuver:
    def __init__(self, name, reverse):
        self.name = name
        self.reverse = reverse
