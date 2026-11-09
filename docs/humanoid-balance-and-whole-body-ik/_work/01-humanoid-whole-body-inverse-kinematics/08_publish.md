---
stage: 08_publish
chapter: 01-humanoid-whole-body-inverse-kinematics
status: complete
---

# 5단계 출판 기록

## 출판 결과

- 공개 장: `docs/humanoid-balance-and-whole-body-ik/01-humanoid-whole-body-inverse-kinematics.md`
- 기준 원고: 공개 장 본문 자체(adr/0001). 확정 기록은 `docs/humanoid-balance-and-whole-body-ik/_work/01-humanoid-whole-body-inverse-kinematics/07_final.md`
- 인터랙티브 실습: `docs/humanoid-balance-and-whole-body-ik/assets/humanoid-whole-body-inverse-kinematics/whole-body-ik-lab.html`
- 목차: `docs/humanoid-balance-and-whole-body-ik/index.md`의 5단계와 실습 목록에 연결
- 이전 단계 연결: 4단계의 `다음 단계` 절에서 5단계 공개 장으로 연결

## 내용 검증

- 1–6단계 공개 장은 각각 H1이 하나다.
- 공개 장 본문이 기준 원고이며 `_work/`에 본문 사본을 두지 않는다.
- 공개 장과 목차의 상대 링크는 모두 존재한다.
- 공개 장에 `TODO`, `TBD`, `검증대기`, `출처대기`, `미완성` 표지가 없다.
- 공개 장에 줄 끝 공백이 없다.
- 5단계 작업 기록 `01_scope.md`부터 `08_publish.md`까지 갖췄다.

## 실습 검증

- 인라인 자바스크립트 구문 검사를 통과했다.
- 중복 HTML `id`와 누락된 `getElementById` 대상이 없다.
- 일반·목표 충돌·이중 지지·도달 불가의 네 프리셋이 동작한다.
- 기본 화면과 360 px 폭에서 가로 넘침이 없다.
- 브라우저 콘솔 오류가 없다.
- 화면에 좌표축, 단위, 베이스 이동 상한과 반복 클램프·접촉 재보정의 한계가 보인다.
- 30단계 실행에서 가중 DLS와 접촉 우선 계층 IK가 각각 10회에 수렴했다.
- 일반 목표에서 두 방법이 수렴하고, 충돌·이중 지지에서는 접촉 우선 해가 지지발 오차를 0으로 유지한다.

## 빌드 검증

- 현재 저장소에서 `python -m mkdocs build --strict` 통과(MkDocs 1.6.1, Material 9.7.6, uv와 Python 3.14)
