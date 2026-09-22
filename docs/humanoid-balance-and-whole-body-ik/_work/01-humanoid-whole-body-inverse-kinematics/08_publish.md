---
stage: 08_publish
chapter: 05-humanoid-whole-body-inverse-kinematics
status: complete-with-environment-warning
updated: 2026-08-12
---

# 5단계 출판 기록

## 출판 결과

- 공개 장: `docs/humanoid-balance-and-whole-body-ik/01-humanoid-whole-body-inverse-kinematics.md`
- 최종 원고: `docs/humanoid-balance-and-whole-body-ik/_work/01-humanoid-whole-body-inverse-kinematics/07_final.md`
- 인터랙티브 실습: `docs/humanoid-balance-and-whole-body-ik/assets/humanoid-whole-body-inverse-kinematics/whole-body-ik-lab.html`
- 목차: `docs/humanoid-balance-and-whole-body-ik/index.md`의 5단계와 실습 목록에 연결
- 이전 단계 연결: 4단계의 `다음 단계` 절에서 5단계 공개 장으로 연결

## 내용 검증

- 1–5단계 공개 장은 각각 H1이 하나다.
- 최종 원고 본문과 공개 장은 마지막 줄바꿈을 제외하고 일치한다.
- 공개 장과 목차의 상대 링크는 모두 존재한다.
- 공개 장과 최종 원고에 `TODO`, `TBD`, `검증대기`, `출처대기`, `미완성` 표지가 없다.
- 공개 장과 최종 원고에 줄 끝 공백이 없다.
- 5단계 작업 기록 `01_scope.md`부터 `08_publish.md`까지 갖췄다.

## 실습 검증

- 인라인 자바스크립트 구문 검사를 통과했다.
- 중복 HTML `id`와 누락된 `getElementById` 대상이 없다.
- 일반·목표 충돌·이중 지지·도달 불가의 네 프리셋이 동작한다.
- 기본 화면과 360 px 폭에서 가로 넘침이 없다.
- 브라우저 콘솔 오류가 없다.
- 일반 목표에서 두 방법이 수렴하고, 충돌·이중 지지에서는 접촉 우선 해가 지지발 오차를 0으로 유지한다.

## 빌드 검증

- 기본 MkDocs 테마와 프로젝트의 Markdown 확장을 사용한 `--strict` 빌드: 통과
- 원래 Material 테마 설정의 `--strict` 빌드: 환경 오류로 중단
- 환경 오류: 설치된 Material 검색 플러그인이 `partials/language.html`을 찾지 못한다.
- 판정: 같은 문서 집합이 기본 테마의 엄격 빌드를 통과했으므로 5단계 원고·내부 링크 문제는 아니다. Material 패키지 설치 상태는 별도 저장소 환경 정비 대상이다.

## 2차 퇴고 재검증

- 전신 구성, 단위 쿼터니언, 랭크, 활성 제약, 볼록 영역과 후속 locomotion 용어의 첫 설명을 보강했다.
- 접촉 등식의 영공간 해법과 관절 제한 부등식의 제약 최적화 적용 범위를 분리했다.
- 공개 장과 `07_final.md` 본문은 마지막 줄바꿈을 제외하고 일치한다.
- HTML에서 좌표축, 단위, 베이스 이동 상한과 반복 클램프·접촉 재보정의 한계가 보인다.
- 30단계 실행 시 가중 DLS와 접촉 우선 계층 IK가 각각 10회에 수렴했다.
- 브라우저 콘솔 오류와 기본 화면의 가로 넘침이 없다.
- 퇴고 후 기본 MkDocs 테마의 `--strict` 빌드를 다시 통과했다.

## 정리

- 검증용 임시 설정과 빌드 디렉터리를 삭제했다.
- 커밋과 푸시는 이번 요청 범위에 포함되지 않아 수행하지 않았다.
