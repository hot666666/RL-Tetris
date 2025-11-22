# Contributing

RL-Tetris 프로젝트에 기여해주셔서 감사합니다! 이 가이드는 프로젝트에 기여하는 방법을 설명합니다.

## Getting Started

### 1. Fork and Clone

```bash
# 저장소 Fork (GitHub에서)
# 그 다음 클론
git clone https://github.com/YOUR_USERNAME/RL-Tetris.git
cd RL-Tetris
```

### 2. Install Dependencies

```bash
# Poetry 설치
curl -sSL https://install.python-poetry.org | python3 -

# 의존성 설치 (개발 의존성 포함)
poetry install --with dev --with docs

# 가상환경 활성화
poetry shell
```

### 3. Create a Branch

```bash
git checkout -b feature/your-feature-name
# 또는
git checkout -b fix/your-bug-fix
```

## Development Workflow

### Running Tests

테스트는 **필수**입니다. 모든 기여는 테스트를 통과해야 합니다.

```bash
# 모든 테스트 실행
pytest tests/ -v

# 특정 파일 테스트
pytest tests/test_board.py -v

# 커버리지 포함
pytest tests/ --cov=rl_tetris --cov-report=html
```

### Writing Tests

새로운 기능을 추가할 때는 반드시 테스트를 작성하세요:

```python
# tests/test_your_feature.py
import pytest
from rl_tetris.your_module import YourClass

def test_your_feature():
    """Test description"""
    obj = YourClass()
    result = obj.your_method()
    assert result == expected_value

def test_edge_case():
    """Test edge case"""
    # ...
```

### Code Style

- **Google Style Docstrings** 사용
- **Type Hints** 추가
- **명확한 변수명** 사용

예시:

```python
def calculate_reward(self, lines_cleared: int, overflow: bool) -> int:
    """
    Calculate the reward for the current action.

    Args:
        lines_cleared: Number of lines cleared.
        overflow: Whether the game is over due to overflow.

    Returns:
        The calculated reward value.

    Examples:
        >>> game.calculate_reward(lines_cleared=2, overflow=False)
        4
    """
    if overflow:
        return -10
    return lines_cleared ** 2
```

### Documentation

코드에 docstring을 추가하세요:

```python
class YourClass:
    """
    Brief description of the class.

    This class does X, Y, and Z. It is used for...

    Attributes:
        attr1: Description of attr1.
        attr2: Description of attr2.

    Examples:
        >>> obj = YourClass(param=value)
        >>> obj.method()
        result
    """

    def __init__(self, param: int):
        """
        Initialize the class.

        Args:
            param: Description of parameter.
        """
        self.attr1 = param
```

### Building Documentation

로컬에서 문서를 빌드하고 확인할 수 있습니다:

```bash
# 문서 빌드
mkdocs build

# 로컬 서버에서 문서 미리보기
mkdocs serve
# http://127.0.0.1:8000 에서 확인
```

## Contribution Guidelines

### What to Contribute

환영하는 기여:

- **버그 수정**: 이슈 생성 후 PR
- **새로운 기능**: 먼저 이슈에서 논의
- **테스트 추가**: 커버리지 개선
- **문서 개선**: 오타 수정, 예제 추가
- **성능 개선**: 벤치마크 포함

### Pull Request Process

1. **이슈 생성**: 큰 변경사항은 먼저 이슈에서 논의
2. **테스트 작성**: 모든 새 코드에 테스트 추가
3. **테스트 통과**: 로컬에서 모든 테스트 확인
4. **문서 업데이트**: README, docstring 업데이트
5. **커밋 메시지**: 명확하고 설명적인 메시지
6. **PR 생성**: 변경사항 설명 포함

### Commit Message Format

```
<type>: <subject>

<body>

<footer>
```

Types:
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `test`: 테스트 추가/수정
- `refactor`: 코드 리팩토링
- `perf`: 성능 개선
- `ci`: CI 설정 변경

예시:
```
feat: Add advanced feature extractor

- Added AdvancedFeatureExtractor class
- Includes weighted holes, wells, transitions
- Added comprehensive tests

Closes #123
```

## Testing Guidelines

### Test Structure

```
tests/
├── test_board.py       # Board 클래스 테스트
├── test_piece.py       # Piece 클래스 테스트
├── test_game.py        # Game 클래스 테스트
├── test_integration.py # 통합 테스트
└── conftest.py         # Pytest fixtures
```

### Test Coverage

- **최소 커버리지**: 80% 이상
- **모든 공개 메서드**: 테스트 필수
- **엣지 케이스**: 경계 조건 테스트
- **에러 처리**: 예외 상황 테스트

### Example Test

```python
import pytest
from rl_tetris.core import Board, Piece

@pytest.fixture
def board():
    """Fixture for creating a fresh board"""
    return Board(height=20, width=10)

def test_place_piece_basic(board):
    """Test basic piece placement"""
    piece = Piece(piece_type=0)
    board.place_piece(piece, x=5, y=18)

    state = board.get_state()
    assert state[18][5] != 0

def test_collision_detection(board):
    """Test collision detection at boundaries"""
    piece = Piece(piece_type=0)

    # Bottom boundary
    assert board.check_collision(piece, x=5, y=20)

    # Left boundary
    assert board.check_collision(piece, x=-1, y=10)

    # Right boundary
    assert board.check_collision(piece, x=10, y=10)
```

## Code Review

모든 PR은 코드 리뷰를 거칩니다:

- **명확성**: 코드가 읽기 쉬운가?
- **테스트**: 충분한 테스트가 있는가?
- **문서**: docstring이 있는가?
- **성능**: 불필요한 연산이 없는가?
- **호환성**: 기존 API를 깨뜨리지 않는가?

## Questions?

- **Issues**: [GitHub Issues](https://github.com/hot666666/RL-Tetris/issues)
- **Discussions**: [GitHub Discussions](https://github.com/hot666666/RL-Tetris/discussions)

감사합니다!
