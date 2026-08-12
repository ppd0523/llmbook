---
title: 초고 기록
version: 1.0
status: complete
owner: agent
updated: 2026-08-12
target_reader: EDSDK를 처음 접하는 기술 담당자
topic: Canon EDSDK 기능 중심 카메라 제어
---

# 초고 기록

## 초고 범위

- 2026-08-12에 6개 챕터의 전 범위를 작성했다.
- 코드·언어별 DLL 연동 설명은 의도적으로 제외했다.
- 촬영·전송, 라이브 뷰, AF·상대 렌즈 구동, 설정·동영상의 절차와 표를 포함했다.

## 초고에서 확인할 대상

- `SaveTo`의 Host/Both와 `DownloadComplete`/`DownloadCancel`의 관계
- 셔터 버튼 해제 요구
- PC EVF 출력 비트 추가·제거 순서
- AF·DriveLens의 라이브 뷰 조건과 모델·렌즈 의존성
- 기준 세 기종의 호환성 및 지역별 명칭

## 예제·연습 설계

- 코드가 아닌 촬영·전송 상태 흐름을 Worked Example으로 제시했다.
- 각 핵심 장 끝에 확인 질문을 두었다.
- 6장에 실제 카메라·렌즈 조합으로 수행할 승인 시험표를 뒀다.
