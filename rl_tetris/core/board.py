"""Board module for managing the Tetris game board state and operations."""

import numpy as np
from typing import List, Tuple


class Board:
    """
    Manages the Tetris game board state and operations.

    Responsibilities:
    - Board state management (initialization, copying)
    - Collision detection
    - Line clearing
    - Feature extraction (holes, bumpiness, height)
    """

    def __init__(self, height: int = 20, width: int = 10):
        """
        Initialize a new board.

        Args:
            height: Number of rows in the board
            width: Number of columns in the board
        """
        self.height = height
        self.width = width
        self._state = None
        self.reset()

    def reset(self) -> None:
        """Reset the board to an empty state."""
        self._state = [[0] * self.width for _ in range(self.height)]

    def get_state(self) -> List[List[int]]:
        """
        Get a copy of the current board state.

        Returns:
            A deep copy of the board state
        """
        return [row[:] for row in self._state]

    def set_state(self, state: List[List[int]]) -> None:
        """
        Set the board state.

        Args:
            state: The new board state
        """
        if len(state) != self.height or any(len(row) != self.width for row in state):
            raise ValueError(f"Invalid board state dimensions. Expected {self.height}x{self.width}")
        self._state = [row[:] for row in state]

    def is_valid_position(self, x: int, y: int) -> bool:
        """
        Check if a position is within board boundaries.

        Args:
            x: Column index
            y: Row index

        Returns:
            True if position is valid, False otherwise
        """
        return 0 <= x < self.width and 0 <= y < self.height

    def is_cell_occupied(self, x: int, y: int) -> bool:
        """
        Check if a cell is occupied.

        Args:
            x: Column index
            y: Row index

        Returns:
            True if cell is occupied, False otherwise
        """
        if not self.is_valid_position(x, y):
            return False
        return self._state[y][x] > 0

    def check_collision(self, piece_shape: List[List[int]], x: int, y: int) -> bool:
        """
        Check if placing a piece at the given position would cause a collision.

        Args:
            piece_shape: 2D array representing the piece shape
            x: Column position of the piece's top-left corner
            y: Row position of the piece's top-left corner

        Returns:
            True if collision occurs, False otherwise
        """
        for py in range(len(piece_shape)):
            for px in range(len(piece_shape[py])):
                # Skip empty cells in the piece
                if piece_shape[py][px] == 0:
                    continue

                board_x = x + px
                board_y = y + py

                # Check boundaries
                if not self.is_valid_position(board_x, board_y):
                    return True

                # Check if cell is already occupied
                if self._state[board_y][board_x] > 0:
                    return True

        return False

    def place_piece(self, piece_shape: List[List[int]], x: int, y: int) -> None:
        """
        Place a piece on the board (modifies board state).

        Args:
            piece_shape: 2D array representing the piece shape
            x: Column position of the piece's top-left corner
            y: Row position of the piece's top-left corner
        """
        for py in range(len(piece_shape)):
            for px in range(len(piece_shape[py])):
                if piece_shape[py][px] > 0:
                    board_y = y + py
                    board_x = x + px
                    if self.is_valid_position(board_x, board_y):
                        if self._state[board_y][board_x] == 0:
                            self._state[board_y][board_x] = piece_shape[py][px]

    def get_board_with_piece(self, piece_shape: List[List[int]], x: int, y: int) -> List[List[int]]:
        """
        Get a copy of the board with a piece placed at the given position.

        Args:
            piece_shape: 2D array representing the piece shape
            x: Column position of the piece's top-left corner
            y: Row position of the piece's top-left corner

        Returns:
            A new board state with the piece placed
        """
        board_copy = self.get_state()
        for py in range(len(piece_shape)):
            for px in range(len(piece_shape[py])):
                if piece_shape[py][px] > 0:
                    board_y = y + py
                    board_x = x + px
                    if self.is_valid_position(board_x, board_y):
                        if board_copy[board_y][board_x] == 0:
                            board_copy[board_y][board_x] = piece_shape[py][px]
        return board_copy

    def clear_full_rows(self) -> int:
        """
        Clear all full rows from the board and return the number cleared.

        Returns:
            Number of rows cleared
        """
        rows_to_delete = []
        for i, row in enumerate(self._state):
            if 0 not in row:
                rows_to_delete.append(i)

        if rows_to_delete:
            self._remove_rows(rows_to_delete)

        return len(rows_to_delete)

    def _remove_rows(self, indices: List[int]) -> None:
        """
        Remove rows at the given indices and add empty rows at the top.

        Args:
            indices: List of row indices to remove
        """
        # Delete rows in reverse order to maintain correct indices
        for i in sorted(indices, reverse=True):
            del self._state[i]

        # Add empty rows at the top
        num_removed = len(indices)
        for _ in range(num_removed):
            self._state.insert(0, [0] * self.width)

    def get_holes(self) -> int:
        """
        Count the number of holes in the board.
        A hole is an empty cell with at least one filled cell above it.

        Returns:
            Number of holes
        """
        num_holes = 0
        for col_idx in range(self.width):
            # Find first filled cell in column
            row = 0
            while row < self.height and self._state[row][col_idx] == 0:
                row += 1

            # Count empty cells below first filled cell
            for check_row in range(row + 1, self.height):
                if self._state[check_row][col_idx] == 0:
                    num_holes += 1

        return num_holes

    def get_bumpiness_and_height(self) -> Tuple[int, int]:
        """
        Calculate the bumpiness and total height of the board.

        Bumpiness is the sum of absolute differences between adjacent column heights.
        Total height is the sum of all column heights.

        Returns:
            Tuple of (bumpiness, total_height)
        """
        board_array = np.array(self._state)
        mask = board_array != 0

        # Calculate height of each column
        # If column has any filled cell, height = height - first_filled_row
        # Otherwise height = 0
        invert_heights = np.where(
            mask.any(axis=0),
            np.argmax(mask, axis=0),
            self.height
        )
        heights = self.height - invert_heights

        total_height = np.sum(heights)

        # Calculate bumpiness (sum of absolute height differences)
        if len(heights) > 1:
            diffs = np.abs(heights[:-1] - heights[1:])
            total_bumpiness = np.sum(diffs)
        else:
            total_bumpiness = 0

        return int(total_bumpiness), int(total_height)

    def get_column_heights(self) -> List[int]:
        """
        Get the height of each column.

        Returns:
            List of column heights
        """
        board_array = np.array(self._state)
        mask = board_array != 0
        invert_heights = np.where(
            mask.any(axis=0),
            np.argmax(mask, axis=0),
            self.height
        )
        heights = self.height - invert_heights
        return heights.tolist()

    def is_row_full(self, row_idx: int) -> bool:
        """
        Check if a row is completely filled.

        Args:
            row_idx: Row index to check

        Returns:
            True if row is full, False otherwise
        """
        if not 0 <= row_idx < self.height:
            return False
        return 0 not in self._state[row_idx]

    def is_empty(self) -> bool:
        """
        Check if the board is completely empty.

        Returns:
            True if board is empty, False otherwise
        """
        for row in self._state:
            if any(cell > 0 for cell in row):
                return False
        return True

    def __repr__(self) -> str:
        """String representation of the board."""
        return f"Board({self.height}x{self.width})"

    def __str__(self) -> str:
        """Pretty print the board."""
        lines = []
        for row in self._state:
            line = "|" + "".join("█" if cell > 0 else "." for cell in row) + "|"
            lines.append(line)
        lines.append("+" + "-" * self.width + "+")
        return "\n".join(lines)
