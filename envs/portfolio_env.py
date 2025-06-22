# envs/portfolio_env.py
import numpy as np

class PortfolioEnv:
    """
    A simple simulator for N assets over T time steps.

    - prices: np.ndarray of shape (T, N)
    - At each step, you choose a new weight vector (sums to 1)
    - You earn the weighted return, pay a small turnover cost,
      and receive a reward.
    """

    def __init__(self, prices: np.ndarray, turnover_cost: float = 0.001):
        self.prices = prices
        self.T, self.N = prices.shape
        self.turnover_cost = turnover_cost
        self.reset()

    def reset(self):
        self.t = 0
        # start equally weighted
        self.weights = np.ones(self.N) / self.N
        self.value = 1.0
        return self._state()

    def _state(self):
        """
        Returns a 2N-length vector: [current_weights (N), last_returns (N)].
        Clamps t so we never index past T-1.
        """
        idx = min(self.t, self.T - 1)
        if idx == 0:
            last_returns = np.zeros(self.N)
        else:
            last_returns = self.prices[idx] / self.prices[idx - 1] - 1.0
        return np.concatenate([self.weights, last_returns])

    def step(self, new_weights: np.ndarray):
        """
        new_weights: shape (N,), sums to 1
        Returns: (next_state, reward, done, info)
        """
        # compute return based on current t
        idx = min(self.t, self.T - 1)
        if idx == 0:
            ret = np.zeros(self.N)
        else:
            ret = self.prices[idx] / self.prices[idx - 1] - 1.0
        port_ret = np.dot(self.weights, ret)

        # update portfolio value
        self.value *= (1 + port_ret)

        # turnover penalty
        turnover = np.sum(np.abs(new_weights - self.weights))
        cost = turnover * self.turnover_cost

        reward = port_ret - cost

        # update weights/time
        self.weights = new_weights
        self.t += 1

        # done if we've reached or passed T
        done = self.t >= self.T

        # compute the next state (clamped)
        next_state = self._state()
        return next_state, reward, done, {}

    def sample_random_action(self):
        """Random valid weights (Dirichlet) for exploration."""
        w = np.random.dirichlet(np.ones(self.N))
        return w
