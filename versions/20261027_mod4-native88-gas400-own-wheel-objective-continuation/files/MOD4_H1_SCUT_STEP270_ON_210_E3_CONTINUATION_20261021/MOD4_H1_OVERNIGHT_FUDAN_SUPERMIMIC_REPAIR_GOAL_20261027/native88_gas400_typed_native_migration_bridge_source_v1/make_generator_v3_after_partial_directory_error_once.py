"""Keep both failed generators/errors; V3 only makes partial-dir reuse explicit."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
text=(HERE/'prepare_native88_source_integration_V2_after_literal_anchor_fix.py').read_text('utf8')
text=text.replace('dst.parent.mkdir(parents=True);','dst.parent.mkdir(parents=True,exist_ok=True);')
text=text.replace('V2_ENTRY_CONSUMED_SOURCE_ONLY_ACTUAL','V3_ENTRY_CONSUMED_SOURCE_ONLY_ACTUAL').replace('V2_ORIGINAL_NATIVE88_SOURCE_PREPARATION_ERROR_ACTUAL','V3_ORIGINAL_NATIVE88_SOURCE_PREPARATION_ERROR_ACTUAL')
with (HERE/'prepare_native88_source_integration_V3_partial_directory_fix.py').open('x',encoding='utf8',newline='') as f:f.write(text)
