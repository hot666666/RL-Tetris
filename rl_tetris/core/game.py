"""Game module for managing Tetris game logic and state."""

from typing import Optional, Tuple
from rl_tetris.core.board import Board
from rl_tetris.core.piece import Piece
from rl_tetris.tetromino_queue import TetrominoQueue
from rl_tetris.randomizer import Randomizer


class Game:
    """
    Manages Tetris game logic and orchestration.

    Responsibilities:
    - Game state management (score, lines cleared, game over)
    - Piece spawning and movement
    - Reward calculation
    - Game flow orchestration
    """

    def __init__(
        self,
        board: Board,
        queue: TetrominoQueue,
        initial_position: str = "center"
    ):
        """
        Initialize a new game.

        Args:
            board: Board instance to use
            queue: TetrominoQueue instance for piece generation
            initial_position: How to position new pieces ("center" or "left")
        """
        self.board = board
        self.queue = queue
        self.initial_position = initial_position

        self.current_piece: Optional[Piece] = None
        self.score = 0
        self.cleared_lines = 0
        self.gameover = False

    def reset(self) -> None:
        """Reset the game to initial state."""
        self.board.reset()
        self.queue.reset()
        self.score = 0
        self.cleared_lines = 0
        self.gameover = False
        self.spawn_piece()

    def spawn_piece(self) -> bool:
        """
        Spawn a new piece at the top of the board.

        Returns:
            True if piece was spawned successfully, False if game over
        """
        piece_type = self.queue.pop()
        x, y = self._calculate_spawn_position(piece_type)

        self.current_piece = Piece(piece_type, x, y)

        # Check if the new piece collides immediately (game over condition)
        if self.board.check_collision(self.current_piece.shape, x, y):
            self.gameover = True
            return False

        return True

    def _calculate_spawn_position(self, piece_type: int) -> Tuple[int, int]:
        """
        Calculate the spawn position for a piece.

        Args:
            piece_type: Type of piece to spawn

        Returns:
            Tuple of (x, y) spawn position
        """
        shape = Piece.get_shape(piece_type)
        piece_width = len(shape[0]) if shape else 0

        if self.initial_position == "center":
            x = self.board.width // 2 - piece_width // 2
        else:  # "left"
            x = 0

        y = 0
        return x, y

    def can_move(self, dx: int, dy: int) -> bool:
        """
        Check if the current piece can move by the given offset.

        Args:
            dx: Change in x position
            dy: Change in y position

        Returns:
            True if move is valid, False otherwise
        """
        if not self.current_piece:
            return False

        new_x = self.current_piece.x + dx
        new_y = self.current_piece.y + dy

        return not self.board.check_collision(
            self.current_piece.shape,
            new_x,
            new_y
        )

    def move_piece(self, dx: int, dy: int) -> bool:
        """
        Move the current piece by the given offset if valid.

        Args:
            dx: Change in x position
            dy: Change in y position

        Returns:
            True if move was successful, False otherwise
        """
        if self.can_move(dx, dy):
            self.current_piece.move(dx, dy)
            return True
        return False

    def can_rotate(self) -> bool:
        """
        Check if the current piece can be rotated clockwise.

        Returns:
            True if rotation is valid, False otherwise
        """
        if not self.current_piece:
            return False

        rotated_shape = Piece.get_rotated_clockwise(self.current_piece.shape)
        return not self.board.check_collision(
            rotated_shape,
            self.current_piece.x,
            self.current_piece.y
        )

    def rotate_piece(self) -> bool:
        """
        Rotate the current piece clockwise if valid.

        Returns:
            True if rotation was successful, False otherwise
        """
        if self.can_rotate():
            self.current_piece.rotate_clockwise()
            return True
        return False

    def hard_drop(self) -> int:
        """
        Drop the current piece to the lowest valid position.

        Returns:
            Number of cells the piece dropped
        """
        if not self.current_piece:
            return 0

        drop_distance = 0
        while self.can_move(0, 1):
            self.current_piece.move(0, 1)
            drop_distance += 1

        return drop_distance

    def lock_piece(self) -> Tuple[int, bool]:
        """
        Lock the current piece to the board and handle line clearing.

        Returns:
            Tuple of (lines_cleared, is_game_over)
        """
        if not self.current_piece:
            return 0, True

        # Check if piece is overflowing the top (game over condition)
        is_overflow = self._is_piece_overflowing()

        # Place the piece on the board
        self.board.place_piece(
            self.current_piece.shape,
            self.current_piece.x,
            self.current_piece.y
        )

        # Clear full rows
        lines_cleared = self.board.clear_full_rows()
        self.cleared_lines += lines_cleared

        # Calculate and add reward
        reward = self.calculate_reward(lines_cleared, is_overflow)
        self.score += reward

        if is_overflow:
            self.gameover = True
            return lines_cleared, True

        # Spawn next piece
        success = self.spawn_piece()
        return lines_cleared, not success

    def _is_piece_overflowing(self) -> bool:
        """
        Check if the current piece is overflowing above the board.

        Returns:
            True if piece is overflowing, False otherwise
        """
        if not self.current_piece:
            return False

        # Check if any part of the piece is above row 0
        # AND colliding with existing blocks
        for py in range(len(self.current_piece.shape)):
            for px in range(len(self.current_piece.shape[py])):
                if self.current_piece.shape[py][px] == 0:
                    continue

                board_y = self.current_piece.y + py
                board_x = self.current_piece.x + px

                # If piece cell is above board and will collide
                if board_y < 0:
                    return True

                # Check collision with existing blocks in top rows
                if board_y >= 0 and self.board.is_cell_occupied(board_x, board_y):
                    # If there's collision near the top, it might be overflow
                    if self.current_piece.y <= 1:
                        return True

        return False

    def calculate_reward(self, lines_cleared: int, is_overflow: bool = False) -> int:
        """
        Calculate reward based on lines cleared and game state.

        Args:
            lines_cleared: Number of lines cleared
            is_overflow: Whether the piece caused overflow (game over)

        Returns:
            Reward value
        """
        base_reward = 1 + (lines_cleared ** 2) * self.board.width

        if is_overflow:
            return base_reward - 5

        return base_reward

    def get_next_piece_type(self) -> int:
        """
        Get the type of the next piece without popping it.

        Returns:
            Next piece type index
        """
        return self.queue.peek()

    def is_game_over(self) -> bool:
        """
        Check if the game is over.

        Returns:
            True if game is over, False otherwise
        """
        return self.gameover

    def get_state_copy(self) -> dict:
        """
        Get a copy of the current game state.

        Returns:
            Dictionary containing game state
        """
        return {
            "board": self.board.get_state(),
            "current_piece": self.current_piece.copy() if self.current_piece else None,
            "score": self.score,
            "cleared_lines": self.cleared_lines,
            "gameover": self.gameover,
            "next_piece_type": self.get_next_piece_type()
        }

    def get_board_with_current_piece(self):
        """
        Get the board state with the current piece placed.

        Returns:
            Board state with current piece
        """
        if not self.current_piece:
            return self.board.get_state()

        return self.board.get_board_with_piece(
            self.current_piece.shape,
            self.current_piece.x,
            self.current_piece.y
        )

    def __repr__(self) -> str:
        """String representation of the game."""
        return (
            f"Game(score={self.score}, lines={self.cleared_lines}, "
            f"gameover={self.gameover})"
        )
