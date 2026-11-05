"""Refine the empty-field diagnosis using actual original-owner source schema. Read-only, one call."""
from pathlib import Path
import sys,json,time,shlex
D=Path(__file__).resolve().parent;out=D/'FDN_W2_CANONICAL_OWNER_SCHEMA_REFINEMENT_V2.json';assert not out.exists();sys.path.insert(0,str(D.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
code='''from pathlib import Path
import json,time
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');v=json.loads(p.read_bytes());a=v['active_segment'];owner=None if a is None else {k:a[k] for k in('owner_run_id','owner_parent_pid','started_epoch','ended_epoch') if k in a};print(json.dumps(dict(epoch=time.time(),authority_generation=v['authority_generation'],active_segment_owner=owner,remaining_training_seconds=v['remaining_training_seconds'],charged_training_seconds=v['charged_training_seconds'],read_only=True,canonical_bytes_copied_or_written=False,foreign_locks_or_signals=0)))
'''
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();a=o.read().decode();b=e.read().decode();rc=o.channel.recv_exit_status();v=dict(epoch=time.time(),returncode=rc,stdout=a,stderr=b,prior_whitelist_returned_empty_object_not_no_owner_evidence=True,actual_schema_source='source_original_owner_v2/fudan_original_owner_v1.py:18,43,64',no_GPU_query_or_model_reads_repeated=True);out.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(v,indent=2));assert rc==0,b
finally:c.close()
