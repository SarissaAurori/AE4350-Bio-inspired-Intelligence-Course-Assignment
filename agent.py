import numpy as np
import random
from settings import *


# Agent 
class Agent:
    def __init__(self, n_inputs=4, n_hidden=8, n_outputs=1):
        self.n_inputs = n_inputs
        self.n_hidden = n_hidden
        self.n_outputs = n_outputs
        self.W1 = np.random.randn(n_hidden, n_inputs)
        self.b1 = np.random.randn(n_hidden, 1)
        self.W2 = np.random.randn(n_outputs, n_hidden)
        self.b2 = np.random.randn(n_outputs, 1)
        self.fitness = 0.0
        self.score = 0
        self.alive = True
        self.x = 100.0
        self.y = HEIGHT // 2
        self.vy = 0.0
        self.color = (
            random.randint(40, 240),
            random.randint(40, 240),
            random.randint(40, 240),
        )

    def reset_runtime_state(self):
        self.fitness = 0.0
        self.score = 0
        self.alive = True
        self.x = 100.0
        self.y = HEIGHT // 2
        self.vy = 0.0

    def forward(self, inputs):
        h = np.tanh(self.W1 @ inputs + self.b1)
        y = np.tanh(self.W2 @ h + self.b2)
        return float(y[0, 0])

    def decide(self, inputs_vec):
        x = np.array(inputs_vec, dtype=np.float32).reshape(self.n_inputs, 1)
        y = self.forward(x)
        return y > 0

    def mutate(self, rate=0.1):
        def mut(m):
            return m + rate * np.random.randn(*m.shape)

        child = Agent()
        child.W1 = mut(self.W1)
        child.b1 = mut(self.b1)
        child.W2 = mut(self.W2)
        child.b2 = mut(self.b2)
        return child
