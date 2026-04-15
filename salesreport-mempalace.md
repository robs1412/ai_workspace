# Salesreport MemPalace Usage

Local operator workflow for searching the `salesreport` repo with MemPalace.

## Paths

- Repo: `/Users/admin/Documents/GitHub/salesreport`
- Source mirror: `/Users/admin/Documents/GitHub/salesreport/.mempalace/full-src`
- Palace: `/Users/admin/Documents/GitHub/salesreport/.mempalace/full-palace`
- Search helper: `ai_workspace/scripts/salesreport_mempalace_search.sh`
- Reindex helper: `ai_workspace/scripts/salesreport_mempalace_reindex.sh`

## Common Commands

```bash
zsh "/Users/admin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/ai_workspace/scripts/salesreport_mempalace_search.sh" status
zsh "/Users/admin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/ai_workspace/scripts/salesreport_mempalace_search.sh" rooms
zsh "/Users/admin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/ai_workspace/scripts/salesreport_mempalace_search.sh" search "saved reports visibility admin"
zsh "/Users/admin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/ai_workspace/scripts/salesreport_mempalace_search.sh" room hitlist_optimization "approve selected"
zsh "/Users/admin/Library/CloudStorage/GoogleDrive-robert@kovaldistillery.com/My Drive/2026_workspace_sync/ai_workspace/scripts/salesreport_mempalace_reindex.sh"
```

## Notes

- Keep this workflow off live. The helper scripts live in `ai_workspace`, not in the `salesreport` repo.
- `.mempalace/` stays untracked inside `salesreport`.
- Codex MCP is configured globally as `mempalace-salesreport`.
- The local editable MemPalace clone was patched to index `.php` files because upstream did not include them.
