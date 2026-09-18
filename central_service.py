from data_structures import LinkedList, Queue, Stack
from models import Elevator, Call, Maneuver

class Central:
    def __init__(self):
        self.park = LinkedList()
        self.emergency = Queue()
        self.maintenance = Queue()
        self.calls = LinkedList()
        self.emergency_count = 0
        self.clock = 0
        self.attended = {"EMERGENCY": 0, "MAINTENANCE": 0}
        self.rejected_duplicate = 0
        self.rejected_out = 0
        self.completed = 0
        self.aborted = 0
        self.abort_reasons = {}
        self.out_service = []
        self.response = {"EMERGENCY": [], "MAINTENANCE": []}
        self.compliance = {"EMERGENCY": [0, 0], "MAINTENANCE": [0, 0]}

    def load(self, text):
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            p = [x.strip() for x in line.split(";")]
            if len(p) >= 3:
                e = Elevator(p[0], p[1], p[2], int(p[3]) if len(p) > 3 else 0)
                self.park.add(e)
                if e.emergencies >= 3:
                    e.state = "OUT_OF_SERVICE"
                    self.out_service.append(e.code)

    def register(self, code, elevator, kind, time):
        e = self.park.find(elevator)
        if not e:
            return "Elevador no encontrado"
        if e.state == "OUT_OF_SERVICE":
            self.rejected_out += 1
            return "Elevador fuera de servicio"
        p = self.calls.head
        while p:
            c = p.data
            if c.elevator == elevator and c.state in ("WAITING", "IN_PROGRESS"):
                self.rejected_duplicate += 1
                return "Ya existe una llamada activa"
            p = p.next
        c = Call(code, elevator, kind, time)
        self.calls.add(c)
        if kind == "EMERGENCY":
            self.emergency.enqueue(c)
        else:
            self.maintenance.enqueue(c)
        e.state = "IN_QUEUE"
        return "Llamada registrada"

    def attend(self, time):
        c = None
        if self.emergency_count >= 4 and len(self.maintenance):
            c = self.maintenance.dequeue()
            self.emergency_count = 0
        elif len(self.emergency):
            c = self.emergency.dequeue()
            self.emergency_count += 1
        elif len(self.maintenance):
            c = self.maintenance.dequeue()
        else:
            return None
        c.state = "IN_PROGRESS"
        c.start = time
        e = self.park.find(c.elevator)
        if e:
            e.state = "IN_PROGRESS"
        self.attended[c.kind] += 1
        return c

    def execute(self, call, name, reverse):
        if call.kind != "EMERGENCY":
            return "Solo las emergencias tienen protocolo"
        if call.stack is None:
            call.stack = Stack()
        steps = [
            ("Asegurar zona", "Retirar seguro"),
            ("Cortar energia", "Restaurar energia"),
            ("Liberar puertas", "Cerrar puertas"),
            ("Evacuar personas", "Reingresar personas"),
            ("Verificar sistema", "Revertir verificacion")
        ]
        if call.step >= 5:
            return "Protocolo completo"
        expected = steps[call.step][0]
        if name != expected:
            return "Paso incorrecto"
        call.stack.push(Maneuver(name, reverse))
        call.step += 1
        return "Paso ejecutado"

    def undo(self, call):
        if not call.stack or not len(call.stack):
            return "No hay maniobras"
        m = call.stack.pop()
        return "Deshecho: " + m.reverse

    def abort(self, call, reason):
        if call.kind != "EMERGENCY":
            return "Solo aplica a emergencias"
        if call.stack:
            while len(call.stack):
                call.stack.pop()
        call.state = "ABORTED"
        call.abort_reason = reason
        self.aborted += 1
        self.abort_reasons[reason] = self.abort_reasons.get(reason, 0) + 1
        e = self.park.find(call.elevator)
        if e:
            e.state = "OPERATIVE"
        return "Rescate abortado"

    def close(self, call, time):
        if call.kind == "EMERGENCY" and call.step < 5:
            return "No se puede cerrar: faltan pasos"
        call.end = time
        call.state = "CLOSED"
        wait = max(0, time - call.time)
        self.response[call.kind].append(wait)
        limit = 30 if call.kind == "EMERGENCY" else 240
        self.compliance[call.kind][0 if wait <= limit else 1] += 1
        e = self.park.find(call.elevator)
        if e:
            e.state = "OPERATIVE"
            if call.kind == "EMERGENCY":
                e.emergencies += 1
                if e.emergencies >= 3:
                    e.state = "OUT_OF_SERVICE"
                    if e.code not in self.out_service:
                        self.out_service.append(e.code)
        if call.kind == "EMERGENCY":
            self.completed += 1
        return "Llamada cerrada"

    def report(self):
        r = []
        for kind in ("EMERGENCY", "MAINTENANCE"):
            times = self.response[kind]
            avg = sum(times) / len(times) if times else 0
            mx = max(times) if times else 0
            ok, no = self.compliance[kind]
            r.append(f"{kind}: atendidas={self.attended[kind]}, promedio={avg:.1f}, max={mx}, cumplidas={ok}, no_cumplidas={no}")
        waiting = sum(1 for c in self.calls if c.state == "WAITING")
        r.append(f"En espera al cierre={waiting}")
        r.append(f"Rescates completados={self.completed}, abortados={self.aborted}")
        r.append(f"Rechazos duplicados={self.rejected_duplicate}, fuera de servicio={self.rejected_out}")
        r.append(f"Elevadores fuera de servicio={','.join(self.out_service) if self.out_service else 'ninguno'}")
        return "\n".join(r)
