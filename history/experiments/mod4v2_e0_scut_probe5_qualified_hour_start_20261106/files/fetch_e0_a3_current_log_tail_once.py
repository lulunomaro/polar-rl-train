"""Read only the current E0 purpose's bounded live stdout tail; no model/canonical/GPU/process action."""
from pathlib import Path
import json,sys
D=Path(__file__).resolve().parent;p=D/'E0_A3_CURRENT_TRAINING_LOG_TAIL.txt';assert not p.exists();pointer=json.loads((D/'COLLECT_E0_SINGLE_ADMISSION3_ONCE.json').read_bytes());v=json.loads((Path(pointer['output'])/'LATEST_METADATA.json').read_bytes());assert v['root']==pointer['root'] and v['cases']['E0']['V2_NATIVE_INITIALIZED.json']is not None and v['cases']['E0']['V2_LEARNER_LOADED.json']is not None;sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72();s=c.open_sftp()
try:
 with s.open(v['root']+'/roles/E0/PPO_FULL_STDOUT_STDERR.log','rb')as f:n=f.stat().st_size;f.seek(max(0,n-16000));raw=f.read()
 p.write_bytes(raw);text=raw.decode('utf8',errors='replace');print(json.dumps(dict(path=str(p),own_current_purpose_only=True,last_lines=text.splitlines()[-38:],source_model_raw_canonical_GPU_foreign_operations=0),indent=2))
finally:s.close();c.close()
