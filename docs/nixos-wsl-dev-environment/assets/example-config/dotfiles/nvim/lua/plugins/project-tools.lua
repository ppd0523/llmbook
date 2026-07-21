return {
  -- LSPs and formatters are committed as project dependencies or rustup
  -- components. Disabling Mason prevents an editor-private second version.
  { "mason-org/mason-lspconfig.nvim", enabled = false },
  { "mason-org/mason.nvim", enabled = false },
}
