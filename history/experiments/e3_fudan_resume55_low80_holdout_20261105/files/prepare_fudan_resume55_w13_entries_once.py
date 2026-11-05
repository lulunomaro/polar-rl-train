"""Prepare one finite full-learner continuation; no selected-model or remote operations."""
from pathlib import Path
import ast,json,hashlib
D=Path(__file__).resolve().parent;N=D/'source_fudan_native_worker_v9_resume55';names=['prepare_stage_fudan_resume55_w13_once.py','dispatch_fudan_resume55_w13_original_owner_once.py','collect_fudan_resume55_w13_window_once.py'];assert all(not(D/n).exists()for n in names)
H=lambda x:hashlib.sha256(x).hexdigest();worker=(N/'worker_fudan_sequence_ppo_native_v1.py').read_bytes();helper=(N/'retained_learner_source_v1.py').read_bytes()
for raw in(worker,helper):ast.parse(raw.decode('utf8'))
s=(D/'prepare_stage_fudan_timeout8_w6_once.py').read_text(encoding='utf8')
for a,b in [('native_payload_v6_n20000_timeout8','native_payload_v13_resume55_continue25'),('source_fudan_native_worker_v4_20k_timeout8','source_fudan_native_worker_v9_resume55'),('FDN_N20000_W6_TIMEOUT8_','FDN_N20000_W13_RESUME55_'),('source_original_owner_v4_20k_timeout8','source_original_owner_v9_resume55'),('stage_fudan_nonpt_v4_20k_timeout8.py','stage_fudan_nonpt_v9_resume55.py'),('source_task_runtime_v2_lowtimeout8','source_task_runtime_v4_passive_lowstd'),('MOD4V1_E3_FUDAN_N20000_LOWTIMEOUT8_CONTINUE133_W6_','MOD4V1_E3_FUDAN_N20000_FULLRESUME55_CONTINUE25_W13_')]:s=s.replace(a,b)
a=s.index('prior=json.loads(');b=s.index('assert N.is_dir()',a)
s=s[:a]+'''prior=json.loads((D/'reports/FDN_N20000_W12_LRSCHEDULE001_20261105_065807/CLOSED_RESULT.json').read_bytes());assert prior['closed']is True
m=prior['metadata'];x=m['OWNER_EXIT_ACTUAL.json'];outer=m['OUTER_OWNER_WAIT_ACTUAL.json'];f=m['FDN_FINAL.json'];latest=m['FDN_LATEST_COMPLETE_SAVE.json'];qualification=m['FDN_PARENT_WAIT_QUALIFICATION.json']
assert x['errors']==[]and all(x[k]is True for k in('all_own_children_waited','original_cost_settled','original_leases_released'))and outer['actual_wait_returncode']==0 and outer['original_owner_reaped']is True and outer['original_owner_pid']==1639591 and outer['controller_pid']==1639584
assert qualification['qualified']is True and all(v is True for v in qualification['checks'].values())and latest==f['latest_complete_save']and latest['sha256']=='55afa784423b5af3d3e3300932628d4d213756c3d2b6c4edaaba2e66b1aaabd7'and latest['bytes']==146247985
assert f['version']==7 and f['counters']==dict(updates=25,policy_optimizer_steps=500,encoder_optimizer_steps=500,transitions_seen=24000000)and f['native_counters']['actual_native_policy_steps']==1200
assessment=json.loads((D/'FDN_LOW80_THREESEED_CONFIRMATION_ANALYSIS_V1.json').read_bytes());assert assessment['execution_qualified']is True and assessment['source']['sha256']==latest['sha256']
source=dict(path=latest['path'],sha256=latest['sha256'],bytes=latest['bytes'],run=f['run'],counters=f['counters'],source_envs=20000,actual_native_policy_steps=1200,unoptimized_pending_controls=0,source_training_execution_qualified=True)
overlay=D/'source_task_runtime_v4_passive_lowstd/e3_fudan_task_runtime_v1.py';overlay_raw=overlay.read_bytes();assert len(overlay_raw)==12745 and H(overlay_raw)=='a84823a59731f9cd805aa0bf6a91af10e0e26e729652df39b8cbd17dc6def3f9'
''' +f"assert H((N/'worker_fudan_sequence_ppo_native_v1.py').read_bytes())=={H(worker)!r} and H((N/'retained_learner_source_v1.py').read_bytes())=={H(helper)!r}\n"+s[b:]
p=(D/'dispatch_fudan_lrschedule001_w12_original_owner_once.py').read_text(encoding='utf8').replace('FDN_N20000_W12_LRSCHEDULE001_','FDN_N20000_W13_RESUME55_')
c=(D/'collect_fudan_lrschedule001_w12_window_once.py').read_text(encoding='utf8').replace('FDN_N20000_W12_LRSCHEDULE001_','FDN_N20000_W13_RESUME55_').replace('FDN_SINGLE_SOURCE_NEW_BRANCH_WARM_START.json','FDN_FULL_LEARNER_CONTINUATION_INITIALIZED.json')
for name,text in zip(names,(s,p,c)):
 ast.parse(text);compile(text,name,'exec')
 (D/name).write_text(text,encoding='utf8',newline='\n')
err=D/'FDN_RESUME55_OWNER_BUILDER_V1_LOCAL_ANCHOR_ERRATUM.json';assert not err.exists();err.write_text(json.dumps(dict(error='ValueError substring not found before output publication',source='prepare_fudan_resume55_owner_stage_once.py',failed_line=15,fix='new v2 builder uses observed AST line/column for metadata check replacement',original_source_kept=True,PT_SDK_SSH_GPU_GO_C_operations=0),indent=2),encoding='utf8')
print(json.dumps(dict(source_only=True,worker_SHA=H(worker),helper_SHA=H(helper),new_namespace='FDN_N20000_W13_RESUME55_',actual_N20000_T48_new_update_cap=25,base=dict(updates=25,policy_optimizer_steps=500,encoder_optimizer_steps=500,transitions_seen=24000000),three_entry_AST=True),indent=2))
