"""Tests for Wrapper classes."""

import pytest
import numpy as np
from rl_tetris.envs.tetris import Tetris
from rl_tetris.wrapper.Grouped import GroupedWrapper
from rl_tetris.wrapper.Observation import BoardObservation, GroupedFeaturesObservation


class TestGroupedWrapper:
    """Test GroupedWrapper."""

    def test_initialization(self):
        """Test GroupedWrapper initialization."""
        env = Tetris()
        wrapped_env = GroupedWrapper(env)

        assert wrapped_env is not None
        assert wrapped_env.action_space.n == env.width * 4  # 10 * 4 = 40

    def test_observation_space(self):
        """Test observation space structure."""
        env = Tetris()
        wrapped_env = GroupedWrapper(env)

        assert "boards" in wrapped_env.observation_space.spaces
        assert "action_mask" in wrapped_env.observation_space.spaces

    def test_observation_space_with_features(self):
        """Test observation space with feature wrapper."""
        env = Tetris()
        obs_wrapper = GroupedFeaturesObservation(env)
        wrapped_env = GroupedWrapper(env, observation_wrapper=obs_wrapper)

        assert "boards" in wrapped_env.observation_space.spaces
        assert "action_mask" in wrapped_env.observation_space.spaces
        assert "features" in wrapped_env.observation_space.spaces

    def test_encode_decode_action(self):
        """Test action encoding and decoding."""
        env = Tetris()
        wrapped_env = GroupedWrapper(env)

        # Test encoding
        action = wrapped_env.encode_action(x=3, r=2)
        assert action == 3 * 4 + 2  # 14

        # Test decoding
        x, r = wrapped_env.decode_action(14)
        assert x == 3
        assert r == 2

    def test_encode_decode_roundtrip(self):
        """Test that encode/decode are inverse operations."""
        env = Tetris()
        wrapped_env = GroupedWrapper(env)

        for x in range(env.width):
            for r in range(4):
                action = wrapped_env.encode_action(x, r)
                decoded_x, decoded_r = wrapped_env.decode_action(action)
                assert decoded_x == x
                assert decoded_r == r

    def test_reset(self):
        """Test resetting wrapped environment."""
        env = Tetris()
        wrapped_env = GroupedWrapper(env)

        obs, info = wrapped_env.reset()

        assert "boards" in obs
        assert "action_mask" in obs
        assert "board" in info
        assert "action_mapping" in info

    def test_reset_observation_shape(self):
        """Test observation shapes after reset."""
        env = Tetris(height=20, width=10)
        wrapped_env = GroupedWrapper(env)

        obs, info = wrapped_env.reset()

        # boards should have shape (action_space, height, width)
        assert obs["boards"].shape == (40, 20, 10)
        # action_mask should have shape (action_space,)
        assert obs["action_mask"].shape == (40,)

    def test_action_mask_validity(self):
        """Test that action mask contains valid values."""
        env = Tetris()
        wrapped_env = GroupedWrapper(env)

        obs, info = wrapped_env.reset()

        # All values should be 0 or 1
        assert np.all((obs["action_mask"] == 0) | (obs["action_mask"] == 1))
        # At least one action should be valid
        assert np.sum(obs["action_mask"]) > 0

    def test_step(self):
        """Test stepping through wrapped environment."""
        env = Tetris()
        wrapped_env = GroupedWrapper(env)

        obs, info = wrapped_env.reset()

        # Get a valid action
        valid_actions = np.where(obs["action_mask"] == 1)[0]
        action = valid_actions[0]

        obs, reward, terminated, truncated, info = wrapped_env.step(action)

        assert "boards" in obs
        assert "action_mask" in obs
        assert isinstance(reward, (int, float))
        assert isinstance(terminated, bool)

    def test_step_with_invalid_action(self):
        """Test stepping with an invalid action."""
        env = Tetris()
        wrapped_env = GroupedWrapper(env)

        obs, info = wrapped_env.reset()

        # Find an invalid action
        invalid_actions = np.where(obs["action_mask"] == 0)[0]

        if len(invalid_actions) > 0:
            action = invalid_actions[0]
            # Should still work but may have different behavior
            obs, reward, terminated, truncated, info = wrapped_env.step(action)
            assert obs is not None

    def test_action_mapping_in_info(self):
        """Test that action mapping is provided in info."""
        env = Tetris()
        wrapped_env = GroupedWrapper(env)

        obs, info = wrapped_env.reset()

        assert "action_mapping" in info
        # Action mapping should match valid actions
        valid_actions = np.where(obs["action_mask"] == 1)[0]
        assert np.array_equal(info["action_mapping"], valid_actions)

    def test_with_observation_wrapper(self):
        """Test GroupedWrapper with ObservationWrapper."""
        env = Tetris()
        obs_wrapper = GroupedFeaturesObservation(env)
        wrapped_env = GroupedWrapper(env, observation_wrapper=obs_wrapper)

        obs, info = wrapped_env.reset()

        assert "features" in obs
        assert obs["features"].shape == (40, 4)  # 40 actions, 4 features each

    def test_multiple_steps(self):
        """Test multiple steps in wrapped environment."""
        env = Tetris()
        wrapped_env = GroupedWrapper(env)

        obs, info = wrapped_env.reset()

        for _ in range(10):
            valid_actions = np.where(obs["action_mask"] == 1)[0]
            if len(valid_actions) == 0:
                break

            action = valid_actions[0]
            obs, reward, terminated, truncated, info = wrapped_env.step(action)

            if terminated:
                break


class TestBoardObservation:
    """Test BoardObservation wrapper."""

    def test_initialization(self):
        """Test BoardObservation initialization."""
        env = Tetris()
        wrapped_env = BoardObservation(env)

        assert wrapped_env is not None

    def test_observation_returns_boards(self):
        """Test that observation returns only boards."""
        env = Tetris()
        wrapped_env = BoardObservation(GroupedWrapper(env))

        obs, info = wrapped_env.reset()

        # Should return boards array directly
        assert isinstance(obs, np.ndarray)
        assert obs.shape == (40, 20, 10)  # (actions, height, width)

    def test_step(self):
        """Test stepping with BoardObservation."""
        env = Tetris()
        wrapped_env = BoardObservation(GroupedWrapper(env))

        obs, info = wrapped_env.reset()

        # Use first action (usually valid)
        obs, reward, terminated, truncated, info = wrapped_env.step(0)

        assert isinstance(obs, np.ndarray)


class TestGroupedFeaturesObservation:
    """Test GroupedFeaturesObservation wrapper."""

    def test_initialization(self):
        """Test GroupedFeaturesObservation initialization."""
        env = Tetris()
        wrapped_env = GroupedFeaturesObservation(env)

        assert wrapped_env is not None

    def test_extract_board_features(self):
        """Test feature extraction from board."""
        env = Tetris()
        wrapped_env = GroupedFeaturesObservation(env)

        # Create a simple board
        board = np.zeros((20, 10), dtype=np.uint8)
        board[19] = 1  # Bottom row filled

        features = wrapped_env.extract_board_features(board)

        assert len(features) == 4
        assert features[0] >= 0  # lines_cleared
        assert features[1] >= 0  # holes
        assert features[2] >= 0  # bumpiness
        assert features[3] >= 0  # height

    def test_observation_shape(self):
        """Test observation shape."""
        env = Tetris()
        wrapped_env = GroupedFeaturesObservation(GroupedWrapper(env))

        obs, info = wrapped_env.reset()

        # Should return features array
        assert isinstance(obs, np.ndarray)
        assert obs.shape == (40, 4)  # 40 actions, 4 features each

    def test_observation_with_mask(self):
        """Test that masked actions have zero features."""
        env = Tetris()
        grouped_env = GroupedWrapper(env)
        wrapped_env = GroupedFeaturesObservation(grouped_env)

        grouped_obs, info = grouped_env.reset()
        features = wrapped_env.observation(grouped_obs)

        # Check that invalid actions have zero features
        mask = grouped_obs["action_mask"]
        for i, m in enumerate(mask):
            if m == 0:
                assert np.allclose(features[i], np.zeros(4))

    def test_feature_values_valid(self):
        """Test that feature values are valid."""
        env = Tetris()
        wrapped_env = GroupedFeaturesObservation(GroupedWrapper(env))

        obs, info = wrapped_env.reset()

        # All features should be non-negative
        assert np.all(obs >= 0)
        # Features should not be NaN or Inf
        assert np.all(np.isfinite(obs))

    def test_step(self):
        """Test stepping with GroupedFeaturesObservation."""
        env = Tetris()
        wrapped_env = GroupedFeaturesObservation(GroupedWrapper(env))

        obs, info = wrapped_env.reset()

        # Use first action
        obs, reward, terminated, truncated, info = wrapped_env.step(0)

        assert isinstance(obs, np.ndarray)
        assert obs.shape == (40, 4)


class TestWrapperCombinations:
    """Test combinations of wrappers."""

    def test_grouped_with_features(self):
        """Test GroupedWrapper with GroupedFeaturesObservation."""
        env = Tetris()
        obs_wrapper = GroupedFeaturesObservation(env)
        wrapped_env = GroupedWrapper(env, observation_wrapper=obs_wrapper)

        obs, info = wrapped_env.reset()

        assert "boards" in obs
        assert "action_mask" in obs
        assert "features" in obs
        assert obs["features"].shape == (40, 4)

    def test_full_game_with_wrappers(self):
        """Test playing a short game with wrappers."""
        env = Tetris()
        wrapped_env = GroupedWrapper(env)

        obs, info = wrapped_env.reset()
        total_reward = 0
        steps = 0

        for _ in range(50):
            valid_actions = np.where(obs["action_mask"] == 1)[0]
            if len(valid_actions) == 0:
                break

            action = valid_actions[0]
            obs, reward, terminated, truncated, info = wrapped_env.step(action)
            total_reward += reward
            steps += 1

            if terminated:
                break

        assert steps > 0
        assert isinstance(total_reward, (int, float))

    def test_reset_after_done(self):
        """Test resetting after game is done."""
        env = Tetris()
        wrapped_env = GroupedWrapper(env)

        obs, info = wrapped_env.reset()

        # Play until done
        for _ in range(1000):
            valid_actions = np.where(obs["action_mask"] == 1)[0]
            if len(valid_actions) == 0:
                break

            action = valid_actions[0]
            obs, reward, terminated, truncated, info = wrapped_env.step(action)

            if terminated:
                break

        # Reset after done
        obs, info = wrapped_env.reset()

        assert "boards" in obs
        assert "action_mask" in obs
        assert np.sum(obs["action_mask"]) > 0  # Should have valid actions


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
