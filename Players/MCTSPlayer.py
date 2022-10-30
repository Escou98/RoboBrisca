import math

from Players.MCTSNode import MCTSNode
from Game.ForwardModel import ForwardModel
from Game.Heuristic import Heuristic
from Players.Player import Player


class MCTSPlayer(Player):
    def __init__(self):
        self.forward_model = ForwardModel()
        self.heuristic = Heuristic()

    def think(self, observation, budget):
        iterations = 10
        root = MCTSNode(None, None, observation)
        root.expand(self.forward_model)
        for i in range(iterations):
            current = root
            while not current.is_leaf():
                current = current.get_best_child()
            if not current.has_been_visited():
                current.rollout(self.forward_model)
            else:
                current.expand(self.forward_model)
        best_child = root.get_best_child()
        return best_child.action

    def __str__(self):
        return "OSLAPlayer"
