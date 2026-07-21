vim.g.lazyvim_rust_diagnostics = "rust-analyzer"

return {
  { import = "lazyvim.plugins.extras.lang.rust" },
  { import = "lazyvim.plugins.extras.test.core" },
}
