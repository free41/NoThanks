import random
from itertools import groupby
from operator import itemgetter


N_PLAYERS = 4


class Player:

    def __init__(self, n_tokens, player_number):
        self.hand = []
        self.tokens = n_tokens
        self.player_number = player_number
        self.last_score = -1* n_tokens

    def __str__(self):

        s = "Player: {}".format(self.player_number)
        s += "  Tokens: {}".format(self.tokens)
        s += "  Score: {}".format(self.calc_score())
        for seq in self.get_sequences():
            s += str(seq)

        return s

    def has_neighbor(c):
        # checks if c will make a sequence with an existing card in hand. 
        return (c - 1) in self.hand or (c + 1) in self.hand

    def calc_score(self, test_card=None):
        sequences = self.get_sequences(test_card)
        score = 0
        for s in sequences:
            score += s[0]
        return score - self.tokens
    
    def add_card_and_tokens(self, card, tokens):
        self.last_score = self.calc_score()
        self.hand.append(card)
        self.tokens += tokens

    def get_sequences(self,c=None):
        
        test_hand = [h for h in self.hand]
        if c:
            test_hand.append(c)
        test_hand.sort()
        sequences = []
        for k, g in groupby(enumerate(test_hand), lambda i_x: i_x[0] - i_x[1]):
            sequences.append(sorted(list(map(itemgetter(1), g))))

        return sequences

    def get_state(self):

        state = {
            "hand": self.hand.copy(),
            "tokens" : self.tokens,
            "score" : self.calc_score(),
            "score_delta": self.calc_score() - self.last_score
        }
        return state
    
    def no_thanks():
        if self.tokens > 0:
            self.last_score = self.calc_score()
            self.tokens -= 1
        else:
            raise ValueError("User cannot have have negative tokens")
        
    
class Deck:
    def __init__(self):
        deck = list(range(3,36))
        random.shuffle(deck)
        self.deck = deck[:-9]
        self.dropped = deck[-9:]
        self.taken = []

        self.tokens = 0
    
    def get_flipped(self):
        if self.has_cards():
            return self.deck[-1]
        else:
            return 0

    def take_card(self):
        tokens = self.tokens
        card = self.deck.pop()

        self.tokens = 0
        self.taken.append(card)
        return (card, tokens)

    def has_cards(self):
        return len(self.deck) > 0
    
    def no_thanks(self):
        self.tokens += 1
    


class Game:

    def __init__(self, n_players=4):

        # Player Setup
        if 3 > n_players > 7:
            return Error("Player count must be between 3 and 7 inclusive. You provided {}".format(n_players))
        
        self.n_players = n_players
        self.players = []
        ptot = {
            3:11,
            4:11,
            5:11,
            6:9,
            7:7
        }

        for i in range(0, self.n_players):
            self.players.append(Player(ptot[n_players], i))
        
        # deck setup
        self.deck = Deck()
        self.current_player_index = 0
        self.turn_counter = 0

        self.game_log = []

    def get_turn_index(self):
        return self.turn_counter%self.n_players

    def get_state(self):
        player_scores = [(p.player_number, p.calc_score()) for p in self.players]
        player_scores.sort(key=lambda x : x[1])

        state = {
            "flipped_card" : self.deck.get_flipped(),
            "tokens_on_card": self.deck.tokens,
            "player_states" : [p.get_state() for p in self.players],
            "player_positions" : [p[0] for p in player_scores],
            "player_turn_index" : self.get_turn_index()
        }
        return state
    
    def player_action(self, choice):
        player = self.players[self.get_turn_index()]
        old_score = player.calc_score()
        if choice >= 0:
            card, tokens = self.deck.take_card()
            player.add_card_and_tokens(card, tokens)
        else:
            player.tokens -= 1
            self.deck.no_thanks()
            self.turn_counter +=1
        new_score = player.calc_score()
        return old_score - new_score


if __name__ == '__main__':
    input("Ready?")
    game = Game(N_PLAYERS)
    winner = game.play_random_game()
    for p in game.players:
        print(p)
    game_state = game.get_state()
    
    print(encode_state(game_state))
    


