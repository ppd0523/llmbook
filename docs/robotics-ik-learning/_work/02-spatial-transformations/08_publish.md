---
stage: 08_publish
chapter: 02-spatial-transformations
status: published-locally
updated: 2026-08-11
---

# 2단계 출판 기록

## 출판 대상

- 기준 원고: `_work/02-spatial-transformations/07_final.md`
- 공개 장: `02-spatial-transformations.md`
- 인터랙티브 실습: `assets/spatial-transformations/spatial-transform-lab.html`
- 책 색인: `index.md`

## 검증 결과

| 항목 | 결과 |
|---|---|
| 기준 원고와 공개 장 본문 동기화 | 통과 |
| 1·2단계 기호 연결 | $q$: 관절벡터, $\mathbf r$: 공간의 점으로 구분 |
| 용어·표기 교정 | 좌표계의 방위, xz 평면, xy 평면 반사로 통일 |
| 6자유도 연결부 | 목표 첨자 $d$를 정의하고 관절별 기여가 기구 구조에 따라 달라짐을 명시 |
| 미완성·검증대기·출처대기 표지어 검색 | 없음 |
| 로컬 상대 링크 대상 존재 확인 | 통과 |
| HTML 자바스크립트 구문 검사 | 통과 |
| 브라우저 콘솔 오류·경고 | 없음 |
| Worked Example 3 프리셋 | `r_A=[2,2,3]^T` 확인 |
| 점·방향벡터 비교 | 이동 변경 시 `r_A`만 변하고 `d_A`는 유지됨을 확인 |
| 회전 순서 비교 | Z-Y-X는 `[0,1,0]^T`, X-Y-Z는 `[0,0,1]^T` 확인 |
| 짐벌락 수치 예 | pitch 90°에서 roll=yaw=0°와 30°의 회전행렬이 같음을 확인 |
| 390×844 반응형 화면 | 단일 열 배치와 조작부 가독성 확인 |
| MkDocs 엄격 빌드 | 통과 |
| `git diff --check` | 통과 |

## 범위 확인

- 회전행렬과 강체변환까지 출판했다.
- PID·PD 제어, 동역학, 각속도, Jacobian 계산은 포함하지 않았다.
- axis-angle, Rodrigues 공식, 쿼터니언은 이 단계에서 다루지 않았다.

## 다음 출판 단위

3단계 `6자유도 매니퓰레이터의 순기구학`에서 관절 좌표계 설정, 변환 체인, DH와 POE의 역할을 다룬다.
