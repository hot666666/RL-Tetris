"""Feature extractors for Tetris board analysis."""

import numpy as np
from typing import List, Tuple
from rl_tetris.core.board import Board


class BoardFeatureExtractor:
    """
    Extracts features from a Tetris board for use in learning algorithms.

    Features extracted:
    - Lines cleared (from action)
    - Number of holes
    - Bumpiness (variance in column heights)
    - Total height
    """

    @staticmethod
    def extract_features(
        board: Board,
        lines_cleared: int = 0
    ) -> np.ndarray:
        """
        Extract a feature vector from a board state.

        Args:
            board: Board instance to extract features from
            lines_cleared: Number of lines cleared (optional context)

        Returns:
            NumPy array of features: [lines_cleared, holes, bumpiness, height]
        """
        holes = board.get_holes()
        bumpiness, height = board.get_bumpiness_and_height()

        features = np.array([
            lines_cleared,
            holes,
            bumpiness,
            height
        ], dtype=np.float32)

        return features

    @staticmethod
    def extract_features_from_state(
        board_state: List[List[int]],
        lines_cleared: int = 0,
        board_height: int = 20,
        board_width: int = 10
    ) -> np.ndarray:
        """
        Extract features from a raw board state (without Board instance).

        Args:
            board_state: 2D list representing board state
            lines_cleared: Number of lines cleared
            board_height: Height of the board
            board_width: Width of the board

        Returns:
            NumPy array of features
        """
        # Create a temporary board instance
        temp_board = Board(board_height, board_width)
        temp_board.set_state(board_state)

        return BoardFeatureExtractor.extract_features(temp_board, lines_cleared)

    @staticmethod
    def get_feature_names() -> List[str]:
        """
        Get the names of features in the order they appear.

        Returns:
            List of feature names
        """
        return [
            "lines_cleared",
            "holes",
            "bumpiness",
            "total_height"
        ]

    @staticmethod
    def get_feature_dim() -> int:
        """
        Get the dimensionality of the feature vector.

        Returns:
            Number of features
        """
        return len(BoardFeatureExtractor.get_feature_names())

    @staticmethod
    def normalize_features(
        features: np.ndarray,
        max_lines: int = 4,
        max_holes: int = 200,
        max_bumpiness: int = 200,
        max_height: int = 200
    ) -> np.ndarray:
        """
        Normalize features to [0, 1] range.

        Args:
            features: Feature vector to normalize
            max_lines: Maximum lines that can be cleared at once
            max_holes: Maximum expected holes
            max_bumpiness: Maximum expected bumpiness
            max_height: Maximum expected total height

        Returns:
            Normalized feature vector
        """
        normalized = features.copy()
        max_values = np.array([max_lines, max_holes, max_bumpiness, max_height])

        # Avoid division by zero
        max_values = np.where(max_values == 0, 1, max_values)

        normalized = normalized / max_values
        normalized = np.clip(normalized, 0, 1)

        return normalized


class AdvancedFeatureExtractor(BoardFeatureExtractor):
    """
    Extended feature extractor with additional metrics.
    """

    @staticmethod
    def extract_advanced_features(board: Board, lines_cleared: int = 0) -> np.ndarray:
        """
        Extract an extended feature vector with additional metrics.

        Args:
            board: Board instance
            lines_cleared: Number of lines cleared

        Returns:
            Extended feature vector
        """
        # Get basic features
        basic_features = BoardFeatureExtractor.extract_features(board, lines_cleared)

        # Get additional features
        column_heights = board.get_column_heights()
        max_height = max(column_heights) if column_heights else 0
        min_height = min(column_heights) if column_heights else 0
        height_variance = np.var(column_heights) if column_heights else 0

        # Count complete rows
        complete_rows = sum(1 for i in range(board.height) if board.is_row_full(i))

        # Calculate height-weighted holes
        board_state = board.get_state()
        weighted_holes = AdvancedFeatureExtractor._get_weighted_holes(board_state)

        # Wells (gaps between columns)
        wells = AdvancedFeatureExtractor._count_wells(column_heights)

        advanced_features = np.array([
            *basic_features,
            max_height,
            min_height,
            height_variance,
            complete_rows,
            weighted_holes,
            wells
        ], dtype=np.float32)

        return advanced_features

    @staticmethod
    def _get_weighted_holes(board_state: List[List[int]]) -> float:
        """
        Calculate weighted holes (holes near bottom are worse).

        Args:
            board_state: 2D list of board state

        Returns:
            Weighted hole count
        """
        height = len(board_state)
        width = len(board_state[0]) if board_state else 0
        weighted_sum = 0.0

        for col_idx in range(width):
            found_block = False
            for row_idx in range(height):
                if board_state[row_idx][col_idx] > 0:
                    found_block = True
                elif found_block and board_state[row_idx][col_idx] == 0:
                    # Weight increases with depth (row_idx)
                    weight = (row_idx + 1) / height
                    weighted_sum += weight

        return weighted_sum

    @staticmethod
    def _count_wells(column_heights: List[int]) -> int:
        """
        Count wells (columns significantly lower than neighbors).

        Args:
            column_heights: List of column heights

        Returns:
            Number of wells
        """
        if len(column_heights) < 2:
            return 0

        wells = 0
        for i, height in enumerate(column_heights):
            left_higher = i == 0 or column_heights[i - 1] > height
            right_higher = i == len(column_heights) - 1 or column_heights[i + 1] > height

            if left_higher and right_higher:
                wells += 1

        return wells

    @staticmethod
    def get_feature_names() -> List[str]:
        """Get names of advanced features."""
        return [
            "lines_cleared",
            "holes",
            "bumpiness",
            "total_height",
            "max_height",
            "min_height",
            "height_variance",
            "complete_rows",
            "weighted_holes",
            "wells"
        ]

    @staticmethod
    def get_feature_dim() -> int:
        """Get dimensionality of advanced features."""
        return len(AdvancedFeatureExtractor.get_feature_names())
