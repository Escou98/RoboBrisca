class SergiHeuristic:

    def get_score(self, observation, player_id):

        if observation.playing_cards.len() == 0:
            return 0
        if player_id >= observation.playing_cards.len():
            return 0
        points = 0

        if observation.playing_cards.len() == 1:
            points += self.real_value(observation.playing_cards.get_card(0))
        elif observation.playing_cards.len() == 2:
            # No tiene en cuenta la recompensa que se puede llevar, solo si puede ganar o no
            # Lo mejor sería penalizar el intentar ganar cuando la recompensa es 0
            # region BEHAVIOUR 1
            if self.card_can_win(observation, observation.playing_cards.get_card(player_id)):
                ordered_played_cards = self.max_order_cards_by_value(observation.playing_cards.get_cards())
                # Its positive but prioritize play the lower card that win this round
                points += self.sum_cards_value(observation.playing_cards.get_cards()) / \
                    ordered_played_cards[0] - ordered_played_cards[1]
            else:
                # Less points when higher is the card played
                points -= self.real_value(observation.playing_cards.get_card(player_id))
            # endregion
        elif observation.playing_cards.len() == 3:
            # If your teammate can win your opponent
            if self.is_better_card(observation.playing_cards.get_card(0),
                                   observation.playing_cards.get_card(1),
                                   observation.trump_card,
                                   observation.playing_cards.get_card(0)):
                # Penalize higher cards, both if you can use lower card than your mate or not is correct
                points -= self.real_value(observation.playing_cards.get_card(player_id))
            else:
                # region BEHAVIOUR1
                if self.card_can_win(observation, observation.playing_cards.get_card(player_id)):
                    ordered_played_cards = self.max_order_cards_by_value(observation.playing_cards.get_cards())
                    # Its positive but prioritize play the lower card that win this round
                    points += self.sum_cards_value(observation.playing_cards.get_cards()) / \
                              self.real_value(ordered_played_cards[0]) - self.real_value(ordered_played_cards[1])
                else:
                    # Less points when higher is the card played
                    points -= self.real_value(observation.playing_cards.get_card(player_id))
                # endregion
        else:
            # If your teammate can win your opponents
            if self.is_better_card(observation.playing_cards.get_card(1),
                                   observation.playing_cards.get_card(0),
                                   observation.trump_card,
                                   observation.playing_cards.get_card(0)) and \
                self.is_better_card(observation.playing_cards.get_card(1),
                                   observation.playing_cards.get_card(2),
                                   observation.trump_card,
                                   observation.playing_cards.get_card(0)):

                # Penalize higher cards, both if you can use lower card than your mate or not is correct
                points -= self.real_value(observation.playing_cards.get_card(player_id))
            else:
                # region BEHAVIOUR1
                if self.card_can_win(observation, observation.playing_cards.get_card(player_id)):
                    ordered_played_cards = self.max_order_cards_by_value(observation.playing_cards.get_cards())
                    # Its positive but prioritize play the lower card that win this round
                    points += self.sum_cards_value(observation.playing_cards.get_cards()) / \
                              self.real_value(ordered_played_cards[0]) - self.real_value(ordered_played_cards[1])
                else:
                    # Less points when higher is the card played
                    points -= self.real_value(observation.playing_cards.get_card(player_id))
                # endregion

        return points

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
            return 11
        if card.get_number() == 3:
            return 10
        if card.get_number() == 12:
            return 4
        if card.get_number() == 11:
            return 3
        if card.get_number() == 10:
            return 2
        return card.get_number()