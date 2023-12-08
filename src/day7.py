from collections import defaultdict
from enum import auto, IntEnum
from functools import cached_property
from itertools import product

from .utils import AbstractPuzzleSolver

# Global constants
CARDS_TYPES: set[str] = {str(i) for i in range(2, 10)} | {"T", "J", "Q", "K", "A"}
SPECIAL_CARDS_STRENGTH = {"T": 10, "J": 11, "Q": 12, "K": 13, "A": 14}
CARDS_STRENGTH_MAPPING = {
    card_type: (
        int(card_type) if card_type.isdigit() else SPECIAL_CARDS_STRENGTH[card_type]
    )
    for card_type in CARDS_TYPES
}

class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 7 - Common code
    ###########################
    @staticmethod
    def __calculate_total_winnings(hands: list["Hand"]):
        return sum(hand.bid * i for i, hand in enumerate(hands, start=1))

    ###########################
    # DAY 7 - First Part
    ###########################

    def _solve_first_part(self) -> int:
        # Jack card for first part, better than T but lower than Q
        CARDS_STRENGTH_MAPPING["J"] = 11
        hands = sorted(Hand(line=line) for line in self.lines)
        return self.__calculate_total_winnings(hands)

    ###########################
    # DAY 7 - Second Part
    ###########################

    def _solve_second_part(self) -> int:
        # Jack card is now a Joker, and its value is lower than 2
        CARDS_STRENGTH_MAPPING["J"] = 1
        hands = sorted(Hand(line=line, joker=True) for line in self.lines)
        return self.__calculate_total_winnings(hands)


class Card:
    def __init__(self, name: str):
        self.name = name

    @cached_property
    def strength(self) -> int:
        return CARDS_STRENGTH_MAPPING[self.name]

    def __repr__(self):
        return self.name

    def __eq__(self, other: "Card") -> bool:
        return self.strength == other.strength

    def __lt__(self, other: "Card") -> bool:
        return self.strength < other.strength


ALL_CARDS_EXCEPT_JOKER: list[Card] = [
    Card(card_type) for card_type in CARDS_TYPES if card_type != "J"
]


class HandType(IntEnum):
    HIGH_CARD = auto()
    ONE_PAIR = auto()
    TWO_PAIR = auto()
    THREE_OF_A_KIND = auto()
    FULL_HOUSE = auto()
    FOUR_OF_A_KIND = auto()
    FIVE_OF_A_KIND = auto()


class Hand:
    cards: list[Card]
    bid: int = 0
    joker: bool = False

    def __init__(self, line: str = None, joker: bool = False, cards: list[Card] = None):
        if cards:
            self.cards = cards
        else:
            cards, bid = line.split()
            self.cards = [Card(card_name) for card_name in cards]
            self.bid = int(bid)

        self.joker = joker

    @cached_property
    def hand_type(self) -> HandType:
        # Compute the hand type depending if J is a Joker
        return (
            self.__get_best_hand_type()
            if self.joker
            else self.__get_hand_type(self.cards)
        )

    def __eq__(self, other: "Hand") -> bool:
        return self.cards == other.cards

    def __lt__(self, other: "Hand") -> bool:
        # First check hand types
        if self.hand_type != other.hand_type:
            return self.hand_type < other.hand_type

        # Then, check cards individually, one after another
        for self_card, other_card in zip(self.cards, other.cards):
            if self_card != other_card:
                return self_card < other_card

        # Hands seems equal, so self is not lower than other
        return False

    def __repr__(self) -> str:
        return f"Hand(cards={self.cards},bid={self.bid},hand_type={self.hand_type})"

    @staticmethod
    def __get_hand_type(cards: list[Card]) -> HandType:
        cards_by_type = defaultdict(int)
        for card in cards:
            cards_by_type[card.name] += 1

        different_card_types = len(cards_by_type)
        cards_amounts = cards_by_type.values()

        # All 5 cards are the same
        if different_card_types == 1:
            return HandType.FIVE_OF_A_KIND

        # Four cards are the same
        if different_card_types == 2 and any(
            nb_cards == 4 for nb_cards in cards_amounts
        ):
            return HandType.FOUR_OF_A_KIND

        # Three cards are the same, and the remaining two as well
        if different_card_types == 2 and any(
            nb_cards == 3 for nb_cards in cards_amounts
        ):
            return HandType.FULL_HOUSE

        # Three cards are the same, and then remaining two are different
        if different_card_types == 3 and any(
            nb_cards == 3 for nb_cards in cards_amounts
        ):
            return HandType.THREE_OF_A_KIND

        # Two pairs of cards
        if different_card_types == 3 and any(
            nb_cards == 1 for nb_cards in cards_amounts
        ):
            return HandType.TWO_PAIR

        # Only one pair of cards
        if different_card_types == 4 and any(
            nb_cards == 2 for nb_cards in cards_amounts
        ):
            return HandType.ONE_PAIR

        # All card labels are distinct
        return HandType.HIGH_CARD

    def __get_best_hand_type(self) -> HandType:
        # Retrieve the joker positions
        joker_positions: set[int] = {
            i for i, card in enumerate(self.cards) if card.name == "J"
        }

        # First, if we don't have any Joker, no need for calculations
        if not joker_positions:
            return self.__get_hand_type(self.cards)

        # Get a list of all possible hands
        possible_hands = self.__get_possible_hands(joker_positions)

        # Return the best possible hand type
        return max(self.__get_hand_type(hand.cards) for hand in possible_hands)

    def __get_possible_hands(self, joker_positions: set[int]) -> list[Card]:
        # First, assemble possible cards for each position, depending on joker positions
        possible_cards = [
            ALL_CARDS_EXCEPT_JOKER if i in joker_positions else [self.cards[i]]
            for i in range(5)
        ]

        return [Hand(cards=cards) for cards in product(*possible_cards)]
