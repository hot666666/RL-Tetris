# Randomizer

Randomizer 클래스들은 테트리스 피스의 생성 순서를 결정합니다.

## BagRandomizer

"7-bag" 알고리즘을 사용하는 표준 테트리스 랜덤화입니다.

7개의 모든 피스를 섞은 가방에서 하나씩 꺼내며, 가방이 비면 다시 채웁니다.

### API Reference

::: rl_tetris.randomizer.BagRandomizer
    options:
      show_source: true

### Usage Example

```python
from rl_tetris.randomizer import BagRandomizer

randomizer = BagRandomizer()

# 14개의 피스 생성 (2개의 완전한 가방)
pieces = [randomizer.get_random() for _ in range(14)]
print(pieces)
# 예: [2, 0, 5, 1, 6, 3, 4, 1, 3, 5, 0, 2, 6, 4]
# 첫 7개와 다음 7개는 각각 0-6을 모두 포함
```

### Characteristics

- **공정성**: 모든 피스가 고르게 나옴
- **예측 가능성**: 최대 7개 후에는 특정 피스가 반드시 나옴
- **표준**: 공식 테트리스에서 사용하는 방식

## RandRandomizer

완전 랜덤 방식으로 피스를 생성합니다.

### API Reference

::: rl_tetris.randomizer.RandRandomizer
    options:
      show_source: true

### Usage Example

```python
from rl_tetris.randomizer import RandRandomizer

randomizer = RandRandomizer()

# 완전 랜덤 피스 생성
pieces = [randomizer.get_random() for _ in range(14)]
print(pieces)
# 예: [0, 0, 3, 5, 0, 2, 1, 6, 0, 0, 4, 3, 2, 0]
# 어떤 피스든 나올 수 있음
```

### Characteristics

- **완전 랜덤**: 각 피스가 1/7 확률
- **불공정**: 같은 피스가 연속으로 나올 수 있음
- **고전**: 초기 테트리스에서 사용하던 방식

## Custom Randomizer

자신만의 랜덤화 알고리즘을 만들 수 있습니다:

```python
from rl_tetris.randomizer import Randomizer
import random

class WeightedRandomizer(Randomizer):
    """
    가중치가 적용된 랜덤 피스 생성
    """
    def __init__(self, weights=None):
        super().__init__()
        # 각 피스에 대한 가중치 (기본: 균등)
        self.weights = weights or [1.0] * 7

    def get_random(self) -> int:
        """
        가중치에 따라 피스 선택
        """
        return random.choices(range(7), weights=self.weights)[0]

    def reset(self):
        """
        필요시 상태 리셋
        """
        pass

# 사용 예시
# I 피스(0)를 다른 피스보다 2배 자주 나오게
weights = [2.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]
randomizer = WeightedRandomizer(weights)
```

## Comparison

| Randomizer | Distribution | Use Case |
|------------|--------------|----------|
| BagRandomizer | Uniform (공정) | 표준 게임, 학습 |
| RandRandomizer | Random (불공정) | 고전 방식, 변화 |
| Custom | Customizable | 특수 연구, 실험 |

## Usage in Environment

```python
from rl_tetris.envs.tetris import Tetris
from rl_tetris.randomizer import BagRandomizer, RandRandomizer

# Bag randomizer 사용 (기본)
env = Tetris()  # 기본적으로 BagRandomizer

# Rand randomizer 사용
from rl_tetris.tetromino_queue import TetrominoQueue
env = Tetris()
env.queue = TetrominoQueue(RandRandomizer())
```

## See Also

- [TetrominoQueue](queue.md) - 피스 큐 관리
- [Game](../core/game.md) - 게임 로직
