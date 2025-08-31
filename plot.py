import numpy as np
from matplotlib import pyplot as plt

def read_generations(name, values):
    generation_counts = []
    for value in values:
        if isinstance(value, float):
            value = f"{value:.2f}"
        filename = f'fitness_{name}_{value}.npz'
        data = np.load(filename)
        generation_counts.append(len(data['best']) - 1)
    return generation_counts

hidden_values = [5, 7, 9, 11]
mutate_values = [0.05, 0.07, 0.09, 0.11, 0.13, 0.15]
mutate2_values = [0.05, 0.06, 0.07, 0.08, 0.09, 0.10, 0.11, 0.12, 0.13, 0.14, 0.15]
retain_values = [0.10, 0.15, 0.20, 0.25, 0.30]
select_values = [0.02, 0.04, 0.06, 0.08, 0.10]
select2_values = [0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.10]
pop = [25.0, 50.0, 75.0, 100.0]

# hidden_5 = np.load('fitness_hidden_5.npz')
# hidden_7 = np.load('fitness_hidden_7.npz')
# hidden_9 = np.load('fitness_hidden_9.npz')
# hidden_11 = np.load('fitness_hidden_11.npz')
fig, ax = plt.subplots(2, 2)
ax[0,0].plot(hidden_values, read_generations('hidden', hidden_values))
ax[0,1].plot(mutate_values, read_generations('mutate', mutate_values), label='Run 1')
ax[0,1].plot(mutate2_values, read_generations('mutate2', mutate2_values), label='Run 2')
ax[1,0].plot(retain_values, read_generations('retain', retain_values))
ax[1,1].plot(select_values, read_generations('select', select_values), label='Run 1')
ax[1,1].plot(select2_values, read_generations('select2', select2_values), label ='Run 2')
ax[0,0].set_xlabel('Hidden neurons [-]')
ax[0,0].set_ylabel('Generations to reach target score [-]')
ax[0,1].set_xlabel('Mutation rate [-]')
ax[0,1].set_ylabel('Generations to reach target score [-]')
ax[1,0].set_xlabel('Retention rate [-]')
ax[1,0].set_ylabel('Generations to reach target score [-]')
ax[1,1].set_xlabel('Random selection rate [-]')
ax[1,1].set_ylabel('Generations to reach target score [-]')

ax[0,0].grid()
ax[0,1].grid()
ax[1,0].grid()
ax[1,1].grid()

ax[0,1].legend()
ax[1,1].legend()
fig.tight_layout()
# ax.plot([5, 7, 9, 11], [len(hidden_5['best']) - 1, len(hidden_7['best']) - 1, len(hidden_9['best']) - 1, len(hidden_11['best']) - 1])
# ax.set_xlabel('Hidden neurons')
# ax.set_ylabel('Generations to reach target score')

fig2, ax2 = plt.subplots()
ax2.plot(pop, read_generations('pop', pop))
ax2.set_xlabel('Population size [-]')
ax2.set_ylabel('Generations to reach target score [-]')
ax2.grid()
plt.show()
