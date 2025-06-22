# agents/rebalancer_agent.py
import numpy as np
from envs.data_loader import fetch_price_data
from envs.portfolio_env import PortfolioEnv

class QLearningRebalancer:
    """
    Stateless Q-learning on a discretized action space.
    We treat each state (weights+recent returns) as a key in Q-table.
    """
    def __init__(
        self,
        prices: np.ndarray,
        lr: float = 0.1,
        gamma: float = 0.99,
        eps: float = 0.1,
        turnover_cost: float = 0.001
    ):
        self.env = PortfolioEnv(prices, turnover_cost=turnover_cost)
        self.lr = lr
        self.gamma = gamma
        self.eps = eps
        self.q_table: dict = {}  # { state_tuple: { action_tuple: q_value } }

    def _state_key(self, state: np.ndarray) -> tuple:
        # round to 3 decimals to reduce keys
        return tuple(np.round(state, 3).tolist())

    def choose_action(self, state_key: tuple):
        actions = self.q_table.get(state_key, {})
        if not actions or np.random.rand() < self.eps:
            # explore
            return tuple(np.round(self.env.sample_random_action(), 3).tolist())
        # exploit
        return max(actions.items(), key=lambda x: x[1])[0]

    def train(self, episodes: int = 500):
        for _ in range(episodes):
            state = self.env.reset()
            s_key = self._state_key(state)
            done = False
            while not done:
                a_key = self.choose_action(s_key)
                action = np.array(a_key)
                next_state, reward, done, _ = self.env.step(action)
                ns_key = self._state_key(next_state)

                # init tables
                self.q_table.setdefault(s_key, {})\
                            .setdefault(a_key, 0.0)
                self.q_table.setdefault(ns_key, {})

                # Q-learning update
                q_next_max = max(self.q_table[ns_key].values(), default=0.0)
                td = reward + self.gamma * q_next_max - self.q_table[s_key][a_key]
                self.q_table[s_key][a_key] += self.lr * td

                s_key = ns_key

    def get_recommendation(self) -> np.ndarray:
        """
        After training, reset env to final date and ask for best action.
        """
        # fast-forward env to last time step
        self.env.reset()
        for _ in range(self.env.T - 1):
            # step with current weights (no turnover cost effect here)
            self.env.step(self.env.weights)
        last_state = self.env._state()
        best_a = self.choose_action(self._state_key(last_state))
        return np.array(best_a)

    def evaluate(self, weights: np.ndarray) -> float:
        """
        Compute cumulative return of a fixed weight strategy.
        """
        # simulate
        self.env.reset()
        for _ in range(self.env.T - 1):
            self.env.step(weights)
        return self.env.value


def build_and_train(
    tickers: list[str],
    start: str = "2020-01-01",
    end: str = None,
    episodes: int = 500
):
    prices, dates = fetch_price_data(tickers, start, end)
    agent = QLearningRebalancer(prices)
    agent.train(episodes)
    rec_weights = agent.get_recommendation()
    # equal-weight static benchmark
    static_weights = np.ones(len(tickers)) / len(tickers)
    rec_perf = agent.evaluate(rec_weights)
    stat_perf = agent.evaluate(static_weights)
    return {
        "dates": dates.astype(str).tolist(),
        "tickers": tickers,
        "recommended_weights": rec_weights.tolist(),
        "static_weights": static_weights.tolist(),
        "performance": {
            "recommended": rec_perf,
            "static": stat_perf
        }
    }
