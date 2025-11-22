# TetrominoQueue

TetrominoQueue는 피스 생성 순서를 관리하고, Randomizer를 사용하여 다음 피스를 결정합니다.

## API Reference

::: rl_tetris.tetromino_queue.TetrominoQueue
    options:
      show_source: true

## Usage Examples

### 기본 사용법

```python
from rl_tetris.tetromino_queue import TetrominoQueue
from rl_tetris.randomizer import BagRandomizer

# 큐 생성
queue = TetrominoQueue(BagRandomizer())

# 다음 피스 확인 (제거하지 않음)
next_piece = queue.peek()
print(f"Next piece: {next_piece}")

# 피스 가져오기 (제거)
current_piece = queue.pop()
print(f"Current piece: {current_piece}")

# 리셋
queue.reset()
```

### Randomizer 변경

```python
from rl_tetris.randomizer import RandRandomizer

# 다른 randomizer 사용
queue = TetrominoQueue(RandRandomizer())

# 런타임에 변경
queue.randomizer = BagRandomizer()
queue.reset()
```

### Game에서 사용

```python
from rl_tetris.core import Board, Game
from rl_tetris.tetromino_queue import TetrominoQueue
from rl_tetris.randomizer import BagRandomizer

board = Board(height=20, width=10)
queue = TetrominoQueue(BagRandomizer())
game = Game(board, queue)

# 게임에서 자동으로 큐 사용
game.reset()  # 첫 피스 스폰
print(f"Current piece: {game.current_piece.piece_type}")

# 다음 피스 미리보기
print(f"Next piece: {queue.peek()}")
```

## Implementation Details

큐는 2개의 피스를 미리 생성하여 보관합니다:

```python
class TetrominoQueue:
    def __init__(self, randomizer: Randomizer):
        self.randomizer = randomizer
        self._queue = [
            randomizer.get_random(),
            randomizer.get_random()
        ]

    def pop(self) -> int:
        # 첫 번째 피스를 반환하고, 새로운 피스를 추가
        piece = self._queue.pop(0)
        self._queue.append(self.randomizer.get_random())
        return piece

    def peek(self) -> int:
        # 첫 번째 피스를 확인만 함
        return self._queue[0]
```

## See Also

- [Randomizer](randomizer.md) - 피스 생성 알고리즘
- [Game](../core/game.md) - 게임 로직
