# 사이트 자원은 `docs/` 밖 `overrides/`에 둔다

`docs/` 바로 아래는 폴더 하나가 책 한 권이고 게시 단위도 책이다. 어느 책에도 속하지 않는 사이트 자원을 `docs/` 안에 두면 이 원칙이 깨지므로, 테마 override와 전역 스크립트는 `overrides/`에 두고 `mkdocs.yml`의 `theme.custom_dir`로 연결한다. 특정 책에 딸린 그림·다운로드는 사이트 자원이 아니라 책 자산이므로 그 책 폴더의 `assets/`에 둔다.

## 결정 배경

MkDocs Material 공식 문서는 MathJax 설정을 `docs/javascripts/mathjax.js`에 두라고 안내한다. 이 저장소는 1책 1폴더 원칙을 지키기 위해 그 경로를 따르지 않는다. 공식 문서를 근거로 `docs/` 아래로 옮기지 않는다.

## 결과

빌드 결과에서 스크립트 경로는 `site/javascripts/mathjax.js`로, `docs/javascripts/`에 둘 때와 같다. 따라서 `extra_javascript` 참조와 페이지 링크는 위치와 무관하게 그대로 쓴다.
