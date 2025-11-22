# Installation

## Requirements

- Python 3.10 or higher
- pip

## Install from PyPI

가장 간단한 방법은 PyPI에서 직접 설치하는 것입니다:

```bash
pip install rl-tetris
```

## Install from Source

개발 버전을 설치하거나 기여하려면 소스에서 설치할 수 있습니다:

```bash
# 저장소 클론
git clone https://github.com/hot666666/RL-Tetris.git
cd RL-Tetris

# Poetry 설치 (아직 설치하지 않은 경우)
curl -sSL https://install.python-poetry.org | python3 -

# 의존성 설치
poetry install

# 개발 의존성 포함 설치
poetry install --with dev

# 예제 실행을 위한 의존성 포함
poetry install --with examples
```

## Verify Installation

설치가 제대로 되었는지 확인하려면:

```python
import rl_tetris
import gymnasium as gym

# 환경 생성 테스트
env = gym.make("RL-Tetris-v0")
obs, info = env.reset()
print("Installation successful!")
print(f"Observation shape: {obs.shape}")
```

출력 예시:
```
Installation successful!
Observation shape: (20, 10)
```

## Dependencies

RL-Tetris의 주요 의존성:

- **numpy**: 배열 연산
- **opencv-python**: 렌더링
- **gymnasium**: 강화학습 환경 인터페이스

개발 의존성:

- **pytest**: 테스트 프레임워크

예제 의존성 (선택사항):

- **torch**: 딥러닝 모델
- **tensorboard**: 학습 모니터링
- **wandb**: 실험 추적

## Next Steps

- [Quick Start](quick-start.md) - 첫 번째 에이전트 만들기
- [Examples](examples.md) - 더 많은 예제 살펴보기
