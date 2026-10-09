"""Preserve pre-commit capture rejection, decode retained Windows log losslessly, finish once."""
from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';p=R/'returned_rejection/probe.log';raw=p.read_bytes()
assert hashlib.sha256(raw).hexdigest()=='93ee4e4517e2bc4736c774e3d2c8fd571a459ab7cd6dd9259a60586726f7a577'
decoded=raw.decode('gb18030');assert decoded.encode('gb18030')==raw
(R/'ARCHIVE_CAPTURE_UTF8_REJECTION.json').write_text(json.dumps(dict(epoch=time.time(),trial_id='E1-G1-ARCHIVE-CAPTURE-UTF8-REJECT-01',phase='capture_before_record_experiment_or_Git_commit',path=str(p.resolve()),bytes=len(raw),original_sha256=hashlib.sha256(raw).hexdigest(),error="UnicodeDecodeError utf8 byte0xa1 at1018; original Windows probe.log retained",lossless_GB18030_roundtrip_verified=True,original_bytes_not_modified=True,no_GPU_PPO_or_canonical_mutation=True),indent=2),encoding='utf8')
s=(D/'record_postwindow_route_repair_once.py').read_text(encoding='utf8')
s=s.replace("assert not (R/'ARCHIVE_STARTED.json').exists() and not git('diff','--cached','--name-only')","assert (R/'ARCHIVE_STARTED.json').exists() and not (R/'ARCHIVE_UTF8_FINISH_STARTED.json').exists() and not git('diff','--cached','--name-only')\n assert not git('tag','--list','trial-20261010-'+ID)")
s=s.replace("(R/'ARCHIVE_STARTED.json').write_text","(R/'ARCHIVE_UTF8_FINISH_STARTED.json').write_text").replace("assert not dest.exists();dest.mkdir(parents=True)","assert dest.exists()")
bad="  text,n=redact(raw.decode('utf8'));raw=text.encode();out=dest/rel;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)"
fix="""  enc='utf8'
  try:decoded=raw.decode('utf8')
  except UnicodeDecodeError:
   decoded=raw.decode('gb18030');assert decoded.encode('gb18030')==raw;enc='gb18030_lossless_roundtrip'
  text,n=redact(decoded);raw=text.encode();out=dest/rel;out.parent.mkdir(parents=True,exist_ok=True)
  if out.exists():assert out.read_bytes()==raw,('Existing partial capture differs',out)
  else:out.write_bytes(raw)"""
assert s.count(bad)==1;s=s.replace(bad,fix).replace("capture='redacted_full' if n else 'byteexact_full',redactions=n","capture='redacted_full' if n else ('byteexact_full' if enc=='utf8' else 'lossless_transcoded_UTF8_full'),original_encoding=enc,redactions=n")
# The original MONITOR_VERIFIED is already in partial capture; preserve it rather than rewrite epoch.
start=s.index(" (R/'MONITOR_VERIFIED.json').write_text");end=s.index(" (R/'ARCHIVE_UTF8_FINISH_STARTED.json')",start)
s=s[:start]+" assert (R/'MONITOR_VERIFIED.json').exists()\n"+s[end:]
ast.parse(s);out=D/'record_postwindow_route_repair_utf8_continuation_once.py';assert not out.exists();out.write_text(s,encoding='utf8')
