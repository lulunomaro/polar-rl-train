"""Only continue the unexecuted record: prior monitor guard rejected before capture/objects."""
from archive_actual_reference_stage_once import *
assert (R/'SCUT_MONITOR_TERMINAL_NEWLINE_SCHEMA_REVIEW.json').exists()
assert not DEST.exists() and not (R/'SCUT_REFERENCE_ARCHIVE_STARTED.json').exists() and not gitio.g('tag','--list','*'+ID)
main()
