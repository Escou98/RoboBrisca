import math
import random
from Players.SergiHeuristic import SergiHeuristic



class MCTSNode:
    def __init__(self, action, parent, observation):
        self.action = action  # the move that got us to this node - "None" for the root node
        self.parent = parent  # "None" for the root node
        self.children = []
        self.wins = 0
        self.visits = 0
        self.observation = observation
        self.big_number = 100000
        self.myturn = self.get_turn()
        self.mate_turn = self.get_mate_turn()
        self.heuristic = SergiHeuristic()

    def get_turn(self):
        if self.observation.turn == 0:
            return 3
        else:
            return self.observation.turn - 1

    def get_mate_turn(self):
        turn = self.myturn + 2
        if turn > 3:
            turn = 0
        return turn

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
        new_obs = self.observation.clone()
        while not new_obs.is_terminal():
            # Counting every turn as iteration yet
            if new_obs.turn == self.myturn:
                new_obs = new_obs.get_randomized_clone()
                self.wins += self.heuristic.get_score(new_obs, self.myturn)
            forward_model.play(new_obs, random.choice(new_obs.get_list_actions()), self.heuristic)

        forward_model.check_winner(new_obs)

        phi = 1
        if new_obs.winner == self.myturn:
            phi = 4
        self.wins += forward_model.get_points_player(self.myturn, new_obs) * phi
        self.wins += forward_model.get_points_player(self.mate_turn, new_obs) * phi
        self.backpropagate()

    def play_best_action(self, fm, obs):
        best_action = None
        best_reward = None

        for action in obs.get_list_actions():
            n_obs = obs.clone()
            player_id = obs.turn
            fm.play(n_obs, action, self.heuristic)
            reward = self.heuristic.get_score(n_obs, player_id)
            if best_reward is None or reward > best_reward:
                best_reward = reward
                best_action = action
        fm.play(obs, best_action, self.heuristic)

    def backpropagate(self):
        current = self.parent
        while current is not None:
            current.update(self.wins)
            current = current.parent

    def clear_children(self):
        for child in self.children:
            self.children.remove(child)

    def randomize_observation(self):
        self.observation = self.observation.get_randomized_clone()

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
