# Quick Start

이 가이드에서는 RL-Tetris 환경을 사용하는 방법을 빠르게 배웁니다.

## Basic Environment

가장 기본적인 사용법:

```python
import gymnasium as gym

# 환경 생성
env = gym.make("RL-Tetris-v0")

# 환경 초기화
obs, info = env.reset()

# 게임 루프
done = False
total_reward = 0

while not done:
    # 랜덤 액션 선택
    action = env.action_space.sample()

    # 액션 실행
    obs, reward, terminated, truncated, info = env.step(action)
    total_reward += reward

    done = terminated or truncated

print(f"Game Over! Total reward: {total_reward}")
```

## Render Mode

게임 화면을 보려면 `render_mode`를 설정하세요:

```python
import time
import gymnasium as gym

env = gym.make("RL-Tetris-v0", render_mode="human")
obs, info = env.reset()

done = False
while not done:
    env.render()  # 화면 렌더링
    action = env.action_space.sample()
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
    time.sleep(0.1)  # 게임 속도 조절
```

### Render Modes

- **`None`**: 렌더링 없음 (학습 시 빠른 속도)
- **`"human"`**: 게임 화면 표시
- **`"animate"`**: Hard Drop 애니메이션 포함

## Using GroupedWrapper

GroupedWrapper는 가능한 모든 피스 배치를 그룹화하여 제공합니다:

```python
import gymnasium as gym
from rl_tetris.wrapper.Grouped import GroupedWrapper
from rl_tetris.wrapper.Observation import GroupedFeaturesObservation

# 환경 생성 및 래퍼 적용
env = gym.make("RL-Tetris-v0", render_mode="human")
env = GroupedWrapper(env, observation_wrapper=GroupedFeaturesObservation(env))

obs, info = env.reset()

done = False
while not done:
    env.render()

    # action_mask를 사용한 유효한 액션 선택
    action = env.action_space.sample(obs["action_mask"])

    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
```

### Observation Structure

GroupedFeaturesObservation을 사용하면 다음과 같은 observation을 받습니다:

```python
{
    "action_mask": array([1, 1, 0, 1, ...]),  # 유효한 액션
    "features": array([
        [lines_cleared, holes, bumpiness, height],  # 액션 0의 특징
        [lines_cleared, holes, bumpiness, height],  # 액션 1의 특징
        ...
    ])
}
```

## Actions

RL-Tetris는 6가지 액션을 제공합니다:

```python
from rl_tetris.mapping.actions import GameActions

# 액션 타입:
# - GameActions.move_left (0)
# - GameActions.move_right (1)
# - GameActions.move_down (2)
# - GameActions.rotate_clockwise (3)
# - GameActions.rotate_counterclockwise (4)
# - GameActions.hard_drop (5)

env = gym.make("RL-Tetris-v0")
obs, info = env.reset()

# 특정 액션 실행
obs, reward, terminated, truncated, info = env.step(GameActions.hard_drop)
```

## Next Steps

- [Examples](examples.md) - 전체 학습 예제 보기
- [API Reference](../api/env/tetris.md) - 자세한 API 문서
- [Architecture](../architecture/overview.md) - 내부 구조 이해하기
