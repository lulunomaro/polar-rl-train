# Host210 workspace cache cleanup

The user requested removal of obsolete old data after the 4TB workspace migration. This stage removed only identified reconstructible caches.

- Workspace: `/mnt/robowork4t/workspaces/robomaster`
- Removed regular cache files: 15,219
- Removed logical payload: 115,648,483,306 bytes (115.648 GB)
- Measured available-space increase after filesystem sync: 115,684,937,728 bytes (115.685 GB)
- Available space after cleanup: 3,566,104,272,896 bytes (3.566 TB)
- Removed empty cache directories: 5,556
- Actual deletion errors: 0; actual execution skips: 0.

## Removed categories

| Category | Files | Logical GB |
| --- | ---: | ---: |
| python_bytecode | 12,905 | 0.212200 |
| .pytest_cache | 63 | 0.000016 |
| shadercache | 5 | 0.000557 |
| deriveddatacache | 1,652 | 115.153945 |
| kit_cache | 14 | 0.000001 |
| computecache | 580 | 0.281765 |

## Kept data and live-process protection

Unique training checkpoints, pretrained model weights, raw datasets, CAD, source code, Git objects, historical reports, failure evidence and the closed-stage archive were excluded from the deletion plan. Virtual environments were retained. Python bytecode was removed only when the corresponding source file was present. A live Python process was found in the historical MOD4 takeover workspace; its context was excluded during preparation. Final execution repeated the process/file-usage check with root visibility, checked the frozen plan SHA, source metadata, original disk UUID and canonical paths, and removed only individual reviewed files followed by empty cache directories. No process, service, GPU, model or training state was changed.

Cache contents were not fully read/hash-scanned across 115GB: they are disposable derived data. Exact source path, size, mtime and inode, actual deletion outcomes, and SHA256 of the compressed deletion manifest are retained. Do not interpret metadata checks as content SHA256.

The previously rejected local Windows temporary Git deletion and the unreadable local Windows directory were outside this server-cache cleanup and remain unresolved.

## Attempts and limitations

The first read-only du query timed out after 45 seconds. A combined read-only Git-status/query command exceeded the 55-second SSH channel timeout. These did not delete data; asynchronous filesystem inventory and SFTP receipt reading were used. A later local receipt reader attempted JSON parsing on an empty placeholder created by a failed optional SFTP download; the successful cleanup was not repeated. All three reader/query issues are retained separately from the successful deletion result.

Files with equal sizes were catalogued as possible duplicate candidates only. No content-duplicate conclusion was inferred and no model/archive duplicate removal was performed.

## Evidence

`CONTROL_EVIDENCE_01.tar.gz` and `EVIDENCE_INDEX_01.json` retain the controls, original scan inventory, frozen plan, process checks, deletion receipt, progress, logs and reader failures. This is one new cleanup stage with one annotated trial. Verification after Git recording is tool output only to avoid report/commit loops.
