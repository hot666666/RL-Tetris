"""Tests for Piece class."""

import pytest
from rl_tetris.core.piece import Piece, PieceType


class TestPieceInitialization:
    """Test piece initialization."""

    def test_create_all_piece_types(self):
        """Test creating all piece types."""
        for i in range(7):
            piece = Piece(i)
            assert piece.piece_type == i
            assert piece.x == 0
            assert piece.y == 0
            assert piece.shape is not None

    def test_create_with_position(self):
        """Test creating piece with custom position."""
        piece = Piece(0, x=5, y=10)
        assert piece.x == 5
        assert piece.y == 10

    def test_invalid_piece_type(self):
        """Test creating piece with invalid type."""
        with pytest.raises(ValueError):
            Piece(-1)
        with pytest.raises(ValueError):
            Piece(10)

    def test_piece_type_enum(self):
        """Test PieceType enum."""
        assert PieceType.O == 0
        assert PieceType.I == 1
        assert PieceType.S == 2
        assert PieceType.Z == 3
        assert PieceType.T == 4
        assert PieceType.L == 5
        assert PieceType.J == 6


class TestPieceShapes:
    """Test piece shapes."""

    def test_o_piece_shape(self):
        """Test O piece (square) shape."""
        piece = Piece(PieceType.O)
        expected = [[1, 1], [1, 1]]
        assert piece.shape == expected

    def test_i_piece_shape(self):
        """Test I piece (line) shape."""
        piece = Piece(PieceType.I)
        expected = [[2, 2, 2, 2]]
        assert piece.shape == expected

    def test_get_shape_classmethod(self):
        """Test getting shape without creating instance."""
        shape = Piece.get_shape(PieceType.O)
        expected = [[1, 1], [1, 1]]
        assert shape == expected

    def test_get_shape_copy(self):
        """Test getting shape copy."""
        piece = Piece(PieceType.O)
        shape_copy = piece.get_shape_copy()

        # Modify copy
        shape_copy[0][0] = 99

        # Original should be unchanged
        assert piece.shape[0][0] == 1

    def test_num_piece_types(self):
        """Test getting number of piece types."""
        assert Piece.num_piece_types() == 7


class TestPieceRotation:
    """Test piece rotation."""

    def test_rotate_o_piece(self):
        """Test rotating O piece (should stay same)."""
        piece = Piece(PieceType.O)
        original = piece.get_shape_copy()
        piece.rotate_clockwise()
        assert piece.shape == original

    def test_rotate_i_piece(self):
        """Test rotating I piece."""
        piece = Piece(PieceType.I)
        original = [[2, 2, 2, 2]]
        assert piece.shape == original

        piece.rotate_clockwise()
        expected_rotated = [[2], [2], [2], [2]]
        assert piece.shape == expected_rotated

        # Rotate back
        piece.rotate_clockwise()
        assert piece.shape == original

    def test_rotate_t_piece(self):
        """Test rotating T piece."""
        piece = Piece(PieceType.T)
        original = [[0, 5, 0], [5, 5, 5]]

        # Test all 4 rotations
        shapes = [piece.get_shape_copy()]
        for _ in range(3):
            piece.rotate_clockwise()
            shapes.append(piece.get_shape_copy())

        # After 4 rotations, should be back to original
        piece.rotate_clockwise()
        assert piece.shape == original

    def test_get_rotated_clockwise_static(self):
        """Test static rotation method."""
        shape = [[1, 2], [3, 4]]
        rotated = Piece.get_rotated_clockwise(shape)
        expected = [[3, 1], [4, 2]]
        assert rotated == expected

    def test_get_rotated_counterclockwise(self):
        """Test counterclockwise rotation."""
        shape = [[1, 2], [3, 4]]
        rotated = Piece.get_rotated_counterclockwise(shape)
        expected = [[2, 4], [1, 3]]
        assert rotated == expected

    def test_get_all_rotations(self):
        """Test getting all unique rotations."""
        # O piece has only 1 unique rotation
        piece_o = Piece(PieceType.O)
        rotations_o = piece_o.get_all_rotations()
        assert len(rotations_o) == 1

        # I piece has 2 unique rotations
        piece_i = Piece(PieceType.I)
        rotations_i = piece_i.get_all_rotations()
        assert len(rotations_i) == 2

        # T piece has 4 unique rotations
        piece_t = Piece(PieceType.T)
        rotations_t = piece_t.get_all_rotations()
        assert len(rotations_t) == 4


class TestPieceDimensions:
    """Test piece dimension methods."""

    def test_get_width(self):
        """Test getting piece width."""
        piece_o = Piece(PieceType.O)
        assert piece_o.get_width() == 2

        piece_i = Piece(PieceType.I)
        assert piece_i.get_width() == 4

    def test_get_height(self):
        """Test getting piece height."""
        piece_o = Piece(PieceType.O)
        assert piece_o.get_height() == 2

        piece_i = Piece(PieceType.I)
        assert piece_i.get_height() == 1

    def test_get_bounding_box(self):
        """Test getting bounding box."""
        piece_o = Piece(PieceType.O)
        width, height = piece_o.get_bounding_box()
        assert width == 2
        assert height == 2

        piece_i = Piece(PieceType.I)
        width, height = piece_i.get_bounding_box()
        assert width == 4
        assert height == 1

    def test_dimensions_after_rotation(self):
        """Test dimensions change after rotation."""
        piece_i = Piece(PieceType.I)
        assert piece_i.get_width() == 4
        assert piece_i.get_height() == 1

        piece_i.rotate_clockwise()
        assert piece_i.get_width() == 1
        assert piece_i.get_height() == 4


class TestPieceMovement:
    """Test piece movement."""

    def test_move(self):
        """Test moving piece."""
        piece = Piece(PieceType.O, x=5, y=5)
        piece.move(2, 3)
        assert piece.x == 7
        assert piece.y == 8

    def test_move_negative(self):
        """Test moving piece in negative direction."""
        piece = Piece(PieceType.O, x=10, y=10)
        piece.move(-5, -3)
        assert piece.x == 5
        assert piece.y == 7

    def test_set_position(self):
        """Test setting piece position."""
        piece = Piece(PieceType.O)
        piece.set_position(15, 20)
        assert piece.x == 15
        assert piece.y == 20

    def test_get_position(self):
        """Test getting piece position."""
        piece = Piece(PieceType.O, x=7, y=13)
        x, y = piece.get_position()
        assert x == 7
        assert y == 13


class TestPieceCopy:
    """Test piece copying."""

    def test_copy(self):
        """Test copying piece."""
        original = Piece(PieceType.T, x=5, y=10)
        copy = original.copy()

        # Check attributes are copied
        assert copy.piece_type == original.piece_type
        assert copy.x == original.x
        assert copy.y == original.y
        assert copy.shape == original.shape

    def test_copy_independence(self):
        """Test that copy is independent."""
        original = Piece(PieceType.T, x=5, y=10)
        copy = original.copy()

        # Modify copy
        copy.move(10, 10)
        copy.rotate_clockwise()

        # Original should be unchanged
        assert original.x == 5
        assert original.y == 10
        assert original.shape != copy.shape


class TestPieceStringRepresentation:
    """Test piece string representations."""

    def test_repr(self):
        """Test __repr__ method."""
        piece = Piece(PieceType.O, x=3, y=7)
        repr_str = repr(piece)
        assert "Piece" in repr_str
        assert "O" in repr_str
        assert "3" in repr_str
        assert "7" in repr_str

    def test_str(self):
        """Test __str__ method."""
        piece = Piece(PieceType.O)
        str_repr = str(piece)
        assert "█" in str_repr or "." in str_repr


class TestPieceShapeIntegrity:
    """Test that piece shapes maintain integrity."""

    def test_shapes_not_empty(self):
        """Test that all piece shapes are not empty."""
        for i in range(7):
            piece = Piece(i)
            assert len(piece.shape) > 0
            assert all(len(row) > 0 for row in piece.shape)

    def test_shapes_have_correct_values(self):
        """Test that shapes have correct value patterns."""
        for i in range(7):
            piece = Piece(i)
            # Each piece should have its type number (i+1) in the shape
            expected_value = i + 1
            has_expected_value = any(
                cell == expected_value
                for row in piece.shape
                for cell in row
            )
            assert has_expected_value

    def test_rotation_preserves_cell_count(self):
        """Test that rotation doesn't change number of filled cells."""
        for piece_type in range(7):
            piece = Piece(piece_type)
            original_count = sum(
                1 for row in piece.shape for cell in row if cell > 0
            )

            piece.rotate_clockwise()
            rotated_count = sum(
                1 for row in piece.shape for cell in row if cell > 0
            )

            assert original_count == rotated_count


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
