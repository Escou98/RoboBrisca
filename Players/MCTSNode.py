import math
import random
from Game.Heuristic import Heuristic


class MCTSNode:
    def __init__(self, action, parent, observation):
        self.action = action  # the move that got us to this node - "None" for the root node
        self.parent = parent  # "None" for the root node
        self.children = []
        self.wins = 0
        self.visits = 0
        self.observation = observation
        self.big_number = 100000
        self.score = 0
        self.heuristic = Heuristic()

    def expand(self, forward_model):
        actions = self.observation.get_list_actions()
        for action in actions:
            obs = self.observation.clone()
            forward_model.play(obs, action, self.heuristic)
            self.children.append(MCTSNode(action, self, obs))

    def get_ucb(self):
        if self.visits == 0:
            return self.big_number + random.random()
        else:
            return self.wins / self.visits + math.sqrt(2 * math.log(self.parent.visits) / self.visits)

    def get_best_child(self):
        best_child = None
        best_ucb = -self.big_number
        for child in self.children:
            ucb = child.get_ucb()
            if ucb > best_ucb:
                best_child = child
                best_ucb = ucb
        return best_child

    def rollout(self, forward_model):
        i = 0
        max_iter = 10
        new_obs = self.observation.clone()
        forward_model.play(new_obs, self.action, self.heuristic)
        while i < max_iter and not new_obs.is_terminal():
            # Counting every turn as iteration yet
            forward_model.play(new_obs, random.choice(new_obs.get_list_actions()), self.heuristic)
            i += 1
        self.score = self.heuristic.get_score(new_obs, self.observation.turn)
        self.backpropagate()

    def backpropagate(self):
        current = self.parent
        while current is not None:
            current.update(self.score)
            current = current.parent

    def add_child(self, action, observation):
        new_node = MCTSNode(action, self, observation)
        self.children.append(new_node)
        return new_node

    def update(self, result):
        self.visits += 1
        self.wins += result

    def is_leaf(self):
        return len(self.children) == 0

    def has_been_visited(self):
        return self.visits > 0

    def has_parent(self):
        return self.parent is not None

    def get_observation(self):
        return self.observation
