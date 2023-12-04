from functools import cached_property

from .utils import AbstractPuzzleSolver


class PuzzleSolver(AbstractPuzzleSolver):
    ###########################
    # DAY 4 - First Part
    ###########################

    def _solve_first_part(self) -> int:
        return sum(Scratchcard(line).points for line in self.lines)

    ###########################
    # DAY 4 - Second Part
    ###########################

    def _solve_second_part(self) -> int:
        # Assemble cards references
        self.cards_references = self.__get_cards_references()

        # Init cards count with original ones
        # card_number -> count
        self.won_cards: dict[int, int] = {
            card_number: 1 for card_number in self.cards_references.keys()
        }

        # Get won cards for each original cards
        for card in self.cards_references.values():
            self.__get_won_cards(card)

        return sum(self.won_cards.values())

    def __get_cards_references(self) -> dict[int, "Scratchcard"]:
        cards_references = {}
        for line in self.lines:
            card = Scratchcard(line)
            cards_references[card.number] = card
        return cards_references

    def __get_won_cards(self, card: "Scratchcard"):
        for next_card_number in card.next_cards_numbers:
            # Add the new won card in the list
            self.won_cards[next_card_number] += 1
            # Get won cards associated with this new won card
            self.__get_won_cards(self.cards_references[next_card_number])


class Scratchcard:
    winning_numbers: set[str]
    played_numbers: set[str]
    number: int

    def __init__(self, line: str):
        card_number, scratchcard_data = line.split(":")
        self.number = int(card_number.split()[-1])

        winning_data, played_data = scratchcard_data.split("|")
        self.winning_numbers = set(number.strip() for number in winning_data.split())
        self.played_numbers = set(number.strip() for number in played_data.split())

    @cached_property
    def matching_numbers(self) -> set[str]:
        return self.winning_numbers & self.played_numbers

    @cached_property
    def points(self) -> int:
        return pow(2, len(self.matching_numbers) - 1) if self.matching_numbers else 0

    @cached_property
    def next_cards_numbers(self) -> set[int]:
        start = self.number + 1
        stop = start + len(self.matching_numbers)
        return set(range(start, stop))
