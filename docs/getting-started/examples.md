# Examples

RL-Tetris 저장소에는 여러 가지 예제가 포함되어 있습니다.

## Random Agent

### Basic Random Agent

가장 기본적인 랜덤 에이전트:

```python
# examples/random_env.py
import time
import gymnasium as gym

env = gym.make("RL-Tetris-v0", render_mode="human")
obs, info = env.reset()

done = False
total_reward = 0

while not done:
    env.render()
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    total_reward += reward
    done = terminated or truncated
    time.sleep(0.05)

print(f"Total Reward: {total_reward}")
```

### Grouped Random Agent

GroupedWrapper를 사용한 랜덤 에이전트:

```python
# examples/random_grouped_env.py
import time
import gymnasium as gym
from rl_tetris.wrapper.Grouped import GroupedWrapper
from rl_tetris.wrapper.Observation import GroupedFeaturesObservation

env = gym.make("RL-Tetris-v0", render_mode="human")
env = GroupedWrapper(env, observation_wrapper=GroupedFeaturesObservation(env))

obs, info = env.reset()
done = False

while not done:
    env.render()
    # action_mask를 사용하여 유효한 액션만 선택
    action = env.action_space.sample(obs["action_mask"])
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
    time.sleep(1)
```

## Deep Q-Learning

### DQN Training

GroupedWrapper와 특징 기반 DQN 학습:

```python
# examples/train_grouped_model.py
import torch
import torch.nn as nn
import gymnasium as gym
from rl_tetris.wrapper.Grouped import GroupedWrapper
from rl_tetris.wrapper.Observation import GroupedFeaturesObservation

class DQN(nn.Module):
    def __init__(self, input_dim, output_dim=1):
        super(DQN, self).__init__()
        self.fc1 = nn.Linear(input_dim, 128)
        self.fc2 = nn.Linear(128, 64)
        self.fc3 = nn.Linear(64, output_dim)

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return self.fc3(x)

# 환경 생성
env = gym.make("RL-Tetris-v0")
env = GroupedWrapper(env, observation_wrapper=GroupedFeaturesObservation(env))

# 모델 초기화
model = DQN(input_dim=4)  # 4개의 특징
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

# 학습 루프
for episode in range(1000):
    obs, info = env.reset()
    done = False
    total_reward = 0

    while not done:
        # 특징을 사용하여 Q값 계산
        features = torch.FloatTensor(obs["features"])
        q_values = model(features).squeeze()

        # action_mask를 적용하여 유효한 액션 선택
        q_values[obs["action_mask"] == 0] = float('-inf')
        action = q_values.argmax().item()

        # 환경 스텝
        next_obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        done = terminated or truncated

        # 학습 로직 (간단한 예시)
        # ... (전체 코드는 examples/ 폴더 참조)

        obs = next_obs

    print(f"Episode {episode}: Reward = {total_reward}")
```

## Custom Feature Extractor

자신만의 특징 추출기를 만들 수 있습니다:

```python
from rl_tetris.core import Board
import numpy as np

class CustomFeatureExtractor:
    @staticmethod
    def extract_features(board: Board, lines_cleared: int = 0):
        """
        Custom features:
        - Lines cleared
        - Holes
        - Bumpiness
        - Max height
        - Average height
        """
        holes = board.get_holes()
        bumpiness, total_height = board.get_bumpiness_and_height()
        heights = board.get_column_heights()

        return np.array([
            lines_cleared,
            holes,
            bumpiness,
            max(heights),
            np.mean(heights)
        ], dtype=np.float32)

# 사용 예시
from rl_tetris.envs.tetris import Tetris

env = Tetris()
obs, info = env.reset()

# 보드에서 특징 추출
features = CustomFeatureExtractor.extract_features(env.board)
print(f"Features: {features}")
```

## Direct Component Usage

컴포넌트를 직접 사용할 수도 있습니다:

```python
from rl_tetris.core import Board, Piece, Game
from rl_tetris.tetromino_queue import TetrominoQueue
from rl_tetris.randomizer import BagRandomizer

# 컴포넌트 생성
board = Board(height=20, width=10)
queue = TetrominoQueue(BagRandomizer())
game = Game(board, queue)

# 게임 시작
game.reset()

# 피스 조작
game.move_piece(1, 0)   # 오른쪽으로
game.rotate_piece()      # 회전
rows_dropped = game.hard_drop()  # 하드 드롭

# 피스 고정 및 줄 클리어
lines_cleared, is_game_over = game.lock_piece()

print(f"Lines cleared: {lines_cleared}")
print(f"Game over: {is_game_over}")
print(f"Score: {game.score}")
```

## More Examples

전체 예제 코드는 [GitHub 저장소의 examples 폴더](https://github.com/hot666666/RL-Tetris/tree/main/examples)에서 확인할 수 있습니다:

- `random_env.py` - 기본 랜덤 에이전트
- `random_grouped_env.py` - Grouped Wrapper 사용 예제
- `train_grouped_model.py` - DQN 학습 전체 예제

## Next Steps

- [API Reference](../api/core/board.md) - 자세한 API 문서
- [Architecture](../architecture/overview.md) - 컴포넌트 이해하기
