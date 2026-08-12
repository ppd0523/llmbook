---
stage: 08_publish
chapter: 04-jacobian-numerical-inverse-kinematics
status: complete-with-environment-warning
updated: 2026-08-12
---

# 4단계 출판 기록

## 출판 대상

- 기준 원고: `_work/04-jacobian-numerical-inverse-kinematics/07_final.md`
- 공개 장: `04-jacobian-numerical-inverse-kinematics.md`
- 인터랙티브 실습: `assets/jacobian-numerical-inverse-kinematics/numerical-ik-lab.html`
- 책 색인: `index.md`
- 이전 장 연결: `03-six-dof-forward-kinematics.md`

## 검증 결과

| 항목 | 결과 |
|---|---|
| 기준 원고와 공개 장 동기화 | front matter를 제외한 본문 일치 |
| 3단계 기준 원고 동기화 | 4단계 연결 링크를 공개 장과 기준 원고에 동일하게 반영 |
| 새 용어 첫 설명 | 2-노름, 미분, 편미분, 연쇄법칙, 국소 선형 근사, 자코비안, 랭크, 의사역행렬, 특이값, DLS, 외적, 정규화, 특성 길이, 여유 기구, 영공간을 첫 사용 지점에서 설명 |
| 공개 문서의 H1 | 1~4단계 모두 문서당 1개 |
| 미완성·검증대기·출처대기 표지어 | 공개 장과 기준 원고에 없음 |
| 상대 링크 | 색인, 3단계, 4단계의 모든 대상 파일 존재 |
| 2R 자코비안 유도 | 수치 자세와 중앙 유한차분 검사 통과 |
| 2R 특이점 조건 | $\det J=l_1l_2\sin q_2$와 완전 신장 수치 검사 일치 |
| Worked Example 1 | 업데이트 $(0.1,0)$ rad, 실제 FK $(0.8951707,1.0948376)$ 확인 |
| Worked Example 2 | DLS 업데이트 $(0.0399202,0.0199601)$ rad, 실제 FK와 잔차 확인 |
| 3D 기하 자코비안 | 외적 기반 회전·직동관절 열의 수치 예 통과 |
| 방위 오차 | 작은 z축 회전에서 $\mathbf e_R\approx(0,0,\delta)$ 확인 |
| HTML JavaScript | 구문 검사 통과, 중복 정적 ID 없음, 프리셋 4개 존재 |
| HTML 정상 자세 | 3회 안에 오차 0.005 미만 |
| HTML 특이 근처 | 7회 안에 오차 0.005 미만 |
| HTML 완전 신장 | 8회 안에 오차 0.005 미만, 첫 DLS 업데이트가 본문과 일치 |
| HTML 도달 불가 | 300회 뒤 오차 약 0.344가 남아 최대 반복으로 종료 |
| HTML 초기화 | 정상 프리셋 실행 뒤 $(0°,90°)$ 복원, 사용자 지정 $q_1=25°$·자코비안 전치 선택 뒤에도 사용자 시작 상태 복원 |
| HTML 반응형·접근성 | 실제 360px 폭에서 가로 넘침 없이 단일 열 배치, 캔버스·초기화 버튼 표시, 캔버스 대체 설명과 `aria-live` 확인 |
| 브라우저 자동 렌더링 | 기본 폭과 360px 폭 화면 검수 통과, 콘솔 오류 없음, +x·+y 축과 자코비안 열 표시 확인 |
| 저장소의 Material 엄격 빌드 | 설치된 테마에서 `partials/language.html`이 누락되어 문서 처리 전에 실패 |
| 대체 MkDocs 엄격 빌드 | 같은 Markdown 확장과 기본 MkDocs 테마로 전체 문서 빌드 통과 |
| `git diff --check` | 통과 |

## 범위 확인

- 자코비안의 입문 수학, 2R 유도, 특이점, 의사역행렬, DLS와 반복 수치 IK까지 출판한다.
- 3D 기하 자코비안과 국소 6D 자세 오차를 6R 확장에 필요한 수준으로 포함한다.
- 휴머노이드 연결은 여유 자유도, 영공간과 다중 과제의 필요성까지 다룬다.
- PID·PD 제어, 힘·토크, 동역학, SVD 계산, 경로 계획과 전신 우선순위 알고리즘은 포함하지 않는다.

## 다음 출판 단위

5단계 `휴머노이드 보행용 전신 IK`에서 지지발·스윙발·골반 과제를 전신 관절벡터에 연결하고 접촉 조건과 과제 우선순위를 다룬다.

## 환경 경고

저장소의 `.venv`에 설치된 Material 테마가 `templates/partials/language.html`을 찾지 못해 원래 `mkdocs.yml` 빌드는 콘텐츠를 읽기 전에 중단되었다. 새 원고의 Markdown 구조와 링크 문제를 분리하기 위해 동일한 Markdown 확장과 기본 MkDocs 테마로 엄격 빌드를 수행했고 통과했다. Material 패키지를 정상 상태로 복구한 뒤 원래 설정의 엄격 빌드와 실제 브라우저 화면 검수를 다시 수행할 수 있다.
