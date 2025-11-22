# Board

Board 클래스는 테트리스 게임 보드의 상태를 관리하고, 충돌 감지, 줄 클리어, 특징 계산 등의 기능을 제공합니다.

## API Reference

::: rl_tetris.core.board.Board
    options:
      show_source: true
      members:
        - __init__
        - reset
        - get_state
        - set_state
        - check_collision
        - place_piece
        - clear_full_rows
        - get_holes
        - get_bumpiness_and_height
        - get_column_heights

## Usage Examples

### 기본 사용법

```python
from rl_tetris.core import Board, Piece

# 보드 생성 (20x10)
board = Board(height=20, width=10)
board.reset()

# 피스 생성
piece = Piece(piece_type=0)  # I 피스

# 충돌 검사
can_place = not board.check_collision(piece, x=5, y=18)
if can_place:
    board.place_piece(piece, x=5, y=18)

# 줄 클리어
lines_cleared = board.clear_full_rows()
print(f"Cleared {lines_cleared} lines")
```

### 특징 추출

```python
# 보드 특징 계산
holes = board.get_holes()
bumpiness, height = board.get_bumpiness_and_height()
heights = board.get_column_heights()

print(f"Holes: {holes}")
print(f"Bumpiness: {bumpiness}")
print(f"Total Height: {height}")
print(f"Column Heights: {heights}")
```

### 상태 관리

```python
# 상태 저장/복원
saved_state = board.get_state()
# ... 게임 진행 ...
board.set_state(saved_state)  # 이전 상태로 복원
```

## See Also

- [Piece](piece.md) - 피스 관리
- [Game](game.md) - 게임 로직
- [BoardFeatureExtractor](../features/extractors.md) - 특징 추출
