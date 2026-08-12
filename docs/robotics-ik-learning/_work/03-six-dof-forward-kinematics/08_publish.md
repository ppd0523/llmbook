---
stage: 08_publish
chapter: 03-six-dof-forward-kinematics
status: complete-with-environment-warning
updated: 2026-08-11
---

# 3단계 출판 기록

## 출판 대상

- 기준 원고: `_work/03-six-dof-forward-kinematics/07_final.md`
- 공개 장: `03-six-dof-forward-kinematics.md`
- 인터랙티브 실습: `assets/six-dof-forward-kinematics/forward-kinematics-lab.html`
- 책 색인: `index.md`

## 검증 결과

| 항목 | 결과 |
|---|---|
| 기준 원고와 공개 장 동기화 | front matter를 제외한 본문 일치 |
| 새 용어 첫 설명 | 직렬 열린 사슬, R/P, 6R, 플랜지, TCP, 말단 자세 공간, DH, 공통수선, 홈 자세, 구면 손목을 첫 사용 지점에서 설명 |
| 단계 간 용어·기호 | task space와 workspace를 구분하고, $3\times3$의 $R_x,R_y,R_z$와 $4\times4$의 $\operatorname{Rot}_x,\operatorname{Rot}_y,\operatorname{Rot}_z$를 구분 |
| 프레임·IK 문제 정의 | 교육용 손목 중심 프레임과 실제 플랜지 프레임을 구분하고, TCP 목표와 플랜지 목표의 IK 식을 분리 |
| 공개 문서의 H1 | index와 1·2·3단계 모두 문서당 1개 |
| 미완성·검증대기·출처대기 표지어 | 공개 장에 없음 |
| 상대 링크 | 모든 대상 파일 존재 |
| 6R Worked Example | 손목 $(0,3,0)$, TCP $(0,3,-1)$, 목표 TCP에서 손목 중심을 되찾는 식의 수치 검사 통과 |
| 2R DH 유도 | 1단계 FK 식과 일치 |
| HTML JavaScript | 구문 검사 통과, 중복 정적 ID 없음, 프리셋 4개 존재, 동적 관찰 설명에 `aria-live` 적용 |
| HTML 핵심 계산 | Worked Example의 손목·TCP 수치 검사 통과 |
| HTML 특이 자세 설명 | $q_5=0°$에서 유효한 FK와 손목 특이 자세를 구분하도록 관찰 문구 갱신 |
| HTML 반응형 정의 | 960px·620px 중단점과 320px 최소 너비 확인 |
| 브라우저 자동 렌더링 | 실행 환경의 로컬 `file:` URL 보안 정책으로 자동 검수하지 못함 |
| 저장소의 Material 엄격 빌드 | 설치된 테마에서 `partials/language.html`이 누락되어 문서 처리 전에 실패 |
| 대체 MkDocs 엄격 빌드 | 같은 Markdown 확장과 기본 MkDocs 테마로 전체 문서 빌드 통과 |
| `git diff --check` | 통과 |

## 범위 확인

- 6R 직렬 매니퓰레이터의 FK와 표준 DH까지 출판한다.
- PID·PD 제어, 동역학, Jacobian 계산, 수치 IK는 포함하지 않는다.
- POE는 후속 공개 강의의 대안적 FK 표현으로만 안내한다.

## 다음 출판 단위

4단계 `Jacobian과 수치 IK`에서 관절의 작은 변화와 말단 자세 오차를 연결하고 반복 계산으로 목표 자세에 접근한다.

## 환경 경고

저장소의 `.venv`에 설치된 Material 테마의 `templates/partials/`가 비어 있어 원래 `mkdocs.yml` 빌드는 콘텐츠를 읽기 전에 중단되었다. 새 원고의 Markdown 구조와 링크 문제를 분리하기 위해 동일한 Markdown 확장과 기본 MkDocs 테마로 엄격 빌드를 수행했고 통과했다. Material 패키지를 정상 상태로 복구한 뒤 원래 설정의 엄격 빌드와 실제 브라우저 화면 검수를 다시 수행할 수 있다.
