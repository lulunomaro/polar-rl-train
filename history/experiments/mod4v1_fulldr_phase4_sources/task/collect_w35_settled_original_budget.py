"""Read numeric accounting receipt for this finished original-owner segment; never copy ledger."""
from pathlib import Path
import json,shlex,datetime
from project_connector import connect72
R=Path(__file__).resolve().parent;d=json.loads(sorted((R/'reports').glob('W35_adaptation_dispatch_*.json'))[-1].read_bytes());run=d['run_id'];job=d['new_job']
code="""from pathlib import Path
import json,hashlib
C=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=C.read_bytes();c=json.loads(raw);run=%r;job=Path(%r)
a=next(v for v in reversed(c['completed_segments'])if v.get('kind','').endswith(run));e=a['experts']['w35_72'];exit=json.loads((job/'OWNER_EXIT_ACTUAL.json').read_bytes());assert exit['original_cost_settled'] and exit['all_own_children_waited'] and e['actual_returncode']==0 and e['duration_bound_passed'];assert abs(c['charged_training_seconds']+c['remaining_training_seconds']-2268000)<1e-5
print(json.dumps({'kind':'ACTUAL_ORIGINAL_W35_MOD4V1_FINITE_SEGMENT_SETTLED_READONLY','canonical_path':str(C),'canonical_SHA':hashlib.sha256(raw).hexdigest(),'generation':c['authority_generation'],'authorized_seconds':c['authorized_training_seconds'],'charged_total_seconds':c['charged_training_seconds'],'remaining_seconds':c['remaining_training_seconds'],'historical_extension_count':c['historical_budget_extension_count'],'new_authority_budget_extensions':c['new_authority_budget_extensions'],'active_current_owner':None if c['active_segment'] is None else {'kind':c['active_segment']['kind'],'pid':c['active_segment']['owner_parent_pid']},'this_segment':{'kind':a['kind'],'owner_pid':a['owner_parent_pid'],'started_epoch':a['started_epoch'],'ended_epoch':a['ended_epoch'],'charged_expert_seconds':a['charged_expert_seconds'],'w35_72':e},'original_owner_exit':exit,'ledger_copied':False,'ledger_writes_by_this_reader':0,'PT_reads':0}))
"""%(run,job)
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();text=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(text)
finally:c.close()
p=R/'reports'/('W35_actual_settled_original_budget_'+datetime.datetime.now().strftime('%Y%m%d_%H%M%S')+'.json');p.write_text(json.dumps(v,ensure_ascii=False,indent=2),encoding='utf-8');print('REPORT',p);print(json.dumps(v,ensure_ascii=False,indent=2))
