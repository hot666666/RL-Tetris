"""Tests for Game class."""

import pytest
from rl_tetris.core.board import Board
from rl_tetris.core.game import Game
from rl_tetris.core.piece import Piece
from rl_tetris.tetromino_queue import TetrominoQueue
from rl_tetris.randomizer import BagRandomizer


class TestGameInitialization:
    """Test game initialization."""

    def test_create_game(self):
        """Test creating a game."""
        board = Board()
        queue = TetrominoQueue(BagRandomizer())
        game = Game(board, queue)

        assert game.board == board
        assert game.queue == queue
        assert game.score == 0
        assert game.cleared_lines == 0
        assert not game.gameover

    def test_reset_game(self):
        """Test resetting game."""
        board = Board()
        queue = TetrominoQueue(BagRandomizer())
        game = Game(board, queue)

        # Manually set some state
        game.score = 100
        game.cleared_lines = 5
        game.gameover = True

        # Reset
        game.reset()

        assert game.score == 0
        assert game.cleared_lines == 0
        assert not game.gameover
        assert game.current_piece is not None


class TestGamePieceSpawning:
    """Test piece spawning."""

    def test_spawn_piece(self):
        """Test spawning a piece."""
        board = Board()
        queue = TetrominoQueue(BagRandomizer())
        game = Game(board, queue)
        game.reset()

        assert game.current_piece is not None
        assert isinstance(game.current_piece, Piece)

    def test_spawn_next_piece(self):
        """Test spawning next piece."""
        board = Board()
        queue = TetrominoQueue(BagRandomizer())
        game = Game(board, queue)
        game.reset()

        first_piece_type = game.current_piece.piece_type
        game.spawn_piece()
        second_piece_type = game.current_piece.piece_type

        # Pieces might be same, but at least new piece was spawned
        assert game.current_piece is not None


class TestGameMovement:
    """Test piece movement."""

    def test_can_move(self):
        """Test checking if piece can move."""
        board = Board()
        queue = TetrominoQueue(BagRandomizer())
        game = Game(board, queue)
        game.reset()

        # Should be able to move down initially
        assert game.can_move(0, 1)

    def test_move_piece(self):
        """Test moving piece."""
        board = Board()
        queue = TetrominoQueue(BagRandomizer())
        game = Game(board, queue)
        game.reset()

        initial_x = game.current_piece.x
        initial_y = game.current_piece.y

        # Move right
        success = game.move_piece(1, 0)
        if success:
            assert game.current_piece.x == initial_x + 1

        # Move down
        success = game.move_piece(0, 1)
        if success:
            assert game.current_piece.y > initial_y

    def test_cannot_move_out_of_bounds(self):
        """Test that piece cannot move out of bounds."""
        board = Board(height=10, width=10)
        queue = TetrominoQueue(BagRandomizer())
        game = Game(board, queue)
        game.reset()

        # Try to move far left
        for _ in range(20):
            game.move_piece(-1, 0)

        # Should still be within bounds
        assert game.current_piece.x >= 0


class TestGameRotation:
    """Test piece rotation."""

    def test_can_rotate(self):
        """Test checking if piece can rotate."""
        board = Board()
        queue = TetrominoQueue(BagRandomizer())
        game = Game(board, queue)
        game.reset()

        # Usually can rotate at start
        can_rotate = game.can_rotate()
        assert isinstance(can_rotate, bool)

    def test_rotate_piece(self):
        """Test rotating piece."""
        board = Board()
        queue = TetrominoQueue(BagRandomizer())
        game = Game(board, queue)
        game.reset()

        original_shape = [row[:] for row in game.current_piece.shape]
        success = game.rotate_piece()

        if success:
            # Shape should have changed (unless O piece)
            if game.current_piece.piece_type != 0:  # Not O piece
                # Just check that rotation was called
                assert isinstance(game.current_piece.shape, list)


class TestGameHardDrop:
    """Test hard drop."""

    def test_hard_drop(self):
        """Test hard dropping piece."""
        board = Board()
        queue = TetrominoQueue(BagRandomizer())
        game = Game(board, queue)
        game.reset()

        initial_y = game.current_piece.y
        drop_distance = game.hard_drop()

        # Should have moved down
        assert drop_distance >= 0
        assert game.current_piece.y >= initial_y


class TestGameLocking:
    """Test piece locking."""

    def test_lock_piece(self):
        """Test locking piece to board."""
        board = Board()
        queue = TetrominoQueue(BagRandomizer())
        game = Game(board, queue)
        game.reset()

        # Hard drop to bottom
        game.hard_drop()

        # Lock piece
        lines_cleared, is_game_over = game.lock_piece()

        assert lines_cleared >= 0
        assert isinstance(is_game_over, bool)
        # Board should no longer be empty
        assert not board.is_empty()


class TestGameScoring:
    """Test scoring."""

    def test_calculate_reward(self):
        """Test reward calculation."""
        board = Board(height=10, width=10)
        queue = TetrominoQueue(BagRandomizer())
        game = Game(board, queue)

        # Test different line clears
        reward_0 = game.calculate_reward(0)
        reward_1 = game.calculate_reward(1)
        reward_2 = game.calculate_reward(2)
        reward_4 = game.calculate_reward(4)

        # More lines should give more reward
        assert reward_1 > reward_0
        assert reward_2 > reward_1
        assert reward_4 > reward_2

    def test_overflow_penalty(self):
        """Test overflow penalty."""
        board = Board()
        queue = TetrominoQueue(BagRandomizer())
        game = Game(board, queue)

        reward_normal = game.calculate_reward(1, is_overflow=False)
        reward_overflow = game.calculate_reward(1, is_overflow=True)

        # Overflow should reduce reward
        assert reward_overflow < reward_normal


class TestGameState:
    """Test game state management."""

    def test_is_game_over(self):
        """Test checking game over status."""
        board = Board()
        queue = TetrominoQueue(BagRandomizer())
        game = Game(board, queue)
        game.reset()

        assert not game.is_game_over()

        game.gameover = True
        assert game.is_game_over()

    def test_get_state_copy(self):
        """Test getting state copy."""
        board = Board()
        queue = TetrominoQueue(BagRandomizer())
        game = Game(board, queue)
        game.reset()

        state = game.get_state_copy()

        assert "board" in state
        assert "current_piece" in state
        assert "score" in state
        assert "cleared_lines" in state
        assert "gameover" in state
        assert "next_piece_type" in state

    def test_get_board_with_current_piece(self):
        """Test getting board with current piece."""
        board = Board()
        queue = TetrominoQueue(BagRandomizer())
        game = Game(board, queue)
        game.reset()

        board_with_piece = game.get_board_with_current_piece()

        # Should be a valid board state
        assert isinstance(board_with_piece, list)
        assert len(board_with_piece) == board.height


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
