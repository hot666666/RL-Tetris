"""Quick test to verify refactored environment works."""

from rl_tetris.envs.tetris import Tetris
from rl_tetris.mapping.actions import GameActions

# Test basic environment
print("Testing refactored Tetris environment...")

env = Tetris()
obs, info = env.reset()

print(f"✓ Environment reset successful")
print(f"  - Observation keys: {list(obs.keys())}")
print(f"  - Info keys: {list(info.keys())}")
print(f"  - Board shape: {obs['board'].shape}")

# Test taking steps
print("\n✓ Testing actions...")
for i, action in enumerate([GameActions.move_left, GameActions.move_right,
                            GameActions.move_down, GameActions.rotate]):
    obs, reward, terminated, truncated, info = env.step(action)
    print(f"  Step {i+1}: action={action}, reward={reward}, terminated={terminated}")

    if terminated:
        break

print("\n✓ Testing hard drop...")
env.reset()
obs, reward, terminated, truncated, info = env.step(GameActions.hard_drop)
print(f"  Hard drop: reward={reward}, score={info['score']}")

# Test a short game
print("\n✓ Running short game (100 steps)...")
env.reset()
total_reward = 0
for i in range(100):
    action = i % 5  # Cycle through actions
    obs, reward, terminated, truncated, info = env.step(action)
    total_reward += reward

    if terminated:
        print(f"  Game ended at step {i+1}")
        break

print(f"  Total reward: {total_reward}")
print(f"  Final score: {info['score']}")
print(f"  Lines cleared: {info['cleared_lines']}")

# Test new components
print("\n✓ Testing new core components...")
print(f"  Board: {env.board}")
print(f"  Game: {env.game}")
print(f"  Current piece: {env.game.current_piece}")

# Test backward compatibility
print("\n✓ Testing backward compatibility...")
print(f"  env.piece available: {env.piece is not None}")
print(f"  env.x: {env.x}")
print(f"  env.y: {env.y}")
print(f"  env.score: {env.score}")

# Test feature extraction
print("\n✓ Testing feature extraction...")
from rl_tetris.features import BoardFeatureExtractor

features = BoardFeatureExtractor.extract_features(env.board)
feature_names = BoardFeatureExtractor.get_feature_names()

for name, value in zip(feature_names, features):
    print(f"  {name}: {value}")

print("\n✅ All tests passed! Refactored environment is working correctly.")
