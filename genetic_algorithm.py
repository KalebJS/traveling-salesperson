import random
import time
from typing import List

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


def mutate(individual: TSPSolution) -> TSPSolution:
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
    gnome_part_2 = [individual2.route[a] for a in range(len(individual2.route)) if individual2.route[a] not in gnome_part_1]

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


def genetic_algorithm_mutation_only(cities: list[City], time_limit: int):
    POPULATION_SIZE = 100
    ELITE_SIZE = 10

    population = initial_generation(cities, POPULATION_SIZE)

    start_time = time.time()

    while time.time() - start_time < time_limit:
        next_generation = []
        for individual in population:
            while True:
                child = mutate(individual)
                if child.cost < individual.cost:
                    next_generation.append(child)
                    break
                elif random.random() < 0.5:
                    next_generation.append(child)
                    break

        population = next_generation

    end_time = time.time()
    print(f"Time taken: {end_time - start_time}")
    return min(population, key=lambda x: x.cost)

