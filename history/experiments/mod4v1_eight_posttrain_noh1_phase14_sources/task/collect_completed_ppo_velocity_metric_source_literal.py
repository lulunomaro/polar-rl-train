"""Source-only provenance for ownPPO scalarvelocity_tracking_success_rate. Exactinstalled .pyfiles only."""
from pathlib import Path
import json,shlex
from project_connector import connect72
R=Path(__file__).resolve().parent;D=R/'diagnostics/W35_RESUME82_SCALAR_EMITTER_SOURCE_V1';assert not D.exists();D.mkdir();B='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4V1_W35_RESUME89ACA_WAIT_V4_20261102_054158_1793569318385718000';code="""from pathlib import Path
import json,hashlib
B=Path(%r);manifest=json.loads((B/'INSTALL_MOD4V1_ACTUAL.json').read_bytes());rows=[];scanned=0
for row in manifest['files']:
 rel=row['relative']
 if not rel.endswith('.py'):continue
 p=B/rel;raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==row['SHA'];scanned+=1;text=raw.decode('utf-8')
 if 'velocity_tracking_success_rate'in text:rows.append({'relative':rel,'bytes':len(raw),'SHA':row['SHA'],'literal_lines':[{'line':i+1,'text':l}for i,l in enumerate(text.splitlines())if 'velocity_tracking_success_rate'in l],'full_original_source':text})
print(json.dumps({'kind':'OWN_COMPLETED_PPO_INSTALLED_SOURCE_ONLY_METRIC_PROVENANCE','scanned_installed_PY':scanned,'matches':rows,'PT_raw_SDK_canonical_access':False}))
"""%B
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=120);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(text)
finally:c.close()
for row in v['matches']:
 p=D/row['relative'];p.parent.mkdir(parents=True,exist_ok=True);p.write_text(row.pop('full_original_source'),encoding='utf-8');row['local_copy']=str(p)
(D/'SOURCE_READ_RECEIPT.json').write_text(json.dumps(v,indent=2),encoding='utf-8');print(json.dumps(v,indent=2))
