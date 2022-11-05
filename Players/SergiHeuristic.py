from Game.Card import Card
from Game.CardCollection import CardCollection


class SergiHeuristic:

    def __init__(self):
        self.remaining_deck = CardCollection()
        self.new_deck()

    def new_deck(self):
        l_types = ["O", "E", "C", "B"]
        l_numbers = [1, 2, 3, 4, 5, 6, 7, 10, 11, 12]
        self.remaining_deck.clear()
        for card_type in l_types:
            for number in l_numbers:
                self.remaining_deck.add_card(Card(card_type, number))

    def remove_cards(self, cards):
        for card in cards:
            try:
                self.remaining_deck.remove(card)
            except:
                return

    def get_score(self, observation, player_id):

        if observation.playing_cards.len() == 0:
            return 0
        if player_id >= observation.playing_cards.len():
            return 0

        # Remove played cards from remaining deck
        self.remove_cards(observation.playing_cards.get_cards())

        # points of played cards
        cards = observation.playing_cards.get_cards()
        points = 0
        for card in cards:
            points += card.get_value()

        player_card = observation.playing_cards.get_last_card()
        first_card = observation.playing_cards.get_card(0)
        if observation.playing_cards.len() == 1:
            score = points
        elif observation.playing_cards.len() == 2:
            other_player_card = observation.playing_cards.get_card(0)
            if self.is_better_card(other_player_card, player_card, observation.trump_card, first_card):
                score = -points
            else:
                score = points - self.real_value(cards[1])
        elif observation.playing_cards.len() == 3:
            other_player_card = observation.playing_cards.get_card(1)
            my_mate_card = observation.playing_cards.get_card(0)
            if self.is_better_card(other_player_card, player_card, observation.trump_card, first_card) and \
                    self.is_better_card(other_player_card, my_mate_card, observation.trump_card, first_card):
                score = -points
            else:
                score = points - (self.real_value(cards[2]) *
                                  self.prob_of_best_combinations(observation,
                                                                 self.remaining_deck.get_cards(),
                                                                 self.sum_cards_value(observation.playing_cards.get_cards()[:-1])))
        else:
            other_player_card1 = observation.playing_cards.get_card(0)
            other_player_card2 = observation.playing_cards.get_card(2)
            my_mate_card = observation.playing_cards.get_card(1)
            if (self.is_better_card(other_player_card1, player_card, observation.trump_card, first_card) and
                self.is_better_card(other_player_card1, my_mate_card, observation.trump_card, first_card)) or \
                    (self.is_better_card(other_player_card2, player_card, observation.trump_card, first_card) and
                     self.is_better_card(other_player_card2, my_mate_card, observation.trump_card, first_card)):
                score = -points
            else:
                score = points - self.real_value(cards[3])

        return score

    def max_order_cards_by_value(self, cards):
        return sorted(cards, key=lambda x: self.real_value(x), reverse=True)

    def sum_cards_value(self, cards):
        sum = 0
        for card in cards:
            sum += card.get_value()
        return sum

    def card_can_win(self, obs, card):
        for other_card in obs.playing_cards.get_cards():
            if self.is_better_card(other_card, card, obs.trump_card, obs.playing_cards.get_card(0)):
                return False
        return True

    def player_can_win(self, obs, id):

        # Player hand and table cards before playing last turn
        cards_on_table = obs.clone_list(obs.playing_cards.get_cards())
        cards_on_hand = obs.clone_list(obs.hands[id].get_cards())
        cards_on_hand.append(cards_on_table.pop())

        for chand in cards_on_hand:
            can_win = True
            for ctable in cards_on_table:
                if not self.is_better_card(chand, ctable, obs.trump_card, obs.playing_cards.get_card(0)):
                    can_win = False
            if can_win: return True

    def is_better_card(self, card, other_card, trump, round):
        if card.get_type() == other_card.get_type():
            return self.real_value(card) >= self.real_value(other_card)
        elif card.get_type() == trump.get_type():
            return True
        elif card.get_type() == round.get_type():
            if other_card.get_type() == trump.get_type():
                return False
            else:
                return True
        else:
            if other_card.get_type() == trump.get_type() or other_card.get_type() == round.get_type():
                return False
            else:
                return self.real_value(card) >= self.real_value(other_card)

    def real_value(self, card):

        if card.get_number() == 1:
            return 12
        if card.get_number() == 3:
            return 11
        if card.get_number() == 12:
            return 10
        if card.get_number() == 11:
            return 9
        if card.get_number() == 10:
            return 8
        return card.get_number()

    def prob_of_best_combinations(self, obs, disponible_cards, threshold: "Value to overcome"):
        if len(disponible_cards) <= 1:
            return 1
        dispo_copy = obs.clone_list(disponible_cards)
        max_ordered_list = []
        while not dispo_copy:
            max_ordered_list.append(self.return_and_delete_best_card(dispo_copy))

        n = len(max_ordered_list)
        possible_combinations = (n**2-n) / 2
        better_combinations = 0
        if possible_combinations == 0:
            return 1
        i = 0
        for card in max_ordered_list[:-1]:
            for other_card in max_ordered_list[i+1:]:
                if (card.get_value() + other_card.get_value()) > threshold:
                    better_combinations += 1
                else:
                    break
            i += 1

        return better_combinations / possible_combinations

    def return_and_delete_best_card(self, cards):
        best_card = None
        for card in cards:
            if best_card is None or card.get_value() > best_card.get_value():
                best_card = card
        cards.remove(best_card)
        return best_card

