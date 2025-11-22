"""Piece module for managing Tetris piece shapes and operations."""

from typing import List, Tuple
from enum import IntEnum


class PieceType(IntEnum):
    """Enumeration of Tetris piece types."""
    O = 0  # Square
    I = 1  # Line
    S = 2  # S-shape
    Z = 3  # Z-shape
    T = 4  # T-shape
    L = 5  # L-shape
    J = 6  # J-shape


class Piece:
    """
    Represents a Tetris piece (tetromino).

    Responsibilities:
    - Store piece shape and type
    - Provide rotation operations
    - Manage piece position
    """

    # Standard Tetris piece shapes
    SHAPES = [
        # O - Square
        [[1, 1],
         [1, 1]],

        # I - Line
        [[2, 2, 2, 2]],

        # S
        [[0, 3, 3],
         [3, 3, 0]],

        # Z
        [[4, 4, 0],
         [0, 4, 4]],

        # T
        [[0, 5, 0],
         [5, 5, 5]],

        # L
        [[0, 0, 6],
         [6, 6, 6]],

        # J
        [[7, 0, 0],
         [7, 7, 7]]
    ]

    def __init__(self, piece_type: int, x: int = 0, y: int = 0):
        """
        Initialize a new piece.

        Args:
            piece_type: Index of the piece type (0-6)
            x: Initial column position
            y: Initial row position
        """
        if not 0 <= piece_type < len(self.SHAPES):
            raise ValueError(f"Invalid piece type: {piece_type}")

        self.piece_type = piece_type
        self.shape = [row[:] for row in self.SHAPES[piece_type]]
        self.x = x
        self.y = y

    @classmethod
    def get_shape(cls, piece_type: int) -> List[List[int]]:
        """
        Get the shape of a piece type without creating a Piece instance.

        Args:
            piece_type: Index of the piece type (0-6)

        Returns:
            2D list representing the piece shape
        """
        if not 0 <= piece_type < len(cls.SHAPES):
            raise ValueError(f"Invalid piece type: {piece_type}")
        return [row[:] for row in cls.SHAPES[piece_type]]

    @classmethod
    def num_piece_types(cls) -> int:
        """
        Get the number of available piece types.

        Returns:
            Number of piece types
        """
        return len(cls.SHAPES)

    def get_shape_copy(self) -> List[List[int]]:
        """
        Get a copy of the current piece shape.

        Returns:
            2D list representing the piece shape
        """
        return [row[:] for row in self.shape]

    def rotate_clockwise(self) -> None:
        """
        Rotate the piece 90 degrees clockwise (modifies piece state).
        """
        self.shape = self.get_rotated_clockwise(self.shape)

    @staticmethod
    def get_rotated_clockwise(shape: List[List[int]]) -> List[List[int]]:
        """
        Get a clockwise 90-degree rotation of a shape.

        Args:
            shape: 2D list representing the shape to rotate

        Returns:
            Rotated shape
        """
        num_rows_orig = num_cols_new = len(shape)
        num_rows_new = len(shape[0])
        rotated = []

        for i in range(num_rows_new):
            new_row = [0] * num_cols_new
            for j in range(num_cols_new):
                new_row[j] = shape[(num_rows_orig - 1) - j][i]
            rotated.append(new_row)

        return rotated

    @staticmethod
    def get_rotated_counterclockwise(shape: List[List[int]]) -> List[List[int]]:
        """
        Get a counterclockwise 90-degree rotation of a shape.

        Args:
            shape: 2D list representing the shape to rotate

        Returns:
            Rotated shape
        """
        # Rotate clockwise 3 times = rotate counterclockwise once
        rotated = shape
        for _ in range(3):
            rotated = Piece.get_rotated_clockwise(rotated)
        return rotated

    def get_width(self) -> int:
        """
        Get the width of the piece.

        Returns:
            Width in cells
        """
        if not self.shape:
            return 0
        return len(self.shape[0])

    def get_height(self) -> int:
        """
        Get the height of the piece.

        Returns:
            Height in cells
        """
        return len(self.shape)

    def get_bounding_box(self) -> Tuple[int, int]:
        """
        Get the bounding box dimensions of the piece.

        Returns:
            Tuple of (width, height)
        """
        return self.get_width(), self.get_height()

    def move(self, dx: int, dy: int) -> None:
        """
        Move the piece by the given offset.

        Args:
            dx: Change in x position
            dy: Change in y position
        """
        self.x += dx
        self.y += dy

    def set_position(self, x: int, y: int) -> None:
        """
        Set the piece position.

        Args:
            x: New x position
            y: New y position
        """
        self.x = x
        self.y = y

    def get_position(self) -> Tuple[int, int]:
        """
        Get the current piece position.

        Returns:
            Tuple of (x, y)
        """
        return self.x, self.y

    def copy(self) -> 'Piece':
        """
        Create a copy of this piece.

        Returns:
            New Piece instance with the same state
        """
        new_piece = Piece(self.piece_type, self.x, self.y)
        new_piece.shape = self.get_shape_copy()
        return new_piece

    def get_all_rotations(self) -> List[List[List[int]]]:
        """
        Get all unique rotations of the current piece.

        Returns:
            List of rotated shapes (up to 4 rotations)
        """
        rotations = []
        current_shape = self.get_shape_copy()

        for _ in range(4):
            # Check if this rotation is unique
            if current_shape not in rotations:
                rotations.append([row[:] for row in current_shape])
            current_shape = self.get_rotated_clockwise(current_shape)

        return rotations

    def __repr__(self) -> str:
        """String representation of the piece."""
        piece_names = ['O', 'I', 'S', 'Z', 'T', 'L', 'J']
        return f"Piece({piece_names[self.piece_type]}, pos=({self.x}, {self.y}))"

    def __str__(self) -> str:
        """Pretty print the piece."""
        lines = []
        for row in self.shape:
            line = "".join("█" if cell > 0 else "." for cell in row)
            lines.append(line)
        return "\n".join(lines)
