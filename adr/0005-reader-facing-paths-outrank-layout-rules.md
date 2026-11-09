# 독자가 실행하는 경로는 저장소 배치 규칙보다 우선한다

MkDocs 책 폴더 루트에 둘 경로는 `.guide/OUTPUTS.md`가 정한다. 본문이 독자에게 실행 절차로 지시하는 경로는 이 배치 규칙의 적용 대상 밖이다. 예를 들어 `docs/pytorch-ppo-learning/`의 `examples/`, `tests/`, `requirements.txt`는 본문이 실행 절차로 지시하므로 책 폴더 루트에 둔다.

## 고려한 대안

세 경로를 `assets/` 아래로 옮기는 방안이 있다. 본문 [03장](../docs/pytorch-ppo-learning/03-pytorch-for-policies.md)과 [08장](../docs/pytorch-ppo-learning/08-use-ppo-with-torchrl.md)은 `python -m pip install -r requirements.txt`를 실행 절차로 제시한다. 옮기면 독자가 입력하는 명령이 `assets/requirements.txt`로 바뀐다. 저장소 관리 편의를 위해 독자의 절차를 한 단계 복잡하게 만드는 교환이다.

`tests/`만 떼어 옮기면 [06장](../docs/pytorch-ppo-learning/06-build-ppo-with-pytorch.md)의 디렉터리 트리 설명과 실제 배치가 어긋나고, "예제 옆에 테스트"라는 구조 설명도 다시 써야 한다. 규칙 문구는 만족시키고 실질은 나빠진다.

배치 규칙은 저장소를 관리하기 위해 있다. 독자는 저장소 규칙을 모르고 본문만 읽으므로, 본문이 지시하는 경로는 독자가 기대하는 자리에 있어야 한다.

## 결과

본문이 실행 절차로 지시하는 파일은 책 폴더 루트에 둘 수 있다. 이 예외는 독자가 직접 입력하는 경로에만 적용되며, 본문이 참조만 하는 그림과 다운로드 파일은 `assets/` 규칙을 그대로 따른다. `_work/`와 단계 파일에는 적용하지 않는다. 독자가 읽지 않는 내부 기록이기 때문이다.
