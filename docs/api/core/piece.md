# Piece

Piece 클래스는 테트리스 피스(테트로미노)의 형태, 회전, 위치를 관리합니다.

## API Reference

::: rl_tetris.core.piece.Piece
    options:
      show_source: true
      members:
        - __init__
        - rotate_clockwise
        - rotate_counterclockwise
        - move
        - set_position
        - get_all_rotations
        - copy

## Piece Types

| Type | Name | Shape | Rotations |
|------|------|-------|-----------|
| 0 | I | `████` | 2 |
| 1 | O | `██`<br>`██` | 1 |
| 2 | T | `███`<br>` █` | 4 |
| 3 | S | ` ██`<br>`██` | 2 |
| 4 | Z | `██`<br>` ██` | 2 |
| 5 | J | `█`<br>`███` | 4 |
| 6 | L | `  █`<br>`███` | 4 |

## Usage Examples

### 피스 생성 및 회전

```python
from rl_tetris.core import Piece

# T 피스 생성
piece = Piece(piece_type=2)
print(f"Initial position: ({piece.x}, {piece.y})")

# 회전
piece.rotate_clockwise()

# 모든 회전 상태 확인
rotations = piece.get_all_rotations()
print(f"Total rotations: {len(rotations)}")
```

### 피스 이동

```python
# 상대 이동
piece.move(dx=1, dy=0)  # 오른쪽으로
piece.move(dx=0, dy=1)  # 아래로

# 절대 위치 설정
piece.set_position(x=5, y=10)
```

### 피스 복사

```python
# 시뮬레이션을 위한 복사
original = Piece(piece_type=0)
copy = original.copy()

copy.rotate_clockwise()
copy.move(1, 0)

# 원본은 변경되지 않음
assert original.x != copy.x
```

## See Also

- [Board](board.md) - 보드 관리
- [Game](game.md) - 게임 로직
