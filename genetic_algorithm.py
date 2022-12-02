import random
import time
from typing import List

import numpy as np
import pandas as pd

import TSPClasses
from TSPClasses import City, TSPSolution

"""
def geneticAlgorithm(population, popSize, eliteSize, mutationRate, generations):
    pop = initialPopulation(popSize, population)
    print("Initial distance: " + str(1 / rankRoutes(pop)[0][1]))
    
    for i in range(0, generations):
        pop = nextGeneration(pop, eliteSize, mutationRate)
    
    print("Final distance: " + str(1 / rankRoutes(pop)[0][1]))
    bestRouteIndex = rankRoutes(pop)[0][0]
    bestRoute = pop[bestRouteIndex]
    return bestRoute
"""


def initial_generation(cities: List[City], population_size: int) -> list[TSPSolution]:
    return [TSPSolution(random.sample(cities, len(cities))) for _ in range(population_size)]


def selection(pop: List[TSPSolution], elite_size: int):
    results = []

    pop = sorted(pop, key=lambda x: x.cost)

    df = pd.DataFrame(np.array([[ind.cost] for ind in pop]), columns=["cost"])
    df["cum_sum"] = df.cost.cumsum()
    df["cum_perc"] = 100 * df.cum_sum / df.cost.sum()

    for i in range(0, elite_size):
        results.append(pop[i])
    for _ in range(0, len(pop) - elite_size):
        pick = 100 * random.random()
        for i in range(0, len(pop)):
            if pick <= df.iat[i, 2]:
                results.append(pop[i])
                break

    return results


def mutate(individual: TSPSolution, mutation_rate: float = 0.1) -> TSPSolution:
    if random.random() >= mutation_rate:
        return TSPSolution(random.sample(individual.route, len(individual.route)))
    cities = individual.route.copy()
    i = random.randint(0, len(cities) - 1)
    j = random.randint(0, len(cities) - 1)
    cities[i], cities[j] = cities[j], cities[i]
    return TSPSolution(cities)


def breed(individual1: TSPSolution, individual2: TSPSolution) -> TSPSolution:
    i = random.randint(0, len(individual1.route) - 1)
    j = random.randint(0, len(individual1.route) - 1)

    start = min(i, j)
    end = max(i, j)

    gnome_part_1 = [individual1.route[a] for a in range(start, end)]
    gnome_part_2 = [
        individual2.route[a] for a in range(len(individual2.route)) if individual2.route[a] not in gnome_part_1
    ]

    return TSPSolution(gnome_part_1 + gnome_part_2)


def breed_population(population: List[TSPSolution], elite_size: int):
    next_generation = list(population[:elite_size])
    for _ in range(elite_size, len(population)):
        while True:
            parent1 = random.choice(population)
            parent2 = random.choice(population)
            if parent1 != parent2:
                break
        child = breed(parent1, parent2)
        next_generation.append(child)
    return next_generation
