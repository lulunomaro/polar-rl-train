"""Preserve V1 literal-anchor error and partial exact copies; derive corrected V2."""
from pathlib import Path
HERE=Path(__file__).resolve().parent
text=(HERE/'prepare_native88_source_integration_once.py').read_text('utf8')
old=" with p.open('xb') as f:f.write(raw)"
new=" if p.exists():assert p.read_bytes()==raw,'existing partial source differs'\n else:\n  with p.open('xb') as f:f.write(raw)"
assert text.count(old)==1;text=text.replace(old,new)
text=text.replace('                policy_updates=expected[','policy_updates=expected[')
text=text.replace("put('ENTRY_CONSUMED_SOURCE_ONLY_ACTUAL.json'","put('V2_ENTRY_CONSUMED_SOURCE_ONLY_ACTUAL.json'")
text=text.replace("put('ORIGINAL_NATIVE88_SOURCE_PREPARATION_ERROR_ACTUAL.json'","put('V2_ORIGINAL_NATIVE88_SOURCE_PREPARATION_ERROR_ACTUAL.json'")
old="dst.write_text(text,encoding='utf8',newline='')"
text=text.replace(old,'write_new_or_verify(dst,text)')
marker="def replace(text,old,new):"
fn="def write_new_or_verify(p,text):\n raw=text.encode('utf8')\n if p.exists():assert p.read_bytes()==raw,'partial generated source changed'\n else:\n  with p.open('xb') as f:f.write(raw)\n"
assert text.count(marker)==1;text=text.replace(marker,fn+marker)
p=HERE/'prepare_native88_source_integration_V2_after_literal_anchor_fix.py'
with p.open('x',encoding='utf8',newline='') as f:f.write(text)
