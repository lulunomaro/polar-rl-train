"""Genuinely new original admission after fully closed ZERO-GO W13; never replay expired parent."""
from pathlib import Path
import ast,json
D=Path(__file__).resolve().parent;closed=D/'reports/FDN_N20000_W13_RESUME55_20261105_091611/CLOSED_RESULT.json';v=json.loads(closed.read_bytes());m=v['metadata'];end=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];assert v['closed']is True and all(end[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and outer['original_owner_reaped']is True and outer['actual_wait_returncode']==0 and outer['controller_pid']==1645903 and outer['original_owner_pid']==1645910 and m['COHORT_FINAL.json']is None and all(x is None for k,x in m.items()if k.startswith('FDN_'))and 'Original preGOresourcewait1800expired'in json.dumps(end['errors'])
old='FDN_N20000_W13_RESUME55_';new='FDN_N20000_W14_RESUME55_ADMISSION2_';pairs=[('prepare_stage_fudan_resume55_w13_once.py','prepare_stage_fudan_resume55_w14_admission2_once.py'),('dispatch_fudan_resume55_w13_original_owner_once.py','dispatch_fudan_resume55_w14_admission2_original_owner_once.py'),('collect_fudan_resume55_w13_window_once.py','collect_fudan_resume55_w14_admission2_window_once.py'),('run_fudan_resume55_w13_handoff_once.py','run_fudan_resume55_w14_admission2_handoff_once.py'),('publish_fudan_resume55_closed_quality_once.py','publish_fudan_resume55_admission2_closed_quality_once.py'),('freeze_fudan_resume55_w13_first_real_metadata_once.py','freeze_fudan_resume55_w14_admission2_first_real_metadata_once.py')]
assert all(not(D/b).exists()for a,b in pairs)
guard="""zero=json.loads((D/'reports/FDN_N20000_W13_RESUME55_20261105_091611/CLOSED_RESULT.json').read_bytes());zm=zero['metadata'];ze=zm['OWNER_EXIT_ACTUAL.json'];zo=zm['OUTER_OWNER_WAIT_ACTUAL.json']
assert zero['closed']is True and all(ze[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and zo['original_owner_reaped']is True and zo['actual_wait_returncode']==0 and zo['controller_pid']==1645903 and zo['original_owner_pid']==1645910 and zm['COHORT_FINAL.json']is None and all(x is None for k,x in zm.items()if k.startswith('FDN_'))and 'Original preGOresourcewait1800expired'in json.dumps(ze['errors'])
"""
texts=[]
for a,b in pairs:
 s=(D/a).read_text(encoding='utf8').replace(old,new).replace('FDN_RESUME55_W13_','FDN_RESUME55_W14_ADMISSION2_').replace('native_payload_v13_resume55_continue25','native_payload_v14_resume55_admission2').replace('MOD4V1_E3_FUDAN_N20000_FULLRESUME55_CONTINUE25_W13_','MOD4V1_E3_FUDAN_N20000_FULLRESUME55_CONTINUE25_W14_ADMISSION2_')
 for x,y in pairs:s=s.replace(x,y)
 if a.startswith('prepare_stage_'):
  i=s.index('prior=json.loads(');s=s[:i]+guard+s[i:]
 ast.parse(s);compile(s,b,'exec');texts.append(s)
watch=(D/'watch_original_authority_after_lowstd005_w10_once.py').read_text(encoding='utf8').replace('LOWSTD005_W10','RESUME55_W13').replace('FDN_N20000_W10_LOWSTD005_20261105_041929','FDN_N20000_W13_RESUME55_20261105_091611').replace('1633596','1645910').replace('1633589','1645903').replace('zero-GO W10','zero-GO W13');watchname='watch_original_authority_after_resume55_w13_once.py';assert not(D/watchname).exists();ast.parse(watch);compile(watch,watchname,'exec')
for (_,b),s in zip(pairs,texts):(D/b).write_text(s,encoding='utf8',newline='\n')
(D/watchname).write_text(watch,encoding='utf8',newline='\n')
print('Seven NEW source entries prepared; strong W13 zero-GO/null-FDN/actual-wait-release frontdoor; unchanged policy, owner/account/lease; no stage/dispatch/SDK/model/C operations')
