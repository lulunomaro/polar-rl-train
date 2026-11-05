"""Prepare same finite config under a new purpose after actual original zero-GO expiry."""
from pathlib import Path
import ast,json
D=Path(__file__).resolve().parent
closed=D/'reports/FDN_N20000_W10_LOWSTD005_20261105_041929/CLOSED_RESULT.json';v=json.loads(closed.read_bytes());m=v['metadata'];e=m['OWNER_EXIT_ACTUAL.json'];o=m['OUTER_OWNER_WAIT_ACTUAL.json']
assert v['closed']is True and all(e[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and o['original_owner_reaped']is True and o['actual_wait_returncode']==0 and o['original_owner_pid']==1633596 and o['controller_pid']==1633589
assert m['COHORT_FINAL.json']is None and all(value is None for key,value in m.items()if key.startswith('FDN_'))and 'Original preGOresourcewait1800expired'in json.dumps(e['errors'])
newnames=('prepare_stage_fudan_lowstd005_w11_admission2_once.py','dispatch_fudan_lowstd005_w11_admission2_original_owner_once.py','collect_fudan_lowstd005_w11_admission2_window_once.py','freeze_fudan_lowstd005_w11_first_real_metadata_once.py','publish_fudan_lowstd005_admission2_closed_quality_once.py');assert all(not(D/n).exists()for n in newnames)
def namespace(s):return s.replace('FDN_N20000_W10_LOWSTD005_','FDN_N20000_W11_LOWSTD005_ADMISSION2_').replace('native_payload_v10_lowstd00525','native_payload_v11_lowstd00525_admission2').replace('FRESH1CD25_LOWSTD005_W10_','FRESH1CD25_LOWSTD005_W11_ADMISSION2_')
s=(D/'prepare_stage_fudan_lowstd005_w10_once.py').read_text(encoding='utf8');a=s.index('previous=json.loads(');b=s.index('source=dict(',a)
guard="""previous_admission=json.loads((D/'reports/FDN_N20000_W10_LOWSTD005_20261105_041929/CLOSED_RESULT.json').read_bytes());z=previous_admission['metadata'];e=z['OWNER_EXIT_ACTUAL.json'];o=z['OUTER_OWNER_WAIT_ACTUAL.json']
assert previous_admission['closed']is True and all(e[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and o['original_owner_reaped']is True and o['actual_wait_returncode']==0 and o['original_owner_pid']==1633596 and o['controller_pid']==1633589
assert z['COHORT_FINAL.json']is None and all(value is None for key,value in z.items()if key.startswith('FDN_'))and 'Original preGOresourcewait1800expired'in json.dumps(e['errors'])
"""
s=s[:a]+'__CLOSED_W10_GUARD__\n'+s[b:];s=namespace(s).replace('__CLOSED_W10_GUARD__\n',guard);files={D/newnames[0]:s}
for old,new in(('dispatch_fudan_lowstd005_w10_original_owner_once.py',newnames[1]),('collect_fudan_lowstd005_w10_window_once.py',newnames[2]),('freeze_fudan_lowstd005_w10_first_real_metadata_once.py',newnames[3])):files[D/new]=namespace((D/old).read_text(encoding='utf8'))
s=namespace((D/'publish_fudan_lowstd005_closed_quality_once.py').read_text(encoding='utf8')).replace('FDN_LOWSTD005_CLOSED_','FDN_LOWSTD005_ADMISSION2_CLOSED_').replace('CURRENT_PROGRESS_V21_LOWSTD005_CLOSED_QUALITY_RESULT','CURRENT_PROGRESS_V22_LOWSTD005_ADMISSION2_CLOSED_QUALITY_RESULT').replace('# V21 — lowSTD005有限25真实质量结果','# V22 — lowSTD005 Admission2有限25真实质量结果').replace('- W10 root','- W11 Admission2 root');files[D/newnames[4]]=s
for path,s in files.items():ast.parse(s);compile(s,str(path),'exec')
for path,s in files.items():path.write_text(s,encoding='utf8',newline='\n')
print('Prepared same lowSTD005 fresh1cd config under new W11 admission2 namespace after true zero-GO W10 closure; one AST; original worker/core/owner/physics/resources unchanged; no SSH/models/SDK/GO/C')
