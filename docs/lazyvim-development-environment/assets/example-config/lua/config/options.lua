-- These files are loaded automatically before lazy.nvim starts.

-- JavaScript and TypeScript: vtsls handles code intelligence, Prettier owns
-- formatting, and ESLint contributes diagnostics and code actions.
vim.g.lazyvim_ts_lsp = "vtsls"
vim.g.lazyvim_prettier_needs_config = true
vim.g.lazyvim_eslint_auto_format = false

-- Python: Pyright handles types/navigation and the native Ruff server handles
-- linting and formatting.
vim.g.lazyvim_python_lsp = "pyright"
vim.g.lazyvim_python_ruff = "ruff"

-- Rust diagnostics stay with rust-analyzer.
vim.g.lazyvim_rust_diagnostics = "rust-analyzer"
