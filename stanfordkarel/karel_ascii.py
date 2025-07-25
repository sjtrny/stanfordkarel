"""
This file defines the Karel ASCII program.

Original Author: Tyler Yep
License: MIT
Version: 1.0.0
Email: tyep@cs.stanford.edu
"""

from __future__ import annotations

from enum import Enum, unique
from typing import TYPE_CHECKING, Any

from .karel_world import BLANK, Direction, KarelWorld

if TYPE_CHECKING:
    from collections.abc import Iterator

CHAR_WIDTH = 5
HORIZONTAL, VERTICAL = "─", "│"
SPACING = 10
BEEPER_COORDS = dict[tuple[int, int], int]


class Tile:
    def __init__(self, value: str = "·") -> None:
        self.value = value
        self.direction: Direction | None = None
        self.walls: list[Direction] = []
        self.beepers = 0
        self.color = BLANK

    def custom_repr(self, show_only: str | None = None) -> str:
        if not show_only:
            if self.value == "K" and self.beepers > 0:
                return "<K>".center(CHAR_WIDTH)
            if self.beepers > 0:
                return f"<{self.beepers}>".center(CHAR_WIDTH)
            if self.color != BLANK:
                return self.color[:3].center(CHAR_WIDTH)
            return self.value.center(CHAR_WIDTH)

        if show_only == "karel":
            if self.value == "K":
                if self.direction == Direction.EAST:
                    result = "→"
                elif self.direction == Direction.SOUTH:
                    result = "↓"
                elif self.direction == Direction.WEST:
                    result = "←"
                else:
                    result = "↑"
            else:
                result = "·"
        elif show_only == "beeper":
            result = f"<{self.beepers}>" if self.beepers > 0 else "·"
        elif show_only == "color":
            result = self.color[:3] if self.color != BLANK else "·"
        else:
            result = "·"

        return result.center(CHAR_WIDTH)

    def __repr__(self) -> str:
        return self.custom_repr()


class AsciiKarelWorld:
    def __init__(
        self,
        world: KarelWorld,
        karel_street: int,
        karel_avenue: int,
        karel_direction: Any,
    ) -> None:
        num_sts, num_aves = world.num_streets, world.num_avenues
        # Initialize Tiles
        self.world_arr = [[Tile() for _ in range(num_aves)] for _ in range(num_sts)]

        # Add Karel
        self.world_arr[num_sts - karel_street][karel_avenue - 1].value = "K"
        self.world_arr[num_sts - karel_street][
            karel_avenue - 1
        ].direction = karel_direction
        for (avenue, street), count in world.beepers.items():
            self.world_arr[num_sts - street][avenue - 1].beepers = count

        # Add Walls
        for wall in world.walls:
            avenue, street, direction = wall.avenue, wall.street, wall.direction
            self.world_arr[num_sts - street][avenue - 1].walls.append(direction)

        # Add Colors
        for r in range(1, num_sts + 1):
            for c in range(1, num_aves + 1):
                if world.corner_color(c, r):
                    self.world_arr[num_sts - r][c - 1].color = world.corner_color(c, r)

        self.num_streets = num_sts
        self.num_avenues = num_aves

    def custom_repr(self, show_only: str | None = None) -> str:
        avenue_widths = HORIZONTAL * ((CHAR_WIDTH + 1) * self.num_avenues + 1)
        result = f"┌{avenue_widths}┐\n"
        for r in range(self.num_streets):
            next_line = VERTICAL
            result += VERTICAL
            next_block_start = " "
            for c in range(self.num_avenues):
                tile = self.world_arr[r][c]
                line, next_block_start = self.get_next_line(r, c, next_block_start)
                next_line += line
                result += (
                    VERTICAL if self.tile_pair_has_wall(r, c, Direction.WEST) else " "
                ) + tile.custom_repr(show_only)

            result += f" {VERTICAL}\n"
            if r == self.num_streets - 1:
                result += f"└{avenue_widths}┘\n"
            else:
                result += f"{next_line} {VERTICAL}\n"
        return result

    def __repr__(self) -> str:
        return self.custom_repr()

    def tile_has_wall(self, r: int, c: int, direction: Direction) -> bool:
        if 0 <= r < self.num_streets and 0 <= c < self.num_avenues:
            tile = self.world_arr[r][c]
            return direction in tile.walls
        return False

    def tile_pair_has_wall(self, r: int, c: int, direction: Direction) -> bool:
        """
        Checks whether the tile at r, c should have a wall by
        checking itself and its neighbors.
        """
        if direction == Direction.SOUTH:
            return self.tile_has_wall(r, c, Direction.SOUTH) or self.tile_has_wall(
                r + 1, c, Direction.NORTH
            )
        if direction == Direction.NORTH:
            return self.tile_has_wall(r, c, Direction.NORTH) or self.tile_has_wall(
                r - 1, c, Direction.SOUTH
            )
        if direction == Direction.WEST:
            return self.tile_has_wall(r, c, Direction.WEST) or self.tile_has_wall(
                r, c - 1, Direction.EAST
            )
        if direction == Direction.EAST:
            return self.tile_has_wall(r, c, Direction.EAST) or self.tile_has_wall(
                r, c + 1, Direction.WEST
            )
        raise ValueError("Direction is invalid.")

    def get_next_line(self, r: int, c: int, next_block_start: str) -> tuple[str, str]:
        """Given a tile, figures out the lower line of the ASCII art."""

        if self.tile_pair_has_wall(r, c, Direction.SOUTH):
            if (
                next_block_start == HORIZONTAL
                and self.tile_pair_has_wall(r, c, Direction.WEST)
                and self.tile_pair_has_wall(r + 1, c, Direction.WEST)
            ):
                next_block_start = "┼"
            elif (
                next_block_start == " "
                and self.tile_pair_has_wall(r, c, Direction.WEST)
                and self.tile_pair_has_wall(r + 1, c, Direction.WEST)
            ):
                next_block_start = "├"
            elif self.tile_pair_has_wall(r + 1, c, Direction.WEST):
                next_block_start = "┌"
            elif self.tile_pair_has_wall(r, c, Direction.WEST):
                next_block_start = "└"
            next_line = next_block_start + HORIZONTAL * CHAR_WIDTH
            next_block_start = HORIZONTAL
        else:
            if (
                next_block_start == HORIZONTAL
                and self.tile_pair_has_wall(r, c, Direction.WEST)
                and self.tile_pair_has_wall(r + 1, c, Direction.WEST)
            ):
                next_block_start = "┤"
            elif next_block_start == HORIZONTAL and self.tile_pair_has_wall(
                r + 1, c, Direction.WEST
            ):
                next_block_start = "┐"
            elif next_block_start == HORIZONTAL and self.tile_pair_has_wall(
                r, c, Direction.WEST
            ):
                next_block_start = "┘"
            elif self.tile_pair_has_wall(
                r, c, Direction.WEST
            ) and self.tile_pair_has_wall(r + 1, c, Direction.WEST):
                next_block_start = VERTICAL

            next_line = next_block_start + " " * CHAR_WIDTH
            next_block_start = " "
        return next_line, next_block_start


@unique
class Color(Enum):
    PURPLE = "\033[95m"
    CYAN = "\033[96m"
    DARKCYAN = "\033[36m"
    BLUE = "\033[94m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


def compare_output(first: Any, second: Any) -> str:
    """Compares Karel Output and gets the results."""

    def create_two_column_string(col1: list[str], col2: list[str]) -> Iterator[str]:
        """col1 and col2 are Lists."""
        return (f"{x[0]}{' ' * SPACING}{x[1]}" for x in zip(col1, col2, strict=False))

    def symmetric_difference(
        a: BEEPER_COORDS, b: BEEPER_COORDS
    ) -> tuple[BEEPER_COORDS, BEEPER_COORDS]:
        extra_a, extra_b = {}, {}
        for k in a:
            if k not in b:
                extra_a[k] = a[k]
            elif a[k] - b[k] > 0:
                extra_a[k] = a[k] - b[k]
        for k in b:
            if k not in a:
                extra_b[k] = b[k]
            elif b[k] - a[k] > 0:
                extra_b[k] = b[k] - a[k]
        return extra_a, extra_b

    this, that = str(first).split("\n"), str(second).split("\n")
    world_width = len(this[0])

    header1, header2 = "Student Output:", "Expected Output:"
    text_spacing = " " * (world_width - len(header1) + SPACING + 1)
    two_columns = create_two_column_string(this, that)
    output = "\n".join(two_columns)
    fancy_arrows = f"{Color.RED.value}❯{Color.YELLOW.value}❯{Color.GREEN.value}❯ "

    result = (
        f"\n\n{fancy_arrows} "
        f"{Color.YELLOW.value}{first.world.world_file}{Color.END.value}"
        f"\n{header1}{text_spacing}{header2}\n{output}\n"
    )

    if first.avenue != second.avenue or first.street != second.street:
        result += (
            "Karel did not end up in the same location in both worlds:\n"
            f"Student: {(first.avenue, first.street)}\n"
            f"Expected: {(second.avenue, second.street)}\n\n"
        )

    if first.direction != second.direction:
        result += (
            "Karel not facing the correct direction.\n"
            f"Student: {first.direction}\n"
            f"Expected: {second.direction}\n\n"
        )

    if first.world.get_beepers() != second.world.get_beepers():
        extra_a, extra_b = symmetric_difference(
            first.world.get_beepers(), second.world.get_beepers()
        )
        result += (
            "Beepers do not match: "
            "(Only beepers that appear in one world but not the other are listed)\n"
            f"Student: {extra_a}\n"
            f"Expected: {extra_b}\n\n"
        )

    if first.world.get_colors() != second.world.get_colors():
        extra_a, extra_b = symmetric_difference(
            first.world.get_colors(), second.world.get_colors()
        )
        result += (
            "Colors do not match: "
            "(Only colors that appear in one world but not the other are listed)\n"
            f"Student: {extra_a}\n"
            f"Expected: {extra_b}\n\n"
        )

    return result
