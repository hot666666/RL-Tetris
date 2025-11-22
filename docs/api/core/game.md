# Game

Game 클래스는 테트리스 게임의 전체 흐름을 제어하고, 스코어링, 피스 스폰, 게임 오버 처리를 담당합니다.

## API Reference

::: rl_tetris.core.game.Game
    options:
      show_source: true
      members:
        - __init__
        - reset
        - spawn_piece
        - move_piece
        - rotate_piece
        - hard_drop
        - lock_piece
        - calculate_reward

## Usage Examples

### 게임 시작

```python
from rl_tetris.core import Board, Game
from rl_tetris.tetromino_queue import TetrominoQueue
from rl_tetris.randomizer import BagRandomizer

# 컴포넌트 생성
board = Board(height=20, width=10)
queue = TetrominoQueue(BagRandomizer())
game = Game(board, queue)

# 게임 시작
game.reset()
print(f"Current piece type: {game.current_piece.piece_type}")
```

### 피스 조작

```python
# 피스 이동
if game.move_piece(dx=1, dy=0):
    print("Moved right")

if game.move_piece(dx=0, dy=1):
    print("Moved down")

# 피스 회전
if game.rotate_piece():
    print("Rotated")

# 하드 드롭
rows_dropped = game.hard_drop()
print(f"Dropped {rows_dropped} rows")
```

### 게임 루프

```python
game.reset()

while not game.gameover:
    # 피스 조작
    game.move_piece(1, 0)
    game.rotate_piece()

    # 하드 드롭 및 고정
    game.hard_drop()
    lines_cleared, is_game_over = game.lock_piece()

    # 보상 계산
    reward = game.calculate_reward(lines_cleared, is_game_over)

    print(f"Lines: {lines_cleared}")
    print(f"Score: {game.score}")
    print(f"Reward: {reward}")

    if is_game_over:
        print("Game Over!")
        break
```

### 스코어링

```python
# 줄 클리어에 따른 점수
# 1줄: 100점
# 2줄: 300점
# 3줄: 500점
# 4줄 (Tetris): 800점

lines_cleared, _ = game.lock_piece()
print(f"Score: {game.score}")
print(f"Total lines: {game.cleared_lines}")
```

## Scoring System

| Lines Cleared | Points |
|---------------|--------|
| 1 | 100 |
| 2 | 300 |
| 3 | 500 |
| 4 (Tetris) | 800 |

## Reward System

강화학습을 위한 보상:

- **줄 클리어**: `lines_cleared²` (1줄=1, 2줄=4, 3줄=9, 4줄=16)
- **게임 오버**: -10
- **일반 이동**: 0

## See Also

- [Board](board.md) - 보드 관리
- [Piece](piece.md) - 피스 관리
- [Tetris Environment](../env/tetris.md) - Gymnasium 환경
