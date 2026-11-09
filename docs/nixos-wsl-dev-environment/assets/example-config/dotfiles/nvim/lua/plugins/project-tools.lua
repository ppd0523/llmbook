return {
  -- LSP와 formatter는 프로젝트 의존성 또는 rustup component로 기록된다.
  -- Mason을 끄면 편집기 전용 두 번째 버전이 생기지 않는다.
  { "mason-org/mason-lspconfig.nvim", enabled = false },
  { "mason-org/mason.nvim", enabled = false },
}
