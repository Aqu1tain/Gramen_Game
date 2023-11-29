import random
import json


class Deck:
    def __init__(self):
        self.suits = ['Spades', 'Hearts', 'Diamonds', 'Clubs']
        self.values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace']
        self.cards = [Card(suit, value) for suit in self.suits for value in self.values]
        self.shuffle_deck()

    def get_deck(self):
        return self.cards

    def shuffle_deck(self):
        random.shuffle(self.cards)

    def pop_card(self):
        return self.cards.pop(0)

    def is_empty(self):
        return not bool(self.cards)

    def refill_deck(self, discard_pile):
        self.cards = discard_pile.get_discard_pile()
        discard_pile.clear_discard_pile()
        self.shuffle_deck()


class DiscardPile:
    def __init__(self):
        self.discard_pile = []

    def get_discard_pile(self):
        return self.discard_pile

    def add_card(self, card):
        self.discard_pile.append(card)

    def pop_first_card(self):
        return self.discard_pile.pop(-1) if self.discard_pile else None

    def get_first_card(self):
        return self.discard_pile[-1] if self.discard_pile else None

    def clear_discard_pile(self):
        self.discard_pile = []


class Card:
    def __init__(self, suit='Spades', value='Ace'):
        self.suit = suit
        self.value = value

    def get_str_card(self):
        return f'{self.value} of {self.suit}'

    def get_color(self):
        return self.suit


class Player:
    def __init__(self, name='Player1'):
        self.name = name
        self.cards = []

    def get_name(self):
        return self.name

    def get_cards(self):
        return self.cards

    def add_card(self, card):
        self.cards.append(card)

    def pop_card(self, card_pos=0):
        return self.cards.pop(card_pos)


class Game:
    def __init__(self, players_number=3):
        self.players_number = players_number
        self.players = [Player(f'Player{i + 1}') for i in range(self.players_number)]
        self.deck = Deck()
        self.discard_pile = DiscardPile()

    def distribute_cards(self, num=10):
        for player in self.players:
            for _ in range(num):
                player.add_card(self.deck.pop_card())

    def display_players_cards(self):
        for player in self.players:
            print(f"{player.get_name()} : {[card.get_str_card() for card in player.get_cards()]}")

    def display_deck_size(self):
        print(f"The deck contains {len(self.deck.get_deck())} cards")

    def turn(self, player):
        print(f"\n{player.get_name()}'s turn:")
        
        if self.discard_pile.get_discard_pile():
            print(f"First card in discard pile: {self.discard_pile.get_first_card().get_str_card()}")
            choice1 = input("1 to take this card, 2 to draw from the deck, 3 to skip: ")

            if choice1 == "1" and self.discard_pile.get_first_card():
                player.add_card(self.discard_pile.pop_first_card())
                print(f"{player.get_name()} took a card from the discard pile")
            elif choice1 == "2":
                player.add_card(self.deck.pop_card())
                print(f"{player.get_name()} drew a card from the deck")
            else:
                print(f"{player.get_name()} skipped their turn")

        else:
            choice1 = input("2 to draw from the deck, 3 to skip: ")
            
            if choice1 == "2":
                player.add_card(self.deck.pop_card())
                print(f"{player.get_name()} drew a card from the deck")
            else:
                print(f"{player.get_name()} skipped their turn")

        if choice1 != "3":
            self.discard_card(player)

        if self.deck.is_empty():
            print("Deck is empty. Refilling from the discard pile.")
            self.deck.refill_deck(self.discard_pile)
            self.display_deck_size()
        self.save_game()

    def verify_win(self, player):
        for card in player.get_cards():
            if card.suit != player.get_cards()[0].suit:
                return False
        return True

    def discard_card(self, player):
        try:
            print(f"Choose a card to discard from {player.get_name()}'s hand:")
            print(f"Hand: {[card.get_str_card() for card in player.get_cards()]}")
            choice2 = input("Enter the card you want to discard: ")
            card_index = next(i for i, card in enumerate(player.get_cards()) if card.get_str_card() == choice2)
            discarded_card = player.pop_card(card_index)
            self.discard_pile.add_card(discarded_card)
            print(f"{player.get_name()} discarded {discarded_card.get_str_card()} from their hand")
        except StopIteration:
            print("Invalid choice. Try again to enter.")
            self.discard_card(player)

    def launch_game(self):

        if input("Voulez vous ouvrir une sauvegarde ? Y/N \n>") == 'Y':
            self.load_game()
        else:
            self.save_game()
            self.distribute_cards(10)
        self.display_players_cards()
        self.display_deck_size()
            
        while True:
            for player in self.players:
                self.turn(player)
                if self.verify_win(player):
                    print(f"{player.get_name()} wins!")
                    return
                self.display_players_cards()
                self.display_deck_size()

    def save_game(self, filename='saved_game.json'):
        game_state = {
            'players_number': self.players_number,
            'players': [
                {
                    'name': player.name,
                    'cards': [card.get_str_card() for card in player.cards]
                }
                for player in self.players
            ],
            'deck': [card.get_str_card() for card in self.deck.get_deck()],
            'discard_pile': [card.get_str_card() for card in self.discard_pile.get_discard_pile()]
        }

        with open(filename, 'w') as file:
            json.dump(game_state, file, indent=4)
    
    def load_game(self, filename='saved_game.json'):
        with open(filename, 'r') as file:
            game_state = json.load(file)

        self.players_number = game_state['players_number']
        self.players = [Player(player['name']) for player in game_state['players']]
        self.deck = Deck()
        self.discard_pile = DiscardPile()

        for player, player_state in zip(self.players, game_state['players']):
            player.cards = [Card(card.split(' of ')[1], card.split(' of ')[0]) for card in player_state['cards']]

        self.deck.cards = [Card(card.split(' of ')[1], card.split(' of ')[0]) for card in game_state['deck']]
        self.discard_pile.discard_pile = [Card(card.split(' of ')[1], card.split(' of ')[0]) for card in game_state['discard_pile']]

# Create a game with default 3 players and launch the game
game = Game()
game.launch_game()
