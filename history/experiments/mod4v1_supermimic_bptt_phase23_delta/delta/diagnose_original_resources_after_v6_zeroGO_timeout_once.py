"""New resource-release check AFTER V6 actually closed with zero GO.
Reuses only read-only diagnostic code, not its previous once/owner invocation.
"""
from pathlib import Path
import sys,json,ast,shlex
R=Path(__file__).resolve().parent;out=R/'reports/A1_V6_POST_ZERO_GO_TIMEOUT_RESOURCE_RELEASE_V1.json';assert not out.exists();p=json.loads((R/'A1_NATIVE_V6_LATEST_CLOSED_RESULT_PATH.json').read_bytes());closed=json.loads(Path(p['path']).read_bytes());exit=closed['parent_exit'];assert exit and all(exit[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'));assert len(closed['rows'])==8 and all(r['status']=='CLOSED_UNSTARTED'and r.get('actual_GO')is None and r.get('startup')is None and r.get('final')is None for r in closed['rows']);assert'Original preGOresourcewait1800expired'in json.dumps(exit['errors'])
tree=ast.parse((R/'diagnose_v6_actual_original_resource_wait_once.py').read_text(encoding='utf-8'));code=next(ast.literal_eval(n.value)for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='code'for t in n.targets));sys.path.insert(0,str(R.parent/'mod4v1_experts_fulldr_rm70_20261101'));from project_connector import connect72
c=connect72()
try:
 i,o,e=c.exec_command(shlex.quote('/home/lc01/Zonglin Li/zonglin2/run-python.sh')+' -B -c '+shlex.quote(code),timeout=60);i.close();txt=o.read().decode(errors='replace');err=e.read().decode(errors='replace');rc=o.channel.recv_exit_status();value=dict(kind='NEW_READONLY_RESOURCE_RELEASE_PURPOSE_AFTER_ACTUAL_ZERO_GO_TIMEOUT',prior_root=closed['root'],prior_exit=exit,prior_all8_GO_absent=True,prior_actual_model_SDK_BPTT_started=False,returncode=rc,stderr=err,actual=json.loads(txt)if rc==0 else None,stdout_if_error=txt if rc else None)
 if rc==0:value['original_canonical_and_authority_private_locks_observed_clear']=value['actual']['canonical_summary'].get('active_segment')is None and all(not r.get('kernel_records')for r in value['actual']['lock_records']if not r['path'].endswith('finite_environment_validation.lock'))
 out.write_text(json.dumps(value,indent=2),encoding='utf-8');print(json.dumps(value,indent=2));assert rc==0,(rc,err)
finally:c.close()
