# 탐색 메뉴의 책 이름과 순서는 `.pages` 파일에서 정한다

MkDocs는 폴더에 `index.md`가 있어도 탐색 메뉴의 섹션 이름을 폴더명에서 만든다. 그래서 게시 사이트의 사이드바는 책 13권을 `Humanoid balance and whole body ik`, `Nix cpp cyclonedds` 같은 영문 폴더명으로 표시했다. `index.md` 프런트매터의 `title`은 그 페이지 제목에만 적용되어 한국어 제목이 탐색 메뉴에 나타나지 않았고, 책 순서도 폴더명 알파벳순이라 학습 순서와 무관했다. `mkdocs-awesome-pages-plugin`을 도입해 `docs/<book-slug>/.pages`의 `title`로 표시 이름과 번호를, `docs/.pages`의 `nav`로 책 순서를 정한다.

## 고려한 대안

`mkdocs.yml`에 수동 `nav`를 쓰면 의존성 없이 해결된다. 그러나 이 저장소는 책과 챕터를 `nav`에 반복 등록하지 않기로 했고, 챕터가 100개를 넘는 상태에서 `nav`를 손으로 유지하면 챕터를 추가할 때마다 두 곳을 고쳐야 한다. 폴더명에 번호를 붙이는 안은 의존성도 규칙 변경도 없지만 게시 URL이 전부 바뀌고, 사이드바 이름이 여전히 영문 폴더명이라 원래 문제를 풀지 못한다.

`.pages`는 책 폴더 안에 놓이므로 "폴더 하나가 책 한 권"이라는 원칙과 맞고, 책을 옮기면 표시 이름도 따라간다. 챕터 순서는 여전히 파일명의 읽기 순서 번호가 정하므로 챕터 단위의 수동 등록은 생기지 않는다.

## 결과

`docs/.pages`의 책 순서는 `docs/index.md`의 책 목록과 같게 유지한다. 책을 추가·삭제·개명하면 세 곳(`docs/index.md`, `docs/.pages`, 해당 책의 `.pages`)을 함께 갱신한다.

`.pages`의 `title`에 콜론이 들어가면 YAML 파싱이 실패하므로 값을 따옴표로 감싼다. 책 제목에 콜론이 흔하다.

`requirements.txt`의 직접 의존성이 `mkdocs-material` 하나에서 둘로 늘었다. 전이 의존성 `bracex`, `natsort`, `wcmatch`도 함께 고정했다.
