# GroupedWrapper

GroupedWrapper는 가능한 모든 피스 배치를 그룹화하여 액션 공간을 단순화합니다.

## Overview

기본 Tetris 환경은 6개의 원자적 액션(left, right, down, rotate, etc.)을 제공하지만, GroupedWrapper는 현재 피스로 가능한 모든 최종 배치 위치를 액션으로 제공합니다.

예를 들어, I 피스가 스폰되면:
- 수평 배치: 10개 위치 (x=0~9)
- 수직 배치: 7개 위치 (x=0~6)
- 총 17개의 그룹화된 액션

## API Reference

::: rl_tetris.wrapper.Grouped.GroupedWrapper
    options:
      show_source: false

## Usage Examples

### 기본 사용법

```python
import gymnasium as gym
from rl_tetris.wrapper.Grouped import GroupedWrapper
from rl_tetris.wrapper.Observation import GroupedFeaturesObservation

env = gym.make("RL-Tetris-v0")
env = GroupedWrapper(env, observation_wrapper=GroupedFeaturesObservation(env))

obs, info = env.reset()

done = False
while not done:
    # action_mask를 사용하여 유효한 액션 선택
    valid_actions = np.where(obs["action_mask"] == 1)[0]
    action = np.random.choice(valid_actions)

    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
```

### Action Mask 사용

```python
# 유효한 액션만 선택
action = env.action_space.sample(obs["action_mask"])

# 또는 직접 필터링
q_values = model(obs["features"])
q_values[obs["action_mask"] == 0] = float('-inf')
action = q_values.argmax()
```

## Grouped Actions

각 액션은 `(x, rotation)` 조합을 나타냅니다:

```python
# Action 0: x=0, rotation=0
# Action 1: x=1, rotation=0
# Action 2: x=2, rotation=0
# ...
# Action 10: x=0, rotation=1
# Action 11: x=1, rotation=1
# ...
```

## Visualization

![GroupedWrapper](https://raw.githubusercontent.com/hot666666/RL-Tetris/main/GroupedWrapper.png)

위 이미지는 현재 피스가 상단에서 배치 가능한 위치들을 보여줍니다.
`(x, r)` 표시는 각각 위치와 회전 상태를 나타냅니다.

## Benefits

### 장점
- **액션 공간 단순화**: 여러 단계의 액션을 하나로 통합
- **학습 효율성**: 더 적은 스텝으로 게임 완료
- **명확한 목표**: 각 액션이 명확한 결과를 가짐

### 단점
- **유연성 감소**: 중간 단계 제어 불가
- **동적 액션 공간**: 피스마다 가능한 액션 수가 다름

## See Also

- [ObservationWrapper](observation.md) - 관찰 변환
- [Tetris Environment](../env/tetris.md) - 기본 환경
