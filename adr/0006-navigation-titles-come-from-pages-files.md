# 탐색 메뉴의 책 이름과 순서는 `.pages` 파일에서 정한다

MkDocs는 폴더에 `index.md`가 있어도 탐색 메뉴의 섹션 이름을 폴더명에서 만들고, 순서를 폴더명 알파벳순으로 정한다. 그러면 사이드바에 `Nix cpp cyclonedds` 같은 영문 폴더명이 학습 순서와 무관하게 나온다. `index.md` 프런트매터의 `title`은 그 페이지 제목에만 적용된다. 그래서 `mkdocs-awesome-pages-plugin`을 쓰고, `docs/<book-slug>/.pages`의 `title`로 표시 이름을, `docs/.pages`의 `nav`로 책 순서를 정한다.

## 고려한 대안

`mkdocs.yml`에 수동 `nav`를 쓰면 의존성 없이 해결된다. 그러나 이 저장소는 책과 챕터를 `nav`에 반복 등록하지 않는다. 챕터가 많아 `nav`를 손으로 유지하면 챕터를 추가할 때마다 두 곳을 고쳐야 한다. 폴더명에 번호를 붙이는 안은 의존성도 규칙 변경도 없지만 게시 URL이 전부 바뀌고, 사이드바 이름이 여전히 영문 폴더명이라 문제를 풀지 못한다.

`.pages`는 책 폴더 안에 놓이므로 "폴더 하나가 책 한 권"이라는 원칙과 맞고, 책을 옮기면 표시 이름도 따라간다. 챕터 순서는 여전히 파일명의 읽기 순서 번호가 정하므로 챕터 단위의 수동 등록은 생기지 않는다.

## 결과

`docs/.pages`의 책 순서는 `docs/index.md`의 책 목록과 같게 유지한다. 책을 추가·삭제·개명하면 `docs/index.md`, `docs/.pages`, 해당 책의 `.pages`를 함께 갱신한다.

`.pages`의 `title`에 콜론이 들어가면 YAML 파싱이 실패하므로 값을 따옴표로 감싼다. 책 제목에 콜론이 흔하다.

`mkdocs-awesome-pages-plugin`은 직접 의존성이므로 전이 의존성과 함께 `requirements.txt`에 고정한다.

## 표시 위치

책 번호는 세로로 나열될 때만 쓸모가 있다. `navigation.tabs`를 켜면 최상위 항목인 책이 상단 가로 탭으로 한 줄에 늘어서 번호가 찾는 데 도움이 되지 않으므로, `navigation.tabs`와 `navigation.tabs.sticky`를 쓰지 않는다. `navigation.sections`도 쓰지 않는다. 이 옵션은 최상위 섹션을 항상 펼친 묶음으로 그려 모든 책과 챕터가 한 번에 펼쳐진다. 그래서 책은 왼쪽 사이드바에 번호와 함께 세로로 나오고, 각 책은 접힌 상태로 시작한다.

번호 자체는 콘텐츠에 쓰지 않는다. `.pages`의 `title`에는 제목만 두고, 사이드바 번호는 `overrides/stylesheets/nav-numbering.css`의 CSS 카운터로 붙인다. 사이드바 최상위의 `md-nav__item--nested`가 책 한 권이므로 그 항목만 센다. `docs/index.md`의 책 목록은 Markdown 순서 있는 목록이며 항목마다 `1.`로 적어 렌더링 시 번호가 매겨지게 한다. 그래서 책을 추가·삭제하거나 순서를 바꿀 때 번호를 손으로 고칠 일이 없다.
