# TABNINE.md AO Tooling Instructions

Use AO tools for repository context and local execution when they are available.

AO tool precedence:

- Treat compact AO MCP tools as the default workflow surface before provider-native repository, shell, or file tools.
- Use `mcp_ao-context_ao_find_files` for file discovery and `mcp_ao-context_ao_search_code` for semantic/code evidence; answer from search results when they contain enough file/line evidence.
- Use `mcp_ao-context_ao_read_file` only for bounded file slices after discovery/search proves the file is needed; avoid full-file reads by default.
- Do not use built-in broad repository tools such as `grep_search`, `glob`, `list_directory`, or `read_file` for repository context until AO compact/search/open tools have been tried first.
- Use built-in repository tools only when AO MCP tools are unavailable, fail, or return insufficient file/line evidence; if you fall back, state the specific AO gap first.
- Prefer one targeted `mcp_ao-context_ao_search_code` call per subquestion; do not repeatedly reformulate similar searches unless the first search misses the needed subsystem.
- When more context is needed for multiple refs, call `mcp_ao-context_ao_expand_ranges` once with all required `path/start_line/end_line` ranges; avoid repeated `mcp_ao-context_ao_expand_lines` calls.
- Use `mcp_ao-context_ao_open_chunk` or a single `mcp_ao-context_ao_expand_lines` only for one-off follow-up context.
- Use `mcp_ao-context_ao_git_status` and `mcp_ao-context_ao_git_diff` instead of shelling out to git.
- Use `mcp_ao-context_ao_run_tests` for validation; use `mcp_ao-context_ao_run_local_command` only when no specialized AO command exists.
- Use `mcp_ao-context_ao_replace` for exact targeted edits and `mcp_ao-context_ao_write_file` only when creating/replacing a whole file is intentional.
- Use `mcp_ao-context_ao_latest_run` and `mcp_ao-context_ao_open_artifact` for orchestrator artifacts instead of direct artifact file reads.
- Use `mcp_ao-context_ao_health` for compact diagnostics and `mcp_ao-context_ao_index_status` when repository context looks stale or incomplete.
- Prefer file/line citations and concise summaries over pasted content.
- Keep tool responses within the requested token budget.
