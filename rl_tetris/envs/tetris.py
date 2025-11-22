"""Tetris Gymnasium environment using refactored components."""

import numpy as np
import gymnasium as gym
from gymnasium.spaces import Box, Discrete
from dataclasses import fields
from typing import Optional

from rl_tetris.core.board import Board
from rl_tetris.core.piece import Piece
from rl_tetris.core.game import Game
from rl_tetris.game_state import GameStates
from rl_tetris.tetromino_queue import TetrominoQueue
from rl_tetris.renderer import Renderer
from rl_tetris.mapping.actions import GameActions


class Tetris(gym.Env):
    """
    Tetris Gymnasium environment.

    This environment provides a standard Gymnasium interface for playing Tetris.
    It uses refactored components for better modularity and testability:
    - Board: Manages board state and operations
    - Piece: Handles piece shapes and rotations
    - Game: Orchestrates game logic and scoring
    """

    metadata = {
        "render_modes": ["human", "animate"],
        "render_fps": 1
    }

    def __init__(
        self,
        render_mode: Optional[str] = None,
        height: int = 20,
        width: int = 10,
        block_size: int = 30,
        randomizer=None
    ):
        """
        Initialize Tetris environment.

        Args:
            render_mode: Rendering mode ("human", "animate", or None)
            height: Board height in cells
            width: Board width in cells
            block_size: Size of each block for rendering
            randomizer: Randomizer instance for piece generation
        """
        self.height = height
        self.width = width

        # Initialize components
        self.board = Board(height, width)
        self.queue = TetrominoQueue(randomizer=randomizer)
        self.game = Game(self.board, self.queue, initial_position="center")
        self.renderer = Renderer(height, width, block_size)

        # Gymnasium spaces
        self.observation_space = gym.spaces.Dict({
            "board": Box(
                low=0,
                high=Piece.num_piece_types(),
                shape=(self.height, self.width),
                dtype=np.uint8,
            ),
            "p_id": Discrete(Piece.num_piece_types()),
            "x": Discrete(self.width),
            "y": Discrete(self.height),
        })

        self.actions = GameActions
        self.action_space = Discrete(len(fields(GameActions)))
        self.reward_range = (-4, 17)

        self.render_mode = render_mode

        # For backward compatibility with wrappers
        self.PIECES = Piece.SHAPES
        self.piece = None  # Current piece shape (for wrappers)
        self.x = 0  # Current piece x (for wrappers)
        self.y = 0  # Current piece y (for wrappers)
        self.idx = 0  # Current piece type (for wrappers)
        self.score = 0
        self.cleared_lines = 0
        self.gameover = False

    def get_observation(self) -> dict:
        """
        Get the current observation.

        Returns:
            Dictionary containing board state and piece information
        """
        if not self.game.current_piece:
            # Fallback if no current piece
            return {
                "board": np.array(self.board.get_state(), dtype=np.uint8),
                "p_id": 0,
                "x": 0,
                "y": 0,
            }

        return {
            "board": np.array(self.board.get_state(), dtype=np.uint8),
            "p_id": self.game.current_piece.piece_type,
            "x": self.game.current_piece.x,
            "y": self.game.current_piece.y,
        }

    def get_info(self) -> dict:
        """
        Get additional information about the game state.

        Returns:
            Dictionary with score and cleared lines
        """
        return {
            "score": self.game.score,
            "cleared_lines": self.game.cleared_lines,
        }

    def reset(
        self,
        *,
        seed: int | None = None,
        options: dict | None = None
    ) -> tuple[dict, dict]:
        """
        Reset the environment to initial state.

        Args:
            seed: Random seed (optional)
            options: Additional options (optional)

        Returns:
            Tuple of (observation, info)
        """
        super().reset(seed=seed)

        self.game.reset()
        self._sync_state_for_wrappers()

        return self.get_observation(), self.get_info()

    def step(self, action: int) -> tuple[dict, float, bool, bool, dict]:
        """
        Execute one step in the environment.

        Args:
            action: Action to take (from GameActions)

        Returns:
            Tuple of (observation, reward, terminated, truncated, info)
        """
        reward = 0
        lines_cleared = 0

        # Execute action on current piece
        if action == GameActions.move_left:
            self.game.move_piece(-1, 0)
        elif action == GameActions.move_right:
            self.game.move_piece(1, 0)
        elif action == GameActions.move_down:
            self.game.move_piece(0, 1)
        elif action == GameActions.rotate:
            self.game.rotate_piece()
        elif action == GameActions.hard_drop:
            self.game.hard_drop()
            if self.render_mode == "animate":
                self.render()

        # Check if piece can no longer move down (needs to lock)
        if not self.game.can_move(0, 1):
            lines_cleared, is_game_over = self.game.lock_piece()

            if self.render_mode == "animate":
                self.render()

            if is_game_over:
                reward = self.game.calculate_reward(lines_cleared, is_overflow=True)
                self._sync_state_for_wrappers()
                return (
                    self.get_observation(),
                    reward,
                    True,  # terminated
                    False,  # truncated
                    self.get_info()
                )

            reward = self.game.calculate_reward(lines_cleared, is_overflow=False)

        self._sync_state_for_wrappers()

        return (
            self.get_observation(),
            reward,
            self.game.is_game_over(),
            False,  # truncated
            self.get_info()
        )

    def _sync_state_for_wrappers(self) -> None:
        """
        Sync state to legacy attributes for backward compatibility with wrappers.
        """
        self.score = self.game.score
        self.cleared_lines = self.game.cleared_lines
        self.gameover = self.game.is_game_over()

        if self.game.current_piece:
            self.piece = self.game.current_piece.get_shape_copy()
            self.x = self.game.current_piece.x
            self.y = self.game.current_piece.y
            self.idx = self.game.current_piece.piece_type
        else:
            self.piece = None
            self.x = 0
            self.y = 0
            self.idx = 0

    # ========================================
    # Methods for backward compatibility
    # ========================================

    def check_collision(self, piece: list, px: int, py: int) -> bool:
        """Check collision (backward compatibility)."""
        return self.board.check_collision(piece, px, py)

    def get_rotated_piece(self, piece: list) -> list:
        """Rotate piece (backward compatibility)."""
        return Piece.get_rotated_clockwise(piece)

    def get_board_with_piece(self, piece: list, px: int, py: int) -> list:
        """Get board with piece (backward compatibility)."""
        return self.board.get_board_with_piece(piece, px, py)

    def clear_full_rows(self, board_state: list) -> tuple[int, list]:
        """Clear full rows (backward compatibility)."""
        temp_board = Board(self.height, self.width)
        temp_board.set_state(board_state)
        lines_cleared = temp_board.clear_full_rows()
        return lines_cleared, temp_board.get_state()

    def clear_full_rows_(self, board_state: np.ndarray) -> tuple[int, np.ndarray]:
        """
        Clear full rows using numpy operations (backward compatibility).

        Args:
            board_state: NumPy array representing the board

        Returns:
            Tuple of (lines_cleared, new_board_state)
        """
        board_array = np.array(board_state)
        mask = np.all(board_array != 0, axis=1)
        cleared_board = board_array[~mask]
        lines_cleared = np.sum(mask)

        # Add empty rows at the top
        if lines_cleared > 0:
            empty_rows = np.zeros((lines_cleared, self.width), dtype=board_array.dtype)
            cleared_board = np.concatenate([empty_rows, cleared_board])

        return int(lines_cleared), cleared_board

    def get_holes(self, board_state: list) -> int:
        """Get number of holes (backward compatibility)."""
        temp_board = Board(self.height, self.width)
        temp_board.set_state(board_state)
        return temp_board.get_holes()

    def get_bumpiness_and_height(self, board_state: list) -> tuple[int, int]:
        """Get bumpiness and height (backward compatibility)."""
        temp_board = Board(self.height, self.width)
        temp_board.set_state(board_state)
        return temp_board.get_bumpiness_and_height()

    def spawn_next_piece(self) -> None:
        """Spawn next piece (backward compatibility)."""
        success = self.game.spawn_piece()
        if not success:
            self.gameover = True
        self._sync_state_for_wrappers()

    def get_reward(self, lines_cleared: int) -> int:
        """Calculate reward (backward compatibility)."""
        return self.game.calculate_reward(lines_cleared, is_overflow=False)

    def truncate_overflow_piece(self, piece: list, px: int, py: int) -> bool:
        """
        Check for overflow (backward compatibility).
        Note: This is a simplified version for compatibility.
        """
        # Check if piece is at top and colliding
        for y in range(len(piece)):
            for x in range(len(piece[y])):
                if piece[y][x] == 0:
                    continue
                board_y = py + y
                if board_y < 0:
                    return True
                if board_y < self.height and px + x < self.width:
                    if self.board.is_cell_occupied(px + x, board_y):
                        if py <= 1:
                            return True
        return False

    # ========================================
    # Rendering
    # ========================================

    def get_render_state(self) -> GameStates:
        """
        Get current game state for rendering.

        Returns:
            GameStates instance
        """
        board_with_piece = self.game.get_board_with_current_piece()
        next_piece_type = self.game.get_next_piece_type()
        next_piece_shape = Piece.get_shape(next_piece_type)

        return GameStates(
            board=board_with_piece,
            score=self.game.score,
            next_piece=next_piece_shape
        )

    def render(self):
        """Render the game."""
        if self.render_mode in ["human", "animate"]:
            self.renderer.render(self.get_render_state())
