class Action:
    pass


class Move(Action):
    def __init__(self, heading_delta, move_speed):
        self.heading_delta = heading_delta
        self.move_speed = move_speed


class TurnAround(Action):
    pass


class DepositPheromone(Action):
    def __init__(self, pheromone):
        self.pheromone = pheromone


class EnterNest(Action):
    def __init__(self, nest):
        self.nest = nest


class LeaveNest(Action):
    pass
