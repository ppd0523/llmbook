# 08. 게시 준비

## 공개 경로

- 책 root: `docs/isaac-lab-ball-on-plate/index.md`
- repository catalog: `docs/index.md`
- canonical source: Markdown
- work records: `docs/isaac-lab-ball-on-plate/_work/`이며 `mkdocs.yml`에서 제외됨

## 빌드 확인

현재 저장소에서 uv와 Python 3.14 환경의 MkDocs 1.6.1, Material 9.7.6으로 다음 명령이 통과한다.

```bash
python -m mkdocs build --strict
```

strict 모드이므로 내부 문서·예제 파일 링크 경고가 있으면 빌드가 실패한다.

## 게시 전 운영 메모

- 검증된 문서와 예제는 한 커밋으로 묶어 원격 저장소에 게시한다.
- 대상 Ubuntu PC에서 USD와 학습 결과가 생성되면 binary asset과 큰 log를 무조건 문서 저장소에 넣지 말고 보관 정책을 먼저 정한다.
- 새 Isaac Lab release로 갱신할 때는 version lock, 공식 source sample, 두 backend smoke test를 함께 다시 수행한다.
