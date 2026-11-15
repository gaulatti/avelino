# FileInput search provider and availability contract

Status: decision record for issue #5.

## Supported provider and dependency

FileInput indexed search on Linux targets FreeDesktop Tracker 3.x:
- **Build dependency:** `libtracker-sparql-3.0-dev` 3.7.1 and `pkg-config`.
- **Runtime interface:** `org.freedesktop.Tracker3.Miner.Files` on the user session D-Bus.
- **Service requirements:** Tracker's filesystem miner (`tracker-miner-fs-3`) and metadata extractors (`tracker-extract-3`).
- **Query mechanism:** Parameterized SPARQL 1.1 queries over `nfo:FileDataObject`, `nie:url`, `nfo:fileName`, and `fts:match`.

## Unavailable-provider and failure behavior

When Tracker 3.x is unavailable, not running, disabled, or encounters an internal query or index failure:
1. The search UI displays an explicit visible status: `Indexed search is unavailable: <reason>`.
2. Active search queries immediately cancel and emit empty result snapshots; the UI does not hang or enter infinite loading.
3. The application never silently modifies the user's desktop indexing configuration, never reconfigures crawl paths or GSettings (`org.freedesktop.Tracker3.Miner.Files`), and never launches unmanaged daemons.
4. The application does not perform recursive filesystem crawl substitutions. Directory browsing, file selection, and type filtering remain fully operational.
5. All search results and selection cancellations preserve standard single-owner delivery semantics.
