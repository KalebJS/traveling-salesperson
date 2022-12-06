import random
from typing import List

from TSPClasses import City, TSPSolution


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
    population.sort(key=lambda x: x.cost)
    next_generation = list(population[:elite_size])

    CHOOSE_ANY_CHANCE = .01
    ELITE_SIZE_FACTOR = 2

    for _ in range(elite_size, len(population)):
        while True:

            # pick random parent, weighted by cost
            if random.random() < CHOOSE_ANY_CHANCE:
                parent1 = random.choice(population)
                parent2 = random.choice(population)
            else:
                parent1 = random.choice(population[:elite_size * ELITE_SIZE_FACTOR])
                parent2 = random.choice(population[:elite_size * ELITE_SIZE_FACTOR])

            if parent1 != parent2:
                break

        child = breed(parent1, parent2)

        next_generation.append(child)
    return next_generation

