# RL-Tetris 아키텍처 문서

리팩토링된 RL-Tetris 프로젝트의 아키텍처 구조를 설명합니다.

## 목차
- [전체 아키텍처 구조](#전체-아키텍처-구조)
- [클래스 다이어그램](#클래스-다이어그램)
- [컴포넌트 책임 분리](#컴포넌트-책임-분리)
- [데이터 흐름](#데이터-흐름)
- [테스트 구조](#테스트-구조)
- [디렉토리 구조](#디렉토리-구조)
- [주요 개선 사항](#주요-개선-사항)

---

## 전체 아키텍처 구조

```mermaid
graph TB
    subgraph "External"
        User[User/Agent]
        Gym[Gymnasium API]
    end

    subgraph "Environment Layer"
        Tetris[Tetris Environment<br/>rl_tetris/envs/tetris.py]
        Wrapper1[GroupedWrapper]
        Wrapper2[ObservationWrapper]
    end

    subgraph "Core Components<br/>rl_tetris/core/"
        Game[Game<br/>게임 오케스트레이션]
        Board[Board<br/>보드 상태 관리]
        Piece[Piece<br/>피스 형태/회전]
    end

    subgraph "Features<br/>rl_tetris/features/"
        Feature[BoardFeatureExtractor<br/>특징 추출]
        Advanced[AdvancedFeatureExtractor<br/>고급 특징]
    end

    subgraph "Supporting Components"
        Renderer[Renderer<br/>시각화]
        Queue[TetrominoQueue<br/>피스 큐]
        Randomizer[Randomizer<br/>BagRandomizer/RandRandomizer]
        GameState[GameStates<br/>렌더링 상태]
        Actions[GameActions<br/>액션 정의]
    end

    User --> Gym
    Gym --> Wrapper1 & Wrapper2
    Wrapper1 & Wrapper2 --> Tetris

    Tetris --> Game
    Tetris --> Board
    Tetris --> Renderer

    Game --> Board
    Game --> Piece
    Game --> Queue

    Queue --> Randomizer

    Feature --> Board
    Advanced --> Feature

    Renderer --> GameState
    Tetris --> Actions

    style Tetris fill:#4CAF50
    style Game fill:#2196F3
    style Board fill:#2196F3
    style Piece fill:#2196F3
    style Feature fill:#FF9800
    style Advanced fill:#FF9800
```

### 레이어 설명

1. **External Layer**: 사용자/에이전트와 Gymnasium API
2. **Environment Layer**: Tetris 환경과 Wrapper들
3. **Core Components**: 핵심 게임 로직 (Board, Piece, Game)
4. **Features**: 머신러닝을 위한 특징 추출
5. **Supporting Components**: 렌더링, 랜덤화 등 지원 컴포넌트

---

## 클래스 다이어그램

```mermaid
classDiagram
    class Tetris {
        +Board board
        +Game game
        +TetrominoQueue queue
        +Renderer renderer
        +reset() observation, info
        +step(action) observation, reward, terminated, truncated, info
        +render()
        -_sync_state_for_wrappers()
    }

    class Board {
        -List~List~int~~ _state
        +int height
        +int width
        +reset()
        +get_state() List
        +set_state(state)
        +check_collision(piece, x, y) bool
        +place_piece(piece, x, y)
        +clear_full_rows() int
        +get_holes() int
        +get_bumpiness_and_height() tuple
        +get_column_heights() List
    }

    class Piece {
        +int piece_type
        +List~List~int~~ shape
        +int x
        +int y
        +rotate_clockwise()
        +move(dx, dy)
        +set_position(x, y)
        +get_all_rotations() List
        +copy() Piece
    }

    class Game {
        +Board board
        +TetrominoQueue queue
        +Piece current_piece
        +int score
        +int cleared_lines
        +bool gameover
        +reset()
        +spawn_piece() bool
        +move_piece(dx, dy) bool
        +rotate_piece() bool
        +hard_drop() int
        +lock_piece() lines_cleared, is_game_over
        +calculate_reward(lines, overflow) int
    }

    class BoardFeatureExtractor {
        +extract_features(board, lines)$ ndarray
        +get_feature_names()$ List
        +get_feature_dim()$ int
        +normalize_features(features)$ ndarray
    }

    class TetrominoQueue {
        +Randomizer randomizer
        +pop() int
        +peek() int
        +reset()
    }

    class Randomizer {
        <<abstract>>
        +get_random()* int
        +reset()*
    }

    class BagRandomizer {
        -List bag
        +get_random() int
        +reset()
    }

    class RandRandomizer {
        +get_random() int
        +reset()
    }

    Tetris --> Board
    Tetris --> Game
    Tetris --> TetrominoQueue
    Game --> Board
    Game --> Piece
    Game --> TetrominoQueue
    TetrominoQueue --> Randomizer
    Randomizer <|-- BagRandomizer
    Randomizer <|-- RandRandomizer
    BoardFeatureExtractor ..> Board
```

### 주요 클래스 설명

#### Tetris (Environment)
- Gymnasium 인터페이스 구현
- 모든 컴포넌트를 조율
- 하위 호환성 유지

#### Board
- 보드 상태 관리
- 충돌 감지
- 줄 클리어
- 특징 계산 (holes, bumpiness, height)

#### Piece
- 7가지 테트리스 피스 형태 관리
- 회전 로직 (시계방향/반시계방향)
- 위치 관리

#### Game
- 게임 흐름 제어
- 피스 스폰 및 잠금
- 스코어링 및 보상 계산
- 게임 오버 처리

---

## 컴포넌트 책임 분리

```mermaid
graph LR
    subgraph "Board 책임"
        B1[상태 관리]
        B2[충돌 감지]
        B3[줄 클리어]
        B4[특징 계산<br/>holes, bumpiness, height]
    end

    subgraph "Piece 책임"
        P1[피스 형태 관리]
        P2[회전 로직]
        P3[위치 관리]
        P4[피스 복사]
    end

    subgraph "Game 책임"
        G1[게임 흐름 제어]
        G2[피스 스폰]
        G3[스코어링]
        G4[게임 오버 처리]
    end

    subgraph "Tetris 책임"
        T1[Gymnasium 인터페이스]
        T2[컴포넌트 조율]
        T3[하위 호환성]
        T4[렌더링 조율]
    end

    style B1 fill:#E3F2FD
    style B2 fill:#E3F2FD
    style B3 fill:#E3F2FD
    style B4 fill:#E3F2FD
    style P1 fill:#F3E5F5
    style P2 fill:#F3E5F5
    style P3 fill:#F3E5F5
    style P4 fill:#F3E5F5
    style G1 fill:#E8F5E9
    style G2 fill:#E8F5E9
    style G3 fill:#E8F5E9
    style G4 fill:#E8F5E9
    style T1 fill:#FFF3E0
    style T2 fill:#FFF3E0
    style T3 fill:#FFF3E0
    style T4 fill:#FFF3E0
```

### SOLID 원칙 준수

각 컴포넌트는 **단일 책임 원칙(SRP)**을 따르며:
- **Board**: 보드 상태와 관련된 모든 작업
- **Piece**: 피스와 관련된 모든 작업
- **Game**: 게임 로직과 관련된 모든 작업
- **Tetris**: Gymnasium 인터페이스와 컴포넌트 조율

---

## 데이터 흐름

```mermaid
sequenceDiagram
    participant Agent
    participant Tetris
    participant Game
    participant Board
    participant Piece
    participant Queue

    Agent->>Tetris: reset()
    Tetris->>Game: reset()
    Game->>Board: reset()
    Game->>Queue: reset()
    Game->>Queue: pop()
    Queue-->>Game: piece_type
    Game->>Piece: new Piece(type)
    Game-->>Tetris: current_piece
    Tetris-->>Agent: observation, info

    Agent->>Tetris: step(action)
    Tetris->>Game: move_piece() / rotate_piece()
    Game->>Board: check_collision()
    Board-->>Game: is_valid
    alt collision detected
        Game->>Piece: update position
    end

    alt piece locked
        Game->>Board: place_piece()
        Game->>Board: clear_full_rows()
        Board-->>Game: lines_cleared
        Game->>Game: calculate_reward()
        Game->>Queue: pop()
        Game->>Piece: spawn new piece
    end

    Game-->>Tetris: reward, done
    Tetris-->>Agent: obs, reward, terminated, truncated, info
```

### 데이터 흐름 설명

1. **Reset 단계**: 환경 초기화, 보드/큐 리셋, 첫 피스 스폰
2. **Step 단계**: 액션 실행, 충돌 감지, 피스 이동
3. **Lock 단계**: 피스 고정, 줄 클리어, 보상 계산, 새 피스 스폰

---

## 테스트 구조

```mermaid
graph TB
    subgraph "Unit Tests"
        TB[test_board.py<br/>28 tests]
        TP[test_piece.py<br/>30 tests]
        TG[test_game.py<br/>16 tests]
        TR[test_randomizer.py<br/>9 tests]
    end

    subgraph "Integration Tests"
        TI[test_integration.py<br/>16 tests]
    end

    subgraph "Tested Components"
        Board
        Piece
        Game
        Randomizer
        Tetris
        Features
    end

    TB --> Board
    TP --> Piece
    TG --> Game
    TR --> Randomizer
    TI --> Tetris
    TI --> Features
    TI --> Board & Piece & Game

    style TB fill:#4CAF50
    style TP fill:#4CAF50
    style TG fill:#4CAF50
    style TR fill:#4CAF50
    style TI fill:#2196F3
```

### 테스트 커버리지

- **총 99개 테스트**
- **유닛 테스트**: 83개 (각 컴포넌트 독립 테스트)
- **통합 테스트**: 16개 (컴포넌트 간 상호작용 테스트)

#### 테스트 파일별 내용

| 파일 | 테스트 수 | 커버리지 |
|------|----------|---------|
| test_board.py | 28 | Board 클래스 전체 기능 |
| test_piece.py | 30 | Piece 클래스 전체 기능 |
| test_game.py | 16 | Game 클래스 핵심 로직 |
| test_randomizer.py | 9 | BagRandomizer, RandRandomizer |
| test_integration.py | 16 | 환경 통합, 하위 호환성, 특징 추출 |

---

## 디렉토리 구조

```mermaid
graph TB
    Root[RL-Tetris/]

    Root --> RL[rl_tetris/]
    Root --> Tests[tests/]
    Root --> Examples[examples/]

    RL --> Core[core/]
    RL --> Features[features/]
    RL --> Envs[envs/]
    RL --> Wrapper[wrapper/]
    RL --> Mapping[mapping/]
    RL --> Other[renderer.py<br/>randomizer.py<br/>tetromino_queue.py<br/>game_state.py]

    Core --> CB[board.py<br/>piece.py<br/>game.py<br/>__init__.py]
    Features --> FE[extractors.py<br/>__init__.py]
    Envs --> ET[tetris.py<br/>__init__.py]
    Wrapper --> WR[Grouped.py<br/>Observation.py]
    Mapping --> MA[actions.py]

    Tests --> TestFiles[test_board.py<br/>test_piece.py<br/>test_game.py<br/>test_randomizer.py<br/>test_integration.py<br/>test_envs.py]

    Examples --> EX[random_env.py<br/>random_grouped_env.py<br/>train_grouped_model.py]

    style Core fill:#2196F3
    style Features fill:#FF9800
    style Tests fill:#4CAF50
```

### 주요 디렉토리 설명

```
RL-Tetris/
├── rl_tetris/              # 메인 패키지
│   ├── core/              # 핵심 컴포넌트 (새로 추가)
│   │   ├── board.py       # Board 클래스
│   │   ├── piece.py       # Piece 클래스
│   │   ├── game.py        # Game 클래스
│   │   └── __init__.py
│   ├── features/          # 특징 추출 모듈 (새로 추가)
│   │   ├── extractors.py  # 특징 추출 클래스
│   │   └── __init__.py
│   ├── envs/              # Gymnasium 환경
│   │   └── tetris.py      # Tetris 환경 (리팩토링됨)
│   ├── wrapper/           # 환경 래퍼
│   ├── mapping/           # 액션 정의
│   ├── renderer.py        # 렌더링
│   ├── randomizer.py      # 랜덤화
│   ├── tetromino_queue.py # 피스 큐
│   └── game_state.py      # 게임 상태
├── tests/                 # 테스트 스위트 (대폭 확장)
│   ├── test_board.py      # Board 테스트
│   ├── test_piece.py      # Piece 테스트
│   ├── test_game.py       # Game 테스트
│   ├── test_randomizer.py # Randomizer 테스트
│   ├── test_integration.py# 통합 테스트
│   └── test_envs.py       # 기존 테스트
├── examples/              # 사용 예제
│   ├── random_env.py
│   ├── random_grouped_env.py
│   └── train_grouped_model.py
└── test_refactored_env.py # 검증 스크립트
```

---

## 주요 개선 사항

### Before vs After 비교

| 항목 | Before | After |
|------|--------|-------|
| **구조** | 단일 파일 (344줄) | 모듈화된 컴포넌트 |
| **책임 분리** | 혼재됨 | 명확한 단일 책임 |
| **테스트** | 1개 (placeholder) | 99개 (포괄적) |
| **특징 추출** | 환경 내 혼재 | 독립 모듈 |
| **재사용성** | 낮음 | 높음 |
| **유지보수성** | 어려움 | 쉬움 |
| **확장성** | 제한적 | 우수 |
| **코드 중복** | 있음 | 최소화 |

### 리팩토링 통계

```
12 files changed, 2631 insertions(+), 265 deletions(-)
```

#### 새로 추가된 파일
- `rl_tetris/core/board.py` (299 lines)
- `rl_tetris/core/piece.py` (237 lines)
- `rl_tetris/core/game.py` (257 lines)
- `rl_tetris/features/extractors.py` (191 lines)
- `tests/test_board.py` (310 lines)
- `tests/test_piece.py` (270 lines)
- `tests/test_game.py` (150 lines)
- `tests/test_randomizer.py` (119 lines)
- `tests/test_integration.py` (220 lines)

#### 수정된 파일
- `rl_tetris/envs/tetris.py` (344 → 314 lines, -30 lines)

### 아키텍처 원칙

이 리팩토링은 다음 설계 원칙을 따릅니다:

1. **Single Responsibility Principle (SRP)**
   - 각 클래스는 하나의 명확한 책임만 가짐

2. **Open/Closed Principle (OCP)**
   - 확장에는 열려있고 수정에는 닫혀있음
   - 새로운 특징 추출기나 피스 타입 추가 용이

3. **Dependency Injection**
   - Board, Queue 등을 Game에 주입
   - 테스트 시 모킹 용이

4. **Composition over Inheritance**
   - Tetris가 Board, Game, Piece를 조합하여 사용

5. **Separation of Concerns**
   - 게임 로직, 렌더링, 특징 추출이 명확히 분리

### 이점

✅ **모듈화**: 각 컴포넌트를 독립적으로 테스트 및 개발 가능
✅ **테스트 용이성**: Pure function과 DI로 100% 테스트 가능
✅ **유지보수성**: 명확한 구조로 버그 수정과 기능 추가가 쉬움
✅ **확장성**: 새로운 특징, 피스 타입, 게임 모드 추가 용이
✅ **하위 호환성**: 기존 wrapper와 예제 코드 그대로 작동
✅ **재사용성**: 각 컴포넌트를 다른 프로젝트에서도 사용 가능

---

## 사용 예제

### 기본 사용법

```python
from rl_tetris.envs.tetris import Tetris
from rl_tetris.mapping.actions import GameActions

# 환경 생성
env = Tetris()

# 게임 시작
obs, info = env.reset()

# 액션 실행
obs, reward, terminated, truncated, info = env.step(GameActions.move_down)
```

### 컴포넌트 직접 사용

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

# 피스 이동
game.move_piece(1, 0)  # 오른쪽으로 이동
game.rotate_piece()     # 회전
game.hard_drop()        # 하드 드롭
```

### 특징 추출

```python
from rl_tetris.features import BoardFeatureExtractor

# 특징 추출
features = BoardFeatureExtractor.extract_features(board)
# Output: [lines_cleared, holes, bumpiness, total_height]

# 특징 이름 확인
names = BoardFeatureExtractor.get_feature_names()
# Output: ['lines_cleared', 'holes', 'bumpiness', 'total_height']
```

---

## 결론

이 리팩토링을 통해 RL-Tetris 프로젝트는:

1. **더 명확한 구조**를 갖게 되었습니다
2. **테스트 가능한 코드**로 변경되었습니다
3. **유지보수가 쉬운** 코드베이스가 되었습니다
4. **확장 가능한 아키텍처**를 갖추었습니다
5. **하위 호환성**을 유지했습니다

이제 새로운 기능을 추가하거나 버그를 수정하기가 훨씬 쉬워졌으며, 각 컴포넌트를 독립적으로 테스트할 수 있습니다.

---

**작성일**: 2025-11-21
**버전**: 0.2.0
**작성자**: Claude AI
