# Observation Wrappers

Observation Wrapper들은 환경의 관찰 데이터를 변환합니다.

## GroupedFeaturesObservation

보드 상태를 특징 벡터로 변환하는 Wrapper입니다.

### API Reference

::: rl_tetris.wrapper.Observation.GroupedFeaturesObservation
    options:
      show_source: false

### Usage Example

```python
import gymnasium as gym
from rl_tetris.wrapper.Grouped import GroupedWrapper
from rl_tetris.wrapper.Observation import GroupedFeaturesObservation

env = gym.make("RL-Tetris-v0")
env = GroupedWrapper(env, observation_wrapper=GroupedFeaturesObservation(env))

obs, info = env.reset()

# obs 구조
print(obs.keys())  # dict_keys(['features', 'action_mask'])
print(obs['features'].shape)  # (N, 4) - N개 액션, 4개 특징
print(obs['action_mask'].shape)  # (N,) - N개 액션의 유효성
```

### Observation Structure

```python
{
    "features": np.ndarray,  # (N, 4) - 각 액션에 대한 특징
    "action_mask": np.ndarray  # (N,) - 유효한 액션 마스크
}
```

### Features

각 액션(피스 배치)에 대해 4개의 특징을 제공:

1. **lines_cleared**: 해당 배치로 클리어되는 줄 수
2. **holes**: 배치 후 보드의 구멍 수
3. **bumpiness**: 배치 후 높이 편차
4. **total_height**: 배치 후 총 높이

## BoardObservation

보드 상태를 numpy 배열로 반환하는 기본 Wrapper입니다.

### API Reference

::: rl_tetris.wrapper.Observation.BoardObservation
    options:
      show_source: false

### Usage Example

```python
from rl_tetris.wrapper.Grouped import GroupedWrapper
from rl_tetris.wrapper.Observation import BoardObservation

env = gym.make("RL-Tetris-v0")
env = GroupedWrapper(env, observation_wrapper=BoardObservation(env))

obs, info = env.reset()

# obs 구조
print(obs.keys())  # dict_keys(['board', 'action_mask'])
print(obs['board'].shape)  # (N, 20, 10) - N개 액션에 대한 보드 상태
print(obs['action_mask'].shape)  # (N,)
```

## Custom Observation Wrapper

자신만의 Observation Wrapper를 만들 수 있습니다:

```python
from rl_tetris.wrapper.Observation import BaseObservationWrapper
import numpy as np

class CustomObservation(BaseObservationWrapper):
    def get_observation(self, env):
        """
        Custom observation 생성
        """
        states = []

        for x, rotation in env.unwrapped.valid_placements:
            # 보드 시뮬레이션
            board_copy = env.unwrapped.board.copy()
            piece_copy = env.unwrapped.game.current_piece.copy()

            # 피스 회전 및 배치
            for _ in range(rotation):
                piece_copy.rotate_clockwise()

            # 하드 드롭
            y = 0
            while not board_copy.check_collision(piece_copy, x, y+1):
                y += 1

            board_copy.place_piece(piece_copy, x, y)

            # 커스텀 특징 추출
            custom_features = self.extract_custom_features(board_copy)
            states.append(custom_features)

        return {
            "custom_features": np.array(states),
            "action_mask": env.unwrapped.action_mask
        }

    def extract_custom_features(self, board):
        # 여기에 커스텀 특징 로직 구현
        return np.array([...])
```

## Feature Comparison

| Wrapper | Output Shape | Features | Use Case |
|---------|--------------|----------|----------|
| BoardObservation | (N, 20, 10) | Raw board states | CNN 기반 학습 |
| GroupedFeaturesObservation | (N, 4) | Engineered features | 작은 모델, 빠른 학습 |
| Custom | Variable | Your choice | 특수한 요구사항 |

## See Also

- [GroupedWrapper](grouped.md) - 액션 그룹화
- [Feature Extractors](../features/extractors.md) - 특징 추출
