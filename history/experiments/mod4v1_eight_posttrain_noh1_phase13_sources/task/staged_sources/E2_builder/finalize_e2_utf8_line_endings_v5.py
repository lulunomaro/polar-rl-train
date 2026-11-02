"""Preserve original raw SHA; normalize CRLF only in derived in-memory source."""
from pathlib import Path
import ast,json
HERE=Path(__file__).resolve().parent
s=(HERE/'build_e2_mod4v1_sources_v4.py').read_text(encoding='utf-8')
a='    read,replace,J=utility.raw_text,utility.replace,utility.J\n'
b='''    replace,J=utility.replace,utility.J
    def read(path,expected=None):
        text,ref=utility.raw_text(path,expected)
        return text.replace('\\r\\n','\\n'),ref  # input raw bytes/SHA unchanged
'''
assert a in s;s=s.replace(a,b)
a="previous,previous_ref=read(HERE/'build_e2_mod4v1_sources_v3.py');last_correction,last_correction_ref=read(HERE/'finalize_e2_launcher_reader_v4.py');refs.extend([previous_ref,last_correction_ref])"
assert a in s;s=s.replace(a,a+"\n    prior4,prior4_ref=read(HERE/'build_e2_mod4v1_sources_v4.py');line_endings,line_endings_ref=read(HERE/'finalize_e2_utf8_line_endings_v5.py');refs.extend([prior4_ref,line_endings_ref])")
ast.parse(s)
new=HERE/'build_e2_mod4v1_sources_v5.py'
with new.open('x',encoding='utf-8') as f:f.write(s)
print(json.dumps({'generator':str(new),'raw_original_SHA_retained':True,'PT_SDK_or_training':False},indent=2))
