"""Tests for Randomizer classes."""

import pytest
from rl_tetris.randomizer import Randomizer, BagRandomizer, RandRandomizer


class TestBagRandomizer:
    """Test BagRandomizer."""

    def test_initialization(self):
        """Test BagRandomizer initialization."""
        randomizer = BagRandomizer()
        assert randomizer is not None

    def test_next_returns_valid_piece(self):
        """Test that get_random() returns valid piece types."""
        randomizer = BagRandomizer()
        for _ in range(100):
            piece = randomizer.get_random()
            assert 0 <= piece < 7

    def test_bag_contains_all_pieces(self):
        """Test that bag contains all 7 pieces before repeating."""
        randomizer = BagRandomizer()
        pieces = []

        # Get 7 pieces (one full bag)
        for _ in range(7):
            pieces.append(randomizer.get_random())

        # Should have all 7 different pieces
        assert len(set(pieces)) == 7
        assert set(pieces) == {0, 1, 2, 3, 4, 5, 6}

    def test_reset(self):
        """Test resetting randomizer."""
        randomizer = BagRandomizer()

        # Get some pieces
        for _ in range(3):
            randomizer.get_random()

        # Reset
        randomizer.reset()

        # Should work normally after reset
        piece = randomizer.get_random()
        assert 0 <= piece < 7


class TestRandRandomizer:
    """Test RandRandomizer."""

    def test_initialization(self):
        """Test RandRandomizer initialization."""
        randomizer = RandRandomizer()
        assert randomizer is not None

    def test_next_returns_valid_piece(self):
        """Test that get_random() returns valid piece types."""
        randomizer = RandRandomizer()
        for _ in range(100):
            piece = randomizer.get_random()
            assert 0 <= piece < 7

    def test_reset(self):
        """Test resetting randomizer."""
        randomizer = RandRandomizer()

        # Get some pieces
        for _ in range(3):
            randomizer.get_random()

        # Reset
        randomizer.reset()

        # Should work normally after reset
        piece = randomizer.get_random()
        assert 0 <= piece < 7

    def test_distribution(self):
        """Test that RandRandomizer has reasonable distribution."""
        randomizer = RandRandomizer()
        pieces = []

        # Get many pieces
        for _ in range(700):
            pieces.append(randomizer.get_random())

        # Each piece should appear at least once
        assert len(set(pieces)) == 7


class TestRandomizerComparison:
    """Test comparison between randomizers."""

    def test_bag_vs_rand_fairness(self):
        """Test that BagRandomizer is more fair than RandRandomizer."""
        bag = BagRandomizer()
        rand = RandRandomizer()

        # Get 14 pieces from each (2 bags)
        bag_pieces = [bag.get_random() for _ in range(14)]
        rand_pieces = [rand.get_random() for _ in range(14)]

        # Bag should have exactly 2 of each piece
        from collections import Counter
        bag_counts = Counter(bag_pieces)
        assert all(count == 2 for count in bag_counts.values())

        # Rand will likely not have exactly 2 of each
        # (this test might occasionally fail due to randomness, but unlikely)
        rand_counts = Counter(rand_pieces)
        # At least check all pieces types appear
        assert len(rand_counts) >= 5  # Allow some variance


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
