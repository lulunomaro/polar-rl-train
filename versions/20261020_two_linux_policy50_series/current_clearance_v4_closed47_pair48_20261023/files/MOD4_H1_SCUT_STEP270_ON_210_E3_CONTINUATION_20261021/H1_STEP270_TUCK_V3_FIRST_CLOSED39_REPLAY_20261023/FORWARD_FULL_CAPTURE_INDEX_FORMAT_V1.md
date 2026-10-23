# Complete capture index, forward format

Large new complete indexes use `complete_capture_index_full_ordered_utf8_parts_v1`.
`COMPLETE_FILE_CAPTURE_INDEX.json` is a descriptor with epoch, kind, full JSON byte size/SHA, complete entry count, and an ordered list of UTF-8 parts. It is not an excerpt or an empty index. Each part is at most 24,000,000 bytes. All original index JSON values remain in the full reassembled bytes.

Use `capture_index_ordered_parts_v1.read_capture_index(path, repo_root)` in every future archive helper. It accepts old plain JSON indexes and the new complete format, validates individual and combined SHA/size and UTF-8, and returns the original full index with `entries`. Unknown or missing formats fail explicitly. Do not use an old consumed helper to read a new descriptor as though it directly contained `entries`.

Only the new unused archive writer changed. Existing indexes, commits, annotated tags, models, original records and training/budget code remain under their existing retention and accounting rules. The writer still verifies every committed blob and every complete text reassembly. Its final `new_full_large_texts` count includes the full capture index when partitioned.

The memory CPU receipt uses the actual previously committed 86,468,238-byte index with 89,869 entries. It verifies exact full-byte and JSON round trips and rejects changed, missing and reordered parts. No temporary directories, binary model/raw hashes, GPU work, host queries or ledger writes were used.
