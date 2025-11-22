# Feature Extractors

특징 추출 클래스들은 보드 상태에서 머신러닝을 위한 특징을 추출합니다.

## BoardFeatureExtractor

::: rl_tetris.features.extractors.BoardFeatureExtractor
    options:
      show_source: true

## AdvancedFeatureExtractor

::: rl_tetris.features.extractors.AdvancedFeatureExtractor
    options:
      show_source: true

## Usage Examples

### 기본 특징 추출

```python
from rl_tetris.core import Board
from rl_tetris.features import BoardFeatureExtractor

board = Board(height=20, width=10)
# ... 게임 진행 ...

# 특징 추출
features = BoardFeatureExtractor.extract_features(board, lines_cleared=2)
print(features)  # [2, 5, 8, 15] - [lines, holes, bumpiness, height]

# 특징 이름
names = BoardFeatureExtractor.get_feature_names()
print(names)  # ['lines_cleared', 'holes', 'bumpiness', 'total_height']

# 특징 차원
dim = BoardFeatureExtractor.get_feature_dim()
print(dim)  # 4
```

### 고급 특징 추출

```python
from rl_tetris.features import AdvancedFeatureExtractor

# 고급 특징 추출 (10개 특징)
features = AdvancedFeatureExtractor.extract_features(board, lines_cleared=2)
print(features.shape)  # (10,)

# 특징 이름
names = AdvancedFeatureExtractor.get_feature_names()
print(names)
# ['lines_cleared', 'holes', 'bumpiness', 'total_height',
#  'max_height', 'weighted_holes', 'row_transitions',
#  'column_transitions', 'wells', 'hole_depth']
```

### 정규화

```python
# 특징 정규화
normalized = BoardFeatureExtractor.normalize_features(features)
print(normalized)  # 정규화된 값들
```

## Features Description

### Basic Features (4)

1. **lines_cleared**: 클리어된 줄 수
2. **holes**: 블록 아래의 빈 공간 수
3. **bumpiness**: 인접한 열 간 높이 차이의 합
4. **total_height**: 모든 열 높이의 합

### Advanced Features (10)

기본 4개 + 추가 6개:

5. **max_height**: 가장 높은 열의 높이
6. **weighted_holes**: 가중치가 적용된 구멍 수
7. **row_transitions**: 행 내 블록 변화 수
8. **column_transitions**: 열 내 블록 변화 수
9. **wells**: 양쪽이 막힌 빈 공간 수
10. **hole_depth**: 구멍의 평균 깊이

## Custom Feature Extractor

자신만의 특징 추출기를 만들 수 있습니다:

```python
import numpy as np
from rl_tetris.core import Board

class CustomExtractor:
    @staticmethod
    def extract_features(board: Board, lines_cleared: int = 0):
        heights = board.get_column_heights()
        holes = board.get_holes()

        # 커스텀 특징
        avg_height = np.mean(heights)
        max_height = max(heights)
        height_variance = np.var(heights)

        return np.array([
            lines_cleared,
            holes,
            avg_height,
            max_height,
            height_variance
        ], dtype=np.float32)

# 사용
features = CustomExtractor.extract_features(board, 2)
```

## See Also

- [Board](../core/board.md) - 보드 특징 계산
- [GroupedFeaturesObservation](../wrappers/observation.md) - 특징 기반 관찰
