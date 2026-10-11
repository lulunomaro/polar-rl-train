"""Prepare only new read-only 139 readers; retain exact 132/115/129 contracts."""
from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
H=lambda b:hashlib.sha256(b).hexdigest()
def main():
 old=W/'MOD4_E1_CURB20_FULL_STATE_PREPARE_20261011'
 collector=(old/'collect_formal_reviewed_curb133_actual.py').read_text(encoding='utf8')
 header="""from pathlib import Path
import sys
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
sys.path.insert(0,str(D));from stage_dispatch_seed_reviewed_once import NEW,save
sys.path.insert(0,str(W/'MOD4_E1_CURB20_ENTRY_REPAIR_20261011'));import repair_io as io
E,B,connect_both,cleanup,H=io.E,io.B,io.connect_both,io.cleanup,io.H
sys.path.insert(0,str(W/'MOD4_E1_SLOPE5_INDEPENDENT_PREPARE_20261011'))
from slope8_worker_actual import worker_actual
from curb_io import WIN
"""
 collector=collector.replace("from stage_formal_dispatch_reviewed_once import D,R,E,B,NEW,connect_both,cleanup,save,H\nfrom curb_io import WIN\nfrom publish_curb132_frozen_once import worker_actual\n",header)
 collector=collector.replace('CURB133','CURB139').replace('curb133','curb139').replace('e1_CURB20_independent_observation_PASSED.json','e1_CURB20_entry_repair_observation_PASSED.json')
 reviewer=(old/'review_formal_reviewed_curb133_schema_actual.py').read_text(encoding='utf8')
 reviewer=reviewer.replace('from stage_formal_dispatch_reviewed_once import D,R,save',"from pathlib import Path\nimport sys\nD=Path(__file__).resolve().parent;R=D/'reports'\nsys.path.insert(0,str(D));from stage_dispatch_seed_reviewed_once import save\nsys.path.insert(0,str(D.parent/'MOD4_E1_CURB20_INDEPENDENT_PREPARE_20261011'))")
 reviewer=reviewer.replace('CURB133','CURB139').replace('curb133','curb139')
 outputs={'collect_entry139_actual.py':collector,'review_entry139_schema_actual.py':reviewer}
 for name,text in outputs.items():
  p=D/name;assert not p.exists(),p;ast.parse(text);p.write_text(text,encoding='utf8')
 p=R/'ENTRY139_READERS_PREPARED.json';assert not p.exists()
 p.write_text(json.dumps(dict(epoch=time.time(),new_readonly_readers={name:H((D/name).read_bytes()) for name in outputs},origin_contracts=132,retention_contracts=[115,129],current_worker_actual_namespace='E1_SLOPE8_QUERY_REVIEW',no_GPU_queue_or_canonical_write=True),indent=2),encoding='utf8')
 print(json.dumps(dict(prepared=list(outputs),read_only=True)))
if __name__=='__main__':main()
