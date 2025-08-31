import random
import numpy as np
from settings import *


# Environment 
class Environment:
    def __init__(self):
        self.gravity = 0.5
        self.lift = -7.5
        self.gates = []
        self.spawn_timer = 0
        self.next_spawn_interval = random.randint(MIN_SPAWN_INTERVAL, MAX_SPAWN_INTERVAL)
        self.gate_speed = 3.2
        self.frames = 0
        self.score_for_all = 0

    def reset(self):
        self.gates.clear()
        self.spawn_timer = 0
        self.next_spawn_interval = random.randint(MIN_SPAWN_INTERVAL, MAX_SPAWN_INTERVAL)
        self.frames = 0
        self.score_for_all = 0

    def update_gates(self):
        self.spawn_timer += 1
        if self.spawn_timer >= self.next_spawn_interval:
            gate_gap = random.randint(MIN_GATE_GAP, MAX_GATE_GAP)
            gap_y = random.randint(80, HEIGHT - (gate_gap + 80))
            self.gates.append({
                "x": WIDTH,
                "gap_y": gap_y,
                "gap_h": gate_gap,
                "scored": {}
            })
            self.spawn_timer = 0
            self.next_spawn_interval = random.randint(MIN_SPAWN_INTERVAL, MAX_SPAWN_INTERVAL)

        for g in self.gates:
            g["x"] -= self.gate_speed
        self.gates = [g for g in self.gates if g["x"] + gate_width > 0]

    def next_gate_for_x(self, bird_x):
        for g in self.gates:
            if g["x"] + gate_width > bird_x:
                return g
        return {"x": WIDTH, "gap_y": HEIGHT // 2, "gap_h": (MIN_GATE_GAP+MAX_GATE_GAP)//2, "scored": {}}
