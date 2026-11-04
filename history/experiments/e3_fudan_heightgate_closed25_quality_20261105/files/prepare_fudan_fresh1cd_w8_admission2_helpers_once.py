"""Namespace-only new admission after CLOSED zero-GO W7; no worker/owner/core changes."""
from pathlib import Path
import ast
D=Path(__file__).resolve().parent
pairs=(('prepare_stage_fudan_fresh1cd_w7_once.py','prepare_stage_fudan_fresh1cd_w8_admission2_once.py'),('dispatch_fudan_fresh1cd_w7_original_owner_once.py','dispatch_fudan_fresh1cd_w8_admission2_original_owner_once.py'),('collect_fudan_fresh1cd_w7_window_once.py','collect_fudan_fresh1cd_w8_admission2_window_once.py'))
assert all(not(D/new).exists()for old,new in pairs)
guard='''previous_admission=json.loads((D/'reports/FDN_N20000_W7_FRESH1CD_20261105_005713/CLOSED_RESULT.json').read_bytes());am=previous_admission['metadata'];ae=am['OWNER_EXIT_ACTUAL.json'];ao=am['OUTER_OWNER_WAIT_ACTUAL.json']
assert previous_admission['closed']is True and all(ae[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and ao['actual_wait_returncode']==0 and ao['original_owner_reaped']is True and ao['controller_pid']==1625502 and ao['original_owner_pid']==1625509
assert am['COHORT_FINAL.json']is None and all(v is None for k,v in am.items()if k.startswith('FDN_'))and 'Original preGOresourcewait1800expired'in json.dumps(ae['errors'])
'''
results=[]
for old,new in pairs:
 s=(D/old).read_text(encoding='utf8').replace('FDN_N20000_W7_FRESH1CD_','FDN_N20000_W8_FRESH1CD_ADMISSION2_').replace('native_payload_v7_n20000_fresh1cd_25','native_payload_v8_n20000_fresh1cd25_admission2').replace('FRESH1CD25_W7_','FRESH1CD25_W8_ADMISSION2_')
 if old.startswith('prepare_'):
  a="prior=json.loads((D/'reports/FDN_N20000_W6_TIMEOUT8_20261104_231152/CLOSED_RESULT.json').read_bytes());assert prior['closed']is True";assert s.count(a)==1;s=s.replace(a,guard+a)
 ast.parse(s);compile(s,new,'exec');results.append((new,s))
for name,s in results:(D/name).write_text(s,encoding='utf8',newline='\n')
print('Prepared3 new namespaces; W7 closed/zero-GO frontdoor before mkdir/SSH; source-only AST; original worker/owner/core/resource gates unchanged')
