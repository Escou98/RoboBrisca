# --------------------------------------------------------
# - RoboBrisca
# - BriscaGame
# - Implemented by: Raul Montoliu (Dic 2021)
# --------------------------------------------------------

import random
import func_timeout

from Game.Card import Card
from Game.CardCollection import CardCollection


class BriscaGame:
    def __init__(self):
        self.save_game = False
        self.save_file = None

    # Initilize game state
    def reset(self, game_state, player_id_as_first):
        self.save_file = None
        self.create_main_deck(game_state.main_deck)
        game_state.n_players = 4

        # create empty hands
        game_state.hands.clear()
        for p in range(game_state.n_players):
            hand = CardCollection()
            game_state.hands.append(hand)

        # draw three cards to each player
        for i in range(3):
            for p in range(game_state.n_players):
                card = game_state.main_deck.draw()
                game_state.hands[p].add_card(card)

        # The last card on the main deck is the leader type
        game_state.trump_card = game_state.main_deck.get_last_card()

        # cleate empty won cards
        for p in range(game_state.n_players):
            won = CardCollection()
            game_state.won_cards.append(won)

        # who play as first
        game_state.turn = player_id_as_first

        # empty playing cards
        game_state.playing_cards.clear()

    def create_main_deck(self, deck):
        l_types = ["O", "E", "C", "B"]
        l_numbers = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]
        deck.clear()
        for card_type in l_types:
            for number in l_numbers:
                deck.add_card(Card(card_type, number))

        deck.shuffle()

    # run the game
    def run(self, game_state, forward_model, heuristic, l_players, budget, verbose, controlling_time):
        # Brisca is a 4 players game, then 1st bot acts as player 0 and 2, and 2nd one acts as 1 and 3.
        players = [l_players[0], l_players[1], l_players[0], l_players[1]]

        if self.save_game:
            self.save_file.write(str(game_state.main_deck) + ", " + str(game_state.turn) + "\n")
            for hand in game_state.hands:
                self.save_file.write(str(hand) + "\n")

        # run players' turns while game is not finished
        while not game_state.is_terminal():
            for i in range(game_state.n_players):
                prev_turn = game_state.turn

                action, reward = self.player_turn(game_state, forward_model, heuristic, players[game_state.turn],
                                                  budget, verbose, controlling_time)

                if self.save_game:
                    self.save_file.write(str(prev_turn) + ", " + str(action) + ", " + str(reward) + "\n")

                if game_state.is_terminal():
                    break

        forward_model.check_winner(game_state)
        self.save_file.close()

    # ---------------------------------------------------------------------------
    # Performs a player turn
    # ---------------------------------------------------------------------------
    def player_turn(self, gs, fm, ht, pl, budget, verbose, controlling_time):
        if verbose:
            print("")
            print("---------------------------------------- ")
            print("Player " + str(gs.turn) + " [" + str(pl) + "] turn")
            print("---------------------------------------- ")
            print(str(gs))

        observation = gs.get_observation()  # Observable part of the GameState

        # When controlling_time is True, the player has budget seconds to thinks.
        # If it last more than this time, a random action is played instead.
        # It is responsability of the Player to internally control the processinf time.
        if controlling_time:
            try:
                action = func_timeout.func_timeout(budget, self.player_thinking, args=[pl, observation, budget])
            except func_timeout.FunctionTimedOut:
                if verbose:
                    print("Ups, too many time thinking. A random action is selected instead !!!")
                action = self.get_random_action(observation)
        else:
            action = self.player_thinking(pl, observation, budget)

        if verbose:
            print("Player " + str(gs.turn) + " selects [" + str(action) + "]")

        reward = fm.play(gs, action, ht)

        if verbose:
            print("Reward: " + str(reward))

        return action, reward

    # ---------------------------------------------------------------------------
    # The player thinkg.
    # Returns the action to be played
    # ---------------------------------------------------------------------------
    def player_thinking(self, pl, observation, budget):
        return pl.think(observation, budget)

    # ---------------------------------------------------------------------------
    # Returns a random action
    # ---------------------------------------------------------------------------
    def get_random_action(self, observation):
        l_actions = observation.get_list_actions()
        return random.choice(l_actions)

    def save_game_on(self, filename):
        self.save_game = True
        self.save_file = open(filename, "w")
