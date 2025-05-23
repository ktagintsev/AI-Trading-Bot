import random
import numpy as np
from utils import quality, downsample
from config import bounds, timeframes, settings

def simulated_annealing(price_series, log=None, setting=None):
    """
    Implements the Simulated Annealing (SA) algorithm for optimization.

    Args:
        price_series (list or np.ndarray): The input price series data.
        log (list, optional): A list to store the best fitness value at each evaluation. Defaults to None.
        setting (dict, optional): A dictionary containing SA-specific settings. Defaults to the first setting in `settings["SA"]`.

    Returns:
        tuple: A tuple containing:
            - best_sol (np.ndarray): The best solution found by the algorithm.
            - best_fit (float): The fitness value of the best solution.
            - best_timeframe (int): The timeframe corresponding to the best solution.
    """
    if setting is None:
        setting = settings["SA"][0]  # Use default settings if none are provided.

    # Extract algorithm parameters from the settings.
    MAX_EVALS = setting["MAX_EVALS"]  # Maximum number of evaluations.
    initial_temp = setting["initial_temp"]  # Initial temperature for the annealing process.
    cooling_rate = setting["cooling_rate"]  # Cooling rate for temperature reduction.
    perturb_scale = setting["perturb_scale"]  # Scale of perturbations for generating new solutions.

    eval_count = 0  # Counter for the number of evaluations performed.
    dim = len(bounds)  # Dimensionality of the problem (based on bounds).

    def random_solution():
        """
        Generates a random solution within the bounds.

        Returns:
            np.ndarray: A randomly generated solution.
        """
        sol = [random.uniform(low, high) for (low, high) in bounds[:-1]]
        sol.append(random.randint(0, len(timeframes) - 1))
        return np.array(sol)

    def perturb(sol):
        """
        Perturbs a given solution to generate a new solution.

        Args:
            sol (np.ndarray): The current solution.

        Returns:
            np.ndarray: A new solution generated by perturbing the current solution.
        """
        new_sol = sol.copy()
        idx = random.randint(0, dim - 2)  # Select a random dimension to perturb.
        low, high = bounds[idx]
        scale = (high - low) * perturb_scale  # Scale the perturbation based on the bounds.
        new_sol[idx] += np.random.normal(0, scale)  # Apply a random perturbation.
        new_sol[idx] = max(min(new_sol[idx], high), low)  # Ensure the value stays within bounds.
        new_sol[-1] = int(round(max(min(sol[-1], bounds[-1][1]), bounds[-1][0])))  # Adjust the timeframe index.
        return new_sol

    # Initialize the current solution and its fitness.
    curr_sol = random_solution()
    curr_fit = quality(curr_sol[:-1], downsample(price_series, timeframes[int(curr_sol[-1])]))
    best_sol, best_fit = curr_sol.copy(), curr_fit  # Track the best solution and fitness.
    temp = initial_temp  # Set the initial temperature.

    if log is not None:
        log.append(best_fit)  # Log the initial best fitness.

    # Main loop: iterate until the maximum number of evaluations is reached.
    while eval_count < MAX_EVALS:
        new_sol = perturb(curr_sol)  # Generate a new solution by perturbing the current solution.
        new_fit = quality(new_sol[:-1], downsample(price_series, timeframes[int(new_sol[-1])]))  # Evaluate the new solution.
        eval_count += 1  # Increment the evaluation counter.

        # Accept the new solution based on the Metropolis criterion.
        if new_fit > curr_fit or random.random() < np.exp((new_fit - curr_fit) / temp):
            curr_sol, curr_fit = new_sol, new_fit  # Update the current solution and fitness.

            # Update the best solution if the new solution is better.
            if new_fit > best_fit:
                best_sol, best_fit = new_sol.copy(), new_fit

        if log is not None:
            log.append(best_fit)  # Log the best fitness value.

        temp *= cooling_rate  # Reduce the temperature.

    # Print the final result of the algorithm.
    print(f"SA Done | Best Profit: ${best_fit:.2f} | TF: {timeframes[int(best_sol[-1])]}h")
    return best_sol, best_fit, timeframes[int(best_sol[-1])]  # Return the best solution found.