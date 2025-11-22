"""Tests for Board class."""

import pytest
import numpy as np
from rl_tetris.core.board import Board


class TestBoardInitialization:
    """Test board initialization."""

    def test_default_initialization(self):
        """Test board with default dimensions."""
        board = Board()
        assert board.height == 20
        assert board.width == 10
        assert board.is_empty()

    def test_custom_dimensions(self):
        """Test board with custom dimensions."""
        board = Board(height=15, width=8)
        assert board.height == 15
        assert board.width == 8
        assert board.is_empty()

    def test_reset(self):
        """Test board reset."""
        board = Board()
        # Manually set some cells
        state = board.get_state()
        state[19][5] = 1
        board.set_state(state)
        assert not board.is_empty()

        # Reset and check
        board.reset()
        assert board.is_empty()


class TestBoardState:
    """Test board state management."""

    def test_get_state(self):
        """Test getting board state."""
        board = Board(height=4, width=4)
        state = board.get_state()
        assert len(state) == 4
        assert all(len(row) == 4 for row in state)
        assert all(cell == 0 for row in state for cell in row)

    def test_set_state(self):
        """Test setting board state."""
        board = Board(height=3, width=3)
        new_state = [
            [1, 0, 0],
            [0, 2, 0],
            [0, 0, 3]
        ]
        board.set_state(new_state)
        state = board.get_state()
        assert state[0][0] == 1
        assert state[1][1] == 2
        assert state[2][2] == 3

    def test_set_invalid_state(self):
        """Test setting invalid state dimensions."""
        board = Board(height=4, width=4)
        invalid_state = [[0, 0], [0, 0]]  # Wrong dimensions

        with pytest.raises(ValueError):
            board.set_state(invalid_state)


class TestBoardPositionValidation:
    """Test position validation methods."""

    def test_is_valid_position(self):
        """Test valid position checking."""
        board = Board(height=10, width=10)
        assert board.is_valid_position(0, 0)
        assert board.is_valid_position(9, 9)
        assert board.is_valid_position(5, 5)

    def test_is_invalid_position(self):
        """Test invalid position checking."""
        board = Board(height=10, width=10)
        assert not board.is_valid_position(-1, 0)
        assert not board.is_valid_position(0, -1)
        assert not board.is_valid_position(10, 0)
        assert not board.is_valid_position(0, 10)

    def test_is_cell_occupied(self):
        """Test cell occupation checking."""
        board = Board(height=5, width=5)
        state = [[0] * 5 for _ in range(5)]
        state[2][2] = 1
        board.set_state(state)

        assert not board.is_cell_occupied(0, 0)
        assert board.is_cell_occupied(2, 2)
        assert not board.is_cell_occupied(-1, -1)  # Invalid position


class TestBoardCollision:
    """Test collision detection."""

    def test_no_collision_empty_board(self):
        """Test no collision on empty board."""
        board = Board(height=10, width=10)
        piece = [[1, 1], [1, 1]]  # 2x2 square
        assert not board.check_collision(piece, 0, 0)
        assert not board.check_collision(piece, 8, 8)

    def test_collision_with_boundary(self):
        """Test collision with board boundaries."""
        board = Board(height=10, width=10)
        piece = [[1, 1], [1, 1]]

        # Out of bounds
        assert board.check_collision(piece, -1, 0)  # Left
        assert board.check_collision(piece, 9, 0)   # Right
        assert board.check_collision(piece, 0, -1)  # Top
        assert board.check_collision(piece, 0, 9)   # Bottom

    def test_collision_with_occupied_cells(self):
        """Test collision with occupied cells."""
        board = Board(height=10, width=10)
        state = [[0] * 10 for _ in range(10)]
        state[5][5] = 1  # Occupied cell
        board.set_state(state)

        piece = [[1, 1], [1, 1]]
        assert board.check_collision(piece, 4, 4)  # Overlaps (5,5)
        assert not board.check_collision(piece, 6, 6)  # No overlap

    def test_collision_with_empty_piece_cells(self):
        """Test that empty cells in piece don't cause collision."""
        board = Board(height=10, width=10)
        state = [[0] * 10 for _ in range(10)]
        state[5][4] = 1  # Occupied cell
        board.set_state(state)

        # Piece with empty cell in the middle: [1, 0, 1]
        # When placed at (5, 3), the empty cell overlaps with occupied cell
        piece = [[1, 0, 1]]
        assert not board.check_collision(piece, 3, 5)  # Empty cell overlaps occupied, should be OK


class TestBoardPiecePlacement:
    """Test piece placement on board."""

    def test_place_piece(self):
        """Test placing a piece on the board."""
        board = Board(height=10, width=10)
        piece = [[1, 1], [1, 1]]
        board.place_piece(piece, 3, 3)

        state = board.get_state()
        assert state[3][3] == 1
        assert state[3][4] == 1
        assert state[4][3] == 1
        assert state[4][4] == 1

    def test_get_board_with_piece(self):
        """Test getting board copy with piece."""
        board = Board(height=10, width=10)
        piece = [[2, 2], [2, 2]]
        new_board = board.get_board_with_piece(piece, 5, 5)

        # Original board should be unchanged
        assert board.is_empty()

        # New board should have piece
        assert new_board[5][5] == 2
        assert new_board[5][6] == 2

    def test_place_piece_with_empty_cells(self):
        """Test placing piece with empty cells."""
        board = Board(height=10, width=10)
        piece = [[0, 3, 0], [3, 3, 3]]
        board.place_piece(piece, 4, 4)

        state = board.get_state()
        assert state[4][4] == 0  # Empty cell in piece
        assert state[4][5] == 3
        assert state[5][4] == 3


class TestLineClear:
    """Test line clearing functionality."""

    def test_clear_no_lines(self):
        """Test clearing when no lines are full."""
        board = Board(height=10, width=10)
        state = [[0] * 10 for _ in range(10)]
        state[9] = [1, 1, 1, 0, 1, 1, 1, 1, 1, 1]  # Not full
        board.set_state(state)

        lines_cleared = board.clear_full_rows()
        assert lines_cleared == 0

    def test_clear_one_line(self):
        """Test clearing one full line."""
        board = Board(height=10, width=10)
        state = [[0] * 10 for _ in range(10)]
        state[9] = [1] * 10  # Full line at bottom
        board.set_state(state)

        lines_cleared = board.clear_full_rows()
        assert lines_cleared == 1

        # Check that line is cleared and moved to top
        new_state = board.get_state()
        assert new_state[0] == [0] * 10
        assert new_state[9] == [0] * 10

    def test_clear_multiple_lines(self):
        """Test clearing multiple full lines."""
        board = Board(height=10, width=10)
        state = [[0] * 10 for _ in range(10)]
        state[7] = [1] * 10
        state[8] = [2] * 10
        state[9] = [3] * 10
        board.set_state(state)

        lines_cleared = board.clear_full_rows()
        assert lines_cleared == 3

        # All lines should be empty now
        new_state = board.get_state()
        assert all(cell == 0 for row in new_state for cell in row)

    def test_clear_non_consecutive_lines(self):
        """Test clearing non-consecutive full lines."""
        board = Board(height=10, width=10)
        state = [[0] * 10 for _ in range(10)]
        state[5] = [1] * 10
        state[7] = [2] * 10
        state[6] = [3, 0, 3, 3, 3, 3, 3, 3, 3, 3]  # Not full
        board.set_state(state)

        lines_cleared = board.clear_full_rows()
        assert lines_cleared == 2

        new_state = board.get_state()
        # The incomplete line should remain at row 7 after clearing rows 5 and 7
        assert 3 in new_state[7]


class TestBoardFeatures:
    """Test board feature extraction."""

    def test_get_holes_empty_board(self):
        """Test holes on empty board."""
        board = Board(height=10, width=10)
        assert board.get_holes() == 0

    def test_get_holes_with_holes(self):
        """Test holes detection."""
        board = Board(height=10, width=10)
        state = [[0] * 10 for _ in range(10)]
        # Create holes: block on top, empty spaces below
        state[5][3] = 1
        state[6][3] = 0  # Hole
        state[7][3] = 0  # Hole
        state[8][3] = 1
        state[9][3] = 1  # Block at bottom to close the holes
        board.set_state(state)

        holes = board.get_holes()
        assert holes == 2  # Two holes in column 3 (rows 6 and 7)

    def test_get_bumpiness_flat(self):
        """Test bumpiness on flat surface."""
        board = Board(height=10, width=10)
        state = [[0] * 10 for _ in range(10)]
        state[9] = [1] * 10  # Flat bottom row
        board.set_state(state)

        bumpiness, height = board.get_bumpiness_and_height()
        assert bumpiness == 0  # Flat surface
        assert height == 10  # All columns have height 1, total = 10

    def test_get_bumpiness_uneven(self):
        """Test bumpiness on uneven surface."""
        board = Board(height=10, width=3)
        state = [[0] * 3 for _ in range(10)]
        # Column heights: 1, 3, 1
        state[9][0] = 1
        state[9][1] = 1
        state[8][1] = 1
        state[7][1] = 1
        state[9][2] = 1
        board.set_state(state)

        bumpiness, height = board.get_bumpiness_and_height()
        # Bumpiness = |1-3| + |3-1| = 2 + 2 = 4
        assert bumpiness == 4
        # Height = 1 + 3 + 1 = 5
        assert height == 5

    def test_get_column_heights(self):
        """Test getting column heights."""
        board = Board(height=10, width=5)
        state = [[0] * 5 for _ in range(10)]
        state[9][0] = 1  # Height 1
        state[9][1] = 1  # Height 2
        state[8][1] = 1
        # Column 2 empty (height 0)
        state[9][3] = 1  # Height 1
        board.set_state(state)

        heights = board.get_column_heights()
        assert heights == [1, 2, 0, 1, 0]


class TestBoardUtilities:
    """Test utility methods."""

    def test_is_row_full(self):
        """Test checking if row is full."""
        board = Board(height=5, width=5)
        state = [[0] * 5 for _ in range(5)]
        state[4] = [1, 1, 1, 1, 1]  # Full
        state[3] = [1, 0, 1, 1, 1]  # Not full
        board.set_state(state)

        assert board.is_row_full(4)
        assert not board.is_row_full(3)
        assert not board.is_row_full(-1)  # Invalid
        assert not board.is_row_full(10)  # Invalid

    def test_is_empty(self):
        """Test checking if board is empty."""
        board = Board()
        assert board.is_empty()

        state = board.get_state()
        state[10][5] = 1
        board.set_state(state)
        assert not board.is_empty()

    def test_str_representation(self):
        """Test string representation."""
        board = Board(height=3, width=3)
        state = [[0, 1, 0], [0, 1, 0], [0, 1, 0]]
        board.set_state(state)

        str_repr = str(board)
        assert "|" in str_repr
        assert "█" in str_repr
        assert "." in str_repr


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
