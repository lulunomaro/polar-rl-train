"""Finalreadonlyminimaloriginalauthorityreceipt, notnewledger/copy/refund. No model/raw/SDK orforeignsignals."""
from pathlib import Path
import json,sys,shlex
D=Path(__file__).resolve().parent;sys.path.insert(0,str(D.parent));from project_connector import connect72
p=D/'reports/EIGHT_POSTTRAIN_ORIGINAL_FINAL_BUDGET_READONLY_RECEIPT_V1.json';assert not p.exists();runs=[json.loads((D/'PAIR1_V4_STAGE_DISPATCH_RESULT.json').read_bytes()).get('run_id')]
# Actualrunidsfromalreadycollectedclosedproducercohorts, nothardcodedstaleC.
runs=[]
for n in range(1,5):
 path=D/('PAIR1_V4_LATEST_CLOSED_RESULT_PATH.json'if n==1 else'PAIR'+str(n)+'_GENERIC_V2_LATEST_CLOSED_RESULT_PATH.json');closed=json.loads(Path(json.loads(path.read_bytes())['path']).read_bytes());runs.append(closed['root'].rsplit('/',1)[1])
code="""from pathlib import Path
import json,time,hashlib
p=Path('/home/lc01/Zonglin Li/zonglin2/state/mod4_single_canonical_authority_20261026/TRAINING_BUDGET_10H.json');raw=p.read_bytes();c=json.loads(raw);runs=set(%r);active=c['active_segment'];own_active=active is not None and(active.get('owner_run_id')in runs or active.get('run_id')in runs);assert not own_active,'Ownsegmentmustbesettledbeforegoalcompletion';assert c['authority_generation']=='MOD4_SINGLE_WRITER72_20261026'and c['charged_training_seconds']+c['remaining_training_seconds']==2268000.0
rows=[]
for x in c['completed_segments']:
 if x.get('owner_run_id',x.get('run_id'))in runs:rows.append({'run_id':x.get('owner_run_id',x.get('run_id')),'owner_parent_pid':x.get('owner_parent_pid'),'ended_epoch':x.get('ended_epoch')})
assert {x['run_id']for x in rows}==runs,'AllfouroriginalsegmentscompleteintheoriginalC'
print(json.dumps({'kind':'ORIGINAL_AUTHORITY_FINAL_MINIMAL_READONLY_RECEIPT_NOT_NEW_LEDGER','epoch':time.time(),'path':str(p),'SHA':hashlib.sha256(raw).hexdigest(),'authority_generation':c['authority_generation'],'charged_training_seconds':c['charged_training_seconds'],'remaining_training_seconds':c['remaining_training_seconds'],'charged_plus_remaining':c['charged_training_seconds']+c['remaining_training_seconds'],'strict_reserve_seconds':c['finite_minimum_remaining_seconds'],'own_active_segment_absent':not own_active,'other_current_owner':None if active is None else{'pid':active.get('owner_parent_pid',active.get('pid')),'kind':active.get('kind')},'allfour_own_original_segments_completed':rows,'canonical_writes_models_SDK_signals_or_new_budget':0}))
"""%runs;c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();txt=o.read().decode();err=e.read().decode();rc=o.channel.recv_exit_status();assert rc==0,(rc,err);v=json.loads(txt);p.write_text(json.dumps(v,indent=2),encoding='utf-8');print(p);print(json.dumps(v,indent=2))
finally:c.close()
