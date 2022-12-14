#!/usr/bin/python3
import itertools
import time
from contextlib import suppress
from typing import List

from genetic_algorithm import initial_generation, mutate, breed_population
from models import Node
from TSPClasses import *
from queue import PriorityQueue


class TSPSolver:
    def __init__(self, gui_view):
        self._scenario = None

    def setupWithScenario(self, scenario: Scenario):
        self._scenario = scenario

    """ 
    <summary>
    This is the entry point for the default solver
    which just finds a valid random tour.  Note this could be used to find your
    initial BSSF.
    </summary>
    <returns>results dictionary for GUI that contains three ints: cost of solution, 
    time spent to find solution, number of permutations tried during search, the 
    solution found, and three null values for fields not used for this 
    algorithm</returns> 
    """

    def defaultRandomTour(self, time_allowance=60.0):
        cities = self._scenario.get_cities()
        ncities = len(cities)
        foundTour = False
        count = 0
        bssf = None
        start_time = time.time()
        while not foundTour and time.time() - start_time < time_allowance:
            # create a random permutation
            perm = np.random.permutation(ncities)
            route = [cities[perm[i]] for i in range(ncities)]
            bssf = TSPSolution(route)
            count += 1
            if bssf.cost < np.inf:
                # Found a valid route
                foundTour = True

        end_time = time.time()

        return {
            "cost": bssf.cost if foundTour else math.inf,
            "time": end_time - start_time,
            "count": count,
            "soln": bssf,
            "max": None,
            "total": None,
            "pruned": None,
        }

    def greedy(self, time_allowance=60.0, sample_size=0):
        """
        This is the entry point for the greedy algorithm

        Time complexity: O(n^2)
        Space complexity: O(n)

        :param sample_size:
        :param time_allowance:
        :return: results dictionary for GUI that contains three ints: cost of best solution,
        time spent to find best solution, total number of solutions found, the best
        solution found, and three null values for fields not used for this
        algorithm
        """
        start_time = time.time()

        cities = self._scenario.get_cities().copy()
        random.shuffle(cities)
        sample = []

        with suppress(StopIteration):
            for start in cities:
                route = [start]
                remaining = cities.copy()
                remaining.remove(start)

                while remaining:
                    if time.time() - start_time > time_allowance:
                        raise StopIteration
                    nearest = min(remaining, key=lambda city: start.costTo(city))
                    route.append(nearest)
                    remaining.remove(nearest)
                    start = nearest

                solution = TSPSolution(route)

                if solution.cost < np.inf:
                    sample.append(solution)

        end_time = time.time()

        sample.sort(key=lambda solution: solution.cost)
        bssf = sample[0] if sample else None

        if sample_size <= 0:
            return {
                "cost": bssf.cost,
                "time": end_time - start_time,
                "count": 1,
                "soln": bssf,
                "max": None,
                "total": None,
                "pruned": None,
            }
        else:
            return sample[:sample_size]

    def branch_and_bound(self, time_allowance=60.0):
        """
        This is the entry point for the branch-and-bound algorithm

        Time Complexity: O(n^3 * 2^n)
        Space Complexity: O(n^3 * 2^n)

        :param time_allowance: float
        :return: results dictionary for GUI that contains three ints: cost of best solution,
        time spent to find best solution, total number solutions found during search (does
        not include the initial BSSF), the best solution found, and three more ints:
        max queue size, total number of states created, and number of pruned states.
        """

        start_time = time.time()

        queue = PriorityQueue()
        cities: List[City] = self._scenario.get_cities().copy()
        # TC: O(n), SC: O(n)
        city_map = {city.index: city for city in cities}
        ncities = len(cities)

        count = 0
        max_queue_size = 0
        total_states = 0
        pruned_states = 0

        # Create initial matrix
        # TC: O(n^2), SC: O(n^2)
        matrix = np.full((ncities, ncities), np.inf)
        for i, j in itertools.product(range(ncities), range(ncities)):
            matrix[i, j] = city_map[i].costTo(city_map[j])

        # Create initial node
        # TC: O(1), SC: O(1)
        node = Node(matrix, [cities[0]], 0)
        queue.put(node)

        # Create initial BSSF
        # TC: O(n^2), SC: O(n)
        bssf = self.greedy(time_allowance)["soln"]

        # TC: O(b^n), SC: O(b^n)
        while not queue.empty() and time.time() - start_time < time_allowance:
            node = queue.get()

            max_queue_size = max(max_queue_size, queue.qsize())

            if node.cost >= bssf.cost:
                pruned_states += 1
                continue

            if len(node.path) == ncities:
                count += 1
                bssf = TSPSolution(node.path)
                continue

            current_city = node.path[-1]
            i = current_city.index
            # TC: O(n), SC: O(1)
            for j, city in city_map.items():
                if city in node.path:
                    continue

                new_cost = node.cost + node.matrix[i, j]

                # TC: O(n^2), SC: O(n^2)
                new_matrix = node.matrix.copy()
                new_matrix[i, :] = np.inf
                new_matrix[:, j] = np.inf
                new_matrix[j, i] = np.inf

                # TC: O(n), SC: O(1)
                for k in range(ncities):
                    min_cell = np.min(new_matrix[k, :])
                    if min_cell != np.inf:
                        new_matrix[k, :] -= min_cell
                        new_cost += min_cell

                # TC: O(n), SC: O(1)
                for k in range(ncities):
                    min_cell = np.min(new_matrix[:, k])
                    if min_cell != np.inf:
                        new_matrix[:, k] -= min_cell
                        new_cost += min_cell

                new_path = node.path.copy()
                new_path.append(city)

                new_node = Node(new_matrix, new_path, new_cost)
                # TC: O(log(b^n)), SC: O(1)
                queue.put(new_node)

                total_states += 1

        end_time = time.time()

        return {
            "cost": bssf.cost,
            "time": end_time - start_time,
            "count": count,
            "soln": bssf,
            "max": max_queue_size,
            "total": total_states,
            "pruned": pruned_states,
        }

    def fancy(self, time_allowance=60.0):
        """
        Genetic algorithm implementation for TSP

        Time complexity: O(an^2) ( a = number of iterations that can be run in time_allowance)
        Space complexity: O(n^2)

        :param time_allowance: float
        :return:
        """
        POPULATION_SIZE = 200
        ELITE_SIZE = 20

        assert ELITE_SIZE < POPULATION_SIZE

        start_time = time.time()

        greedy_sample = self.greedy(time_allowance, sample_size=ELITE_SIZE)  # T: O(n^2), S: O(n)
        print(len(greedy_sample))
        cities = self._scenario.get_cities().copy()  # T: O(n), S: O(n)
        population = initial_generation(cities, POPULATION_SIZE - len(greedy_sample))  # T: O(n), S: O(n)
        population.extend(greedy_sample)

        bssf_updates = 0
        bssf = min(population, key=lambda solution: solution.cost)  # T: O(n)
        generations = 1

        while time.time() - start_time < time_allowance:  # run time_allowance seconds
            population = breed_population(population, ELITE_SIZE)  # T: O(n^2), S: O(n^2)
            next_generation = []
            for individual in population:
                while True:
                    child = mutate(individual)  # T: O(n), S: O(n)
                    if child.cost < individual.cost:
                        next_generation.append(child)
                        break
                    elif random.random() < 0.01:
                        next_generation.append(child)
                        break

                if child.cost < bssf.cost:
                    bssf_updates += 1
                    bssf = child

            population = next_generation
            generations += 1

        end_time = time.time()
        return {
            "cost": bssf.cost,
            "time": end_time - start_time,
            "count": bssf_updates,
            "soln": bssf,
            "max": POPULATION_SIZE,
            "total": generations,
            "pruned": bssf_updates,
        }
