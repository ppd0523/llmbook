-- 이 파일들은 lazy.nvim이 시작되기 전에 자동으로 로드된다.

-- JavaScript와 TypeScript: 코드 인텔리전스는 vtsls가, 포매팅은 Prettier가
-- 맡고, ESLint는 진단과 code action을 제공한다.
vim.g.lazyvim_ts_lsp = "vtsls"
vim.g.lazyvim_prettier_needs_config = true
vim.g.lazyvim_eslint_auto_format = false

-- Python: 타입과 탐색은 Pyright가, lint와 포매팅은 네이티브 Ruff 서버가
-- 맡는다.
vim.g.lazyvim_python_lsp = "pyright"
vim.g.lazyvim_python_ruff = "ruff"

-- Rust 진단은 rust-analyzer에 맡긴다.
vim.g.lazyvim_rust_diagnostics = "rust-analyzer"
