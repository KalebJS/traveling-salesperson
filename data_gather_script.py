import random
import sys

import pandas as pd
from PyQt5.QtCore import QPointF
from tqdm import tqdm

from TSPClasses import Scenario
from TSPSolver import TSPSolver


args = sys.argv
solver_function = args[1]


data = []
seed = 1
SCALE = 1.0
diff = "Hard"

data_range = {"x": [-1.5 * SCALE, 1.5 * SCALE], "y": [-SCALE, SCALE]}
xr = data_range["x"]
yr = data_range["y"]


for npoints in tqdm(range(10, 201)):
    random.seed(seed)
    points = []
    while len(points) < npoints:
        x = random.uniform(0.0, 1.0)
        y = random.uniform(0.0, 1.0)
        xval = xr[0] + (xr[1] - xr[0]) * x
        yval = yr[0] + (yr[1] - yr[0]) * y
        points.append(QPointF(xval, yval))

    scenario = Scenario(city_locations=points, difficulty=diff, rand_seed=seed)
    solver = TSPSolver(None)
    solver.setupWithScenario(scenario)
    if solver_function == "fancy":
        result = solver.fancy(600)
    elif solver_function == "greedy":
        result = solver.greedy(600)
    elif solver_function == "brute":
        result = solver.defaultRandomTour(600)
    elif solver_function == "branch":
        result = solver.branch_and_bound(600)
    else:
        raise Exception("Solver function not recognized")

    data.append(
        {
            "# Cities": npoints,
            "Seed": seed,
            "Running time (sec.)": result["time"],
            "Cost of best tour found (*=optimal)": result["cost"],
            "Max # of stored states at a given time": result["max"],
            "# of BSSF updates": result["count"],
            "Total # of states created": result["total"],
            "Total # of states pruned": result["pruned"],
        }
    )


df = pd.DataFrame(data)
df.to_csv(path_or_buf=f"./data/data_10_minutes_{solver_function}.csv", index=False)
