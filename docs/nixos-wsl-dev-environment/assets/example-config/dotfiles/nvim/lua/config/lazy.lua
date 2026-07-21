local project_spec = vim.fs.find(".lazy.lua", {
  path = vim.uv.cwd(),
  upward = true,
})[1]
local project_root = project_spec and vim.fs.dirname(project_spec) or nil
local project_id = project_root and vim.fn.sha256(project_root):sub(1, 12) or nil
local plugin_root = project_id and (vim.fn.stdpath("data") .. "/lazy-projects/" .. project_id)
  or (vim.fn.stdpath("data") .. "/lazy")
local lockfile = project_root and (project_root .. "/.lazy-lock.json")
  or (vim.fn.stdpath("config") .. "/lazy-lock.json")

require("lazy").setup({
  root = plugin_root,
  lockfile = lockfile,
  local_spec = true,
  spec = {
    { "LazyVim/LazyVim", import = "lazyvim.plugins" },
    { import = "plugins" },
  },
  defaults = {
    lazy = false,
    version = false,
  },
  install = { colorscheme = { "tokyonight", "habamax" } },
  checker = { enabled = false },
})
