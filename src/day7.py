from collections import defaultdict
from enum import Enum, auto
from functools import cached_property

from .utils import AbstractPuzzleSolver


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 7 - Common code
    ###########################
    cards_strength_mapping: dict[str, int] = {
        "T": 10,
        "Q": 12,
        "K": 13,
        "A": 14,
    }

    def __calculate_total_winnings(self):
        hands = sorted(Hand(line=line) for line in self.lines)
        return sum(hand.bid * i for i, hand in enumerate(hands, start=1))

    ###########################
    # DAY 7 - First Part
    ###########################

    def _solve_first_part(self) -> int:
        # Jack card for first part, better than T but lower than Q
        self.cards_strength_mapping["J"] = 11
        return self.__calculate_total_winnings()

    ###########################
    # DAY 7 - Second Part
    ###########################

    def _solve_second_part(self) -> int:
        # Jack card is now a Joker, and its value is lower than 2
        self.cards_strength_mapping["J"] = 1
        return self.__calculate_total_winnings()


class Card:
    name: str

    def __init__(self, name: str):
        self.name = name

    @cached_property
    def strength(self) -> int:
        return PuzzleSolver.cards_strength_mapping.get(self.name) or int(self.name)

    def __repr__(self):
        return f"Card({self.name})"

    def __eq__(self, other: "Card") -> bool:
        return self.strength == other.strength

    def __lt__(self, other: "Card") -> bool:
        return self.strength < other.strength


class HandType(Enum):
    HIGH_CARD = auto()
    ONE_PAIR = auto()
    TWO_PAIR = auto()
    THREE_OF_A_KIND = auto()
    FULL_HOUSE = auto()
    FOUR_OF_A_KIND = auto()
    FIVE_OF_A_KIND = auto()


class Hand:
    cards: list[Card]
    bid: int

    def __init__(self, line: str):
        cards, bid = line.split()
        self.cards = [Card(card_name) for card_name in cards]
        self.bid = int(bid)

    @cached_property
    def hand_type(self) -> HandType:
        cards_by_type = defaultdict(int)
        for card in self.cards:
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

    @cached_property
    def hand_type_strength(self) -> int:
        return self.hand_type.value

    def __eq__(self, other: "Hand") -> bool:
        return self.cards == other.cards

    def __lt__(self, other: "Hand") -> bool:
        # First check hand types
        if self.hand_type_strength != other.hand_type_strength:
            return self.hand_type_strength < other.hand_type_strength

        # Then, check cards individually, one after another
        for self_card, other_card in zip(self.cards, other.cards):
            if self_card != other_card:
                return self_card < other_card

        # Hands seems equal, so self is not lower than other
        return False
