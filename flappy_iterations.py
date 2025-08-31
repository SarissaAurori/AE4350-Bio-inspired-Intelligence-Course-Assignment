import pygame
import random
import numpy as np
import math
import time

from agent import Agent
from environment import Environment
from settings import *

pygame.init()


# Population evolution
def evolve(population, retain=0.25, mutate_rate=0.08, random_select=0.05):
    population.sort(key=lambda a: a.fitness, reverse=True)
    retain_len = max(1, int(len(population) * retain))
    survivors = population[:retain_len]
    for a in population[retain_len:]:
        if random.random() < random_select:
            survivors.append(a)
    children = []
    while len(survivors) + len(children) < len(population):
        parent = random.choice(survivors)
        children.append(parent.mutate(rate=mutate_rate))
    next_gen = survivors + children
    return next_gen


# Reward Giving
class Rewarder:
    SURVIVE_PER_FRAME = 0.05
    PASS_GATE_REWARD = 50.0
    CENTERING_SCALE = 0.12
    VEL_SMOOTH_PENALTY = 0.01
    HIT_WALL_PENALTY = -100.0
    HIT_GATE_PENALTY = -100.0
    FLAP_COST = 0.005

    @staticmethod
    def centering_reward(bird_y, gate_center, gate_gap):
        d = abs((bird_y - gate_center) / (gate_gap * 0.5))
        d = min(1.5, d)
        return (1.5 - d) * Rewarder.CENTERING_SCALE


# Training
def simulate_generation(population, env, draw=True, max_frames=6000, max_gates=50):
    env.reset()
    for a in population:
        a.reset_runtime_state()

    screen = pygame.display.set_mode((WIDTH, HEIGHT)) if draw else None
    clock = pygame.time.Clock()
    font = pygame.font.SysFont(None, 20)

    alive_count = len(population)
    frame = 0
    last_drawn = -1
    any_finished = False

    while frame < max_frames and alive_count > 0 and not any_finished:
        frame += 1
        env.frames = frame

        if draw:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit

        env.update_gates()

        alive_count = 0
        total_score_for_hud = 0
        for agent in population:
            if not agent.alive:
                continue

            ng = env.next_gate_for_x(agent.x)
            gate_center = ng["gap_y"] + ng["gap_h"] / 2.0
            inputs = [
                agent.y / HEIGHT,
                agent.vy / 10.0,
                (ng["x"] - agent.x) / WIDTH,
                gate_center / HEIGHT,
            ]

            do_flap = agent.decide(inputs)
            if do_flap:
                agent.vy = env.lift
                agent.fitness -= Rewarder.FLAP_COST

            agent.vy += env.gravity
            agent.y += agent.vy

            agent.fitness += Rewarder.SURVIVE_PER_FRAME
            agent.fitness -= Rewarder.VEL_SMOOTH_PENALTY * (abs(agent.vy) / 10.0)
            agent.fitness += Rewarder.centering_reward(agent.y, gate_center, ng["gap_h"])

            hit_ceiling = (agent.y - 12) < 0
            hit_ground = (agent.y + 12) > HEIGHT

            collided_gate = False
            for g in env.gates:
                gx = g["x"]
                gy = g["gap_y"]
                if gx < agent.x + 12 < gx + gate_width:
                    if agent.y - 12 < gy or agent.y + 12 > gy + g["gap_h"]:
                        collided_gate = True
                        break

            if hit_ceiling or hit_ground:
                agent.fitness += Rewarder.HIT_WALL_PENALTY
                agent.alive = False
            elif collided_gate:
                agent.fitness += Rewarder.HIT_GATE_PENALTY
                agent.alive = False
            else:
                for g in env.gates:
                    if ((not g["scored"].get(id(agent), False)) and g["x"] + gate_width < agent.x):  # 
                        agent.score += 1
                        g["scored"][id(agent)] = True
                        agent.fitness += Rewarder.PASS_GATE_REWARD
                        if agent.score >= max_gates:
                            any_finished = True

            if agent.alive:
                alive_count += 1
                total_score_for_hud = max(total_score_for_hud, agent.score)

        env.score_for_all = total_score_for_hud

        if draw and (frame - last_drawn >= SKIP_DRAW_FRAMES):
            last_drawn = frame
            screen.fill(LIGHT_GRAY)

            for g in env.gates:
                pygame.draw.rect(screen, GATE_COLOR, (g["x"], 0, gate_width, g["gap_y"]))
                pygame.draw.rect(
                    screen, GATE_COLOR,
                    (g["x"], g["gap_y"] + g["gap_h"], gate_width, HEIGHT - (g["gap_y"] + g["gap_h"]))
                )

            for a in population:
                if a.alive:
                    pygame.draw.circle(screen, a.color, (int(a.x), int(a.y)), 6)

            best_fit = max(a.fitness for a in population)
            best_score = max(a.score for a in population)
            avg_fit = sum(a.fitness for a in population) / len(population)
            hud_lines = [
                f"Gen running… Frame: {frame}",
                f"Alive: {alive_count}/{len(population)}",
                f"Best score: {best_score}",
                f"Avg fitness: {avg_fit:.2f}",
                f"Best fitness: {best_fit:.2f}",
            ]
            y = 6
            for line in hud_lines:
                txt = font.render(line, True, HUD_COLOR)
                screen.blit(txt, (8, y))
                y += 18

            pygame.display.flip()
            clock.tick(FPS)

    for a in population:
        if a.alive:
            a.fitness += 0.25 * frame

    best_score = max(a.score for a in population)
    avg_fit = sum(a.fitness for a in population) / len(population)
    return best_score, avg_fit


# training loop
def train(
    generations=200,
    pop_size=50,
    target_score=50,
    draw_training=True,
    max_frames_per_gen=10000,
    retain=0.25,
    mutate_rate=0.09,
    random_select=0.05,
    hidden_layers=8
):
    population = [Agent(4, hidden_layers, 1) for _ in range(pop_size)]
    env = Environment()
    if draw_training:
        pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Evolving Flappy Agents")

    np.random.seed(0)
    random.seed(0)

    best_fitness_history = []
    avg_fitness_history = []

    gen = 0
    while gen < generations:
        gen += 1
        best_score, avg_fit = simulate_generation(
            population, env, draw=draw_training, max_frames=max_frames_per_gen, max_gates=target_score
        )
        best_fit_now = max(a.fitness for a in population)
        avg_fitness_history.append(avg_fit)
        best_fitness_history.append(best_fit_now)
        print(f"Generation {gen:3d} | Best score: {best_score:4d} | Best fitness: {best_fit_now:8.2f} | Avg fit: {avg_fit:8.2f}")

        if best_score >= target_score:
            print(f"\nTarget reached (score ≥ {target_score}) at Generation {gen}!")
            break

        population = evolve(population, retain=retain, mutate_rate=mutate_rate, random_select=random_select)

    return avg_fitness_history, best_fitness_history


# Entry point
if __name__ == "__main__":
    retain_list = np.arange(0.1, 0.31, 0.05)
    mutate_list = np.arange(0.05, 0.16, 0.01)
    select_list = np.arange(0.02, 0.11, 0.01)
    hidden_list = [5, 7, 9, 11]
    pop_list = [25, 50, 75, 100]

    # for retain in retain_list:
    #     avg_fit, best_fit = train(
    #         generations=300,
    #         pop_size=50,
    #         target_score=50,
    #         draw_training=True,
    #         max_frames_per_gen=12000,
    #         retain=retain
    #     )
    #     np.savez(f"fitness_retain_{retain:.2f}.npz", avg=np.array(avg_fit), best=np.array(best_fit))
    for pop in pop_list:
        avg_fit, best_fit = train(
            generations=300,
            pop_size=pop,
            target_score=50,
            draw_training=True,
            max_frames_per_gen=12000,
        )
        # np.savez(f"fitness_pop_{pop:.2f}.npz", avg=np.array(avg_fit), best=np.array(best_fit))

    # for mutate in mutate_list:
    #     avg_fit, best_fit = train(
    #         generations=300,
    #         pop_size=50,
    #         target_score=50,
    #         draw_training=True,
    #         max_frames_per_gen=12000,
    #         mutate_rate=mutate
    #     )
        # np.savez(f"fitness_mutate2_{mutate:.2f}.npz", avg=np.array(avg_fit), best=np.array(best_fit))

    # for select in select_list:
    #     avg_fit, best_fit = train(
    #         generations=300,
    #         pop_size=50,
    #         target_score=50,
    #         draw_training=True,
    #         max_frames_per_gen=12000,
    #         random_select=select
    #     )
        # np.savez(f"fitness_select2_{select:.2f}.npz", avg=np.array(avg_fit), best=np.array(best_fit))

    # for hidden in hidden_list:
    #     avg_fit, best_fit = train(
    #         generations=300,
    #         pop_size=50,
    #         target_score=50,
    #         draw_training=True,
    #         max_frames_per_gen=12000,
    #         hidden_layers=hidden
    #     )
    #     np.savez(f"fitness_hidden_{hidden}.npz", avg=np.array(avg_fit), best=np.array(best_fit))
        
    pygame.quit()
