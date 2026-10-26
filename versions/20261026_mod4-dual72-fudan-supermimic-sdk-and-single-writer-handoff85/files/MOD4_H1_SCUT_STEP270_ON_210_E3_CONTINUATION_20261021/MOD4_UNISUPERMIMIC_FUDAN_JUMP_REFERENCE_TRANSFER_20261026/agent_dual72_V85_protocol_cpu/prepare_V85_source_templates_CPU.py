"""Generate new source templates only. Never runs a binder or any live script."""
from pathlib import Path
import ast
import copy
import difflib
import hashlib
import json
import time

HERE=Path(__file__).resolve().parent;J=HERE.parent;T=J.parent
OLD=T/'H1_STEP270_MIXED_FUDAN_SUPERMIMIC_RESOURCE_V84_20261026'
STAGE='H1_STEP270_DUAL72_FUDAN_SUPERMIMIC_E3_RESOURCE_V85_20261026'
NS='H1step270_dual72_fudan_supermimic_E3_2610v85'
snap=HERE/'source_snapshots';snap.mkdir();diffs=HERE/'diffs';diffs.mkdir();(HERE/'reports').mkdir()
index=[]


def read_source(path,label):
    raw=path.read_bytes()
    with (snap/label).open('xb') as stream:stream.write(raw)
    index.append(dict(path=str(path),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),snapshot=str(snap/label)))
    return raw.decode('utf8').replace('\r\n','\n')


def write(name,text,old=None):
    ast.parse(text);path=HERE/name;path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('x',encoding='utf8') as stream:stream.write(text)
    if old is not None:
        with (diffs/(name.replace('/','_')+'.diff')).open('x',encoding='utf8') as stream:
            stream.write(''.join(difflib.unified_diff(old.splitlines(True),text.splitlines(True),fromfile='reviewed84',tofile=name)))


for name in ('three_slot_common_v1.py','three_slot_finite_node_v1.py','three_real_gpu_resource_v1.py','forwarded_original_owner_control_v1.py','mixed84_protocol_v1.py'):
    source=read_source(OLD/'controllers'/name,'84_controller_'+name)
    # Preserve exact bytes for unchanged control/network/common sources.
    path=HERE/'controllers'/name;path.parent.mkdir(exist_ok=True)
    with path.open('xb') as stream:stream.write((OLD/'controllers'/name).read_bytes())
owner=read_source(OLD/'controllers/three_slot_finite_owner_v1.py','84_owner.py')
new=owner.replace("set(specs)=={'h1','e2','recovery'}","set(specs)=={'e2','recovery'}",1).replace("cfg['deferred_experts']==[]","cfg['deferred_experts']==['h1']",1)
needle="c['remaining_training_seconds']>sum(b.CAPS[k] for k in specs)+9400.860692501068+512+64800"
assert new.count(needle)==1
new=new.replace(needle,"c['remaining_training_seconds']>max(86412.86069250107,sum(b.CAPS[k] for k in specs)+9400.860692501068+512+64800)",1)
write('controllers/three_slot_finite_owner_V85_pair_source_only.py',new,owner)

installer=read_source(OLD/'e2_healthy83B_physical_resource_install84_TEMPLATE.py','84_e2_installer.py')
remote=ast.literal_eval(next(n.value for n in ast.parse(installer).body if isinstance(n,ast.Assign)))
loop=remote[remote.index("for row in v['manifest']['files']:"):remote.index('\nprint(json.dumps(',remote.index("for row in v['manifest']['files']:"))]
prefix=f'''from pathlib import Path
import fcntl,json,os,psutil,shutil,subprocess,time
B=Path(v['root']);s=v['spec'];key=s['key'];old=Path(s['previous_runtime_root']);owned=Path('/home/lc01/Zonglin Li/zonglin2')
assert key in ('e2','recovery') and s['execution_backend']=='target72' and not s.get('cross_host_qualified_source')
expected={{'e2':'GPU-16828f91-2b45-b646-8dc0-9481138e2842','recovery':'GPU-c27eecbd-6838-7290-1cd2-37e34522213d'}};assert s['GPU_UUID']==expected[key]
assert str(B)==str(owned/'tasks/{NS}'/key) and str(old)==str(owned/'tasks/H1step270_three_experts_2610v83b'/key) and B.resolve().is_relative_to(owned.resolve())
proof=v['closedproof'];assert proof['passed'] and set(proof['models'])=={{'h1','e2','recovery'}} and proof['all_owner_nodes_children_actual_out'] and proof['original_canonical_cost_settled'] and proof['all_original_private_shared_locks_free']
assert proof['remaining_actual_snapshot']==595256.8240613937 and abs(proof['actual_cost_sumonce']-10943.796510219574)<1e-5
assert all(x['actual_cost']['duration_bound_passed'] for x in proof['models'].values()) and abs(proof['actual_cost_sumonce']-sum(x['actual_cost']['charged_seconds'] for x in proof['models'].values()))<1e-5
if key=='e2':
 assert s['finite_method_test'] and s['h1_step270_method_test'] and s['source_Adamstep']==829700 and s['source_SHA']==proof['models']['h1']['final']['SHA']=='8bb9869ac683550c1e7be1c9dffae9a5eac022e0de0fc8f251cd2005cfa6d4c6'
 assert proof['models']['e2']['Adam']==857460 and proof['models']['e2']['final']['SHA']=='72f4cbefeb5bf02af6f39a9d2922faa8032e36e81cb9a142df45154158998c9f'
else:
 assert not s.get('finite_method_test') and s['policy_hz']==50 and s['source_Adamstep']==860800 and s['source_SHA']==proof['models']['recovery']['final']['SHA']=='68d95156fc5dd294e43b21ad39691da8f1df1c5b85667db3001335796521ea49'
e=json.loads((old/'NODE_EXIT_ACTUAL.json').read_bytes());r=json.loads((old/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row']
assert e['actual_all_own_children_waited'] and e['validation_fcntl_released_if_acquired'] and r['terminal_all_own_children_waited'] and r['returncode']==0 and not r['original_error'] and not r['errors'] and r['final']['passed'] and r['final']['final']['SHA']==proof['models'][key]['final']['SHA']
assert not any(p.pid!=os.getpid() and any(a.startswith(str(old)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))
for path in (Path(s['private_lock']),owned/'state/finite_environment_validation.lock'):
 with path.open('rb+') as stream:fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(stream,fcntl.LOCK_UN)
assert psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True);assert not any(s['GPU_UUID'] in line for line in compute.splitlines())
line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if s['GPU_UUID'] in x);assert int(line.split(',')[-1])>(15669 if key=='e2' else 7000)
assert not B.exists();B.mkdir(parents=True);before={{r['relative']:r for r in json.loads((old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())['files']}};need=[];copied=0
'''
code=prefix+loop+"\nassert shutil.disk_usage(B).free>25*1024**3\nprint(json.dumps(dict(epoch=time.time(),root=str(B),need_upload=need,source_files_reused=copied,GPU_line=line,durable_free=shutil.disk_usage(owned).free,source_cost_proof_historical83B_only=True,original_live_account_checked=False,no_owner_or_GO=True)))\n"
ast.parse(code)
write('dual72_V85_resource_install_source_v1.py','"""72-only resource/copy code; no canonical/210/owner/GO calls."""\nCODE='+repr(code)+'\n')

helper=read_source(OLD/'DEPLOYER_REUSED_H1_HELPER_84_EXACT_SOURCE_TEMPLATE.py','84_deployer_helper.py')
write('DEPLOYER_REUSED_H1_HELPER_85_EXACT_SOURCE_TEMPLATE.py',helper)

# Full deployer is gated separately and still uses the original210 authority.
deploy=read_source(OLD/'deploy_mixed84_original_writer_TEMPLATE.py','84_deployer.py')
new=deploy.replace(OLD.name,STAGE).replace('DEPLOYER_REUSED_H1_HELPER_84_EXACT_SOURCE','DEPLOYER_REUSED_H1_HELPER_85_EXACT_SOURCE')
new=new.replace("set(q['specs'])=={'h1','e2','recovery'}","set(q['specs'])=={'e2','recovery'} and q['deferred_experts']==['h1']",1)
new=new.replace("q['preparation_scope']=='SOURCE_PREPARED_NOT_TARGET_ADMITTED'","q['preparation_scope']=='SOURCE_PREPARED_PAIR_NOT_LIVE_ACCOUNT_ADMITTED'",1)
new=new.replace("if source==d.INSTALL and args['spec']['key']=='e2':","if source==d.INSTALL and args['spec']['key'] in ('e2','recovery'):",1)
new=new.replace("args['root']==q['roots']['e2']\n   from e2_healthy83B_physical_resource_install84_TEMPLATE import CODE","args['root']==q['roots'][args['spec']['key']]\n   from dual72_V85_resource_install_source_v1 import CODE",1)
new=new.replace("c=route.connect();m.install_h1(c,q)","c=route.connect()",1)
new=new.replace("deferred_experts=[],run_id='THREE4090_EXPERT_ORIGINAL_'","deferred_experts=['h1'],run_id='DUAL72_NATIVE_H1_E3_ORIGINAL_V85_'",1)
new=new.replace("'three_slot_finite_owner_v1.py'","'three_slot_finite_owner_V85_pair_source_only.py'")
new=new.replace("/three_slot_finite_owner_v1.py","/three_slot_finite_owner_V85_pair_source_only.py")
oldline="  nodes=dict(h1=d.launch(c,route.PY,q['roots']['h1'],'three_slot_finite_node_v1.py',dict(q['specs']['h1'],role='node',run_id=cfg['run_id'],token=cfg['token'])));c.close();c=None"
assert new.count(oldline)==1
new=new.replace(oldline,"  nodes={};c.close();c=None",1)
new=new.replace("'THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json'","'DUAL72_V85_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json'")
write('deploy_dual72_V85_original210_writer_UNUSED.py',new,deploy)

# First observer: keep72 native/E3 checks (including corrected payload import
# resolution), replace source210 H1 GPU branch by CPU owner/account checks only.
observer=read_source(J/'agent_root_integration_review_cpu/observe_mixed84_baselines_native_first_finite_V2_UNUSED.py','84_observer_V2.py')
outer=ast.parse(observer);node=next(n for n in outer.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='READ210' for t in n.targets))
owner_read='''from pathlib import Path
import json,psutil,time
B=Path(v['owner']['root']);p=psutil.Process(v['owner']['pid']);assert p.create_time()==v['owner']['creation'] and p.cmdline()==v['owner']['argv'];until=time.monotonic()+900
while True:
 current=json.loads((B/'OWNER_CURRENT.json').read_bytes());rows=current['rows'];go=current['go']
 if all(go.get(k) and (rows.get(k,{}).get('latest_save') or {}).get('updates',0)>0 for k in ('e2','recovery')):break
 assert not any(x.get('original_error') for x in rows.values()) and not (B/'OWNER_ORIGINAL_ERROR.json').exists()
 assert time.monotonic()<until,'Pair positive policy evidence not yet proven; no same reader replay'
 time.sleep(3)
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes());active=c['active_segment'];assert active['owner_parent_pid']==p.pid and set(active['experts'])==set(go)=={'e2','recovery'} and current['deferred_experts_without_GO']==['h1']
assert c['authorized_training_seconds']==2268000 and len(c['budget_extensions'])==9
held=[x.path for x in p.open_files()];assert str(C.parent/'native_floor_supervisor.lock') in held and '/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock' in held
print(json.dumps(dict(epoch=time.time(),owner=v['owner'],current=current,canonical_active=active,remaining_actual_snapshot=c['remaining_training_seconds'],actual_original_two_locks_open=True,normal_H1_deferred=True,no210_GPU_query_or_worker=True,not_FINAL_or_skill=True)))
'''
lines=observer.splitlines(keepends=True);new=''.join(lines[:node.lineno-1])+'READ210='+repr(owner_read)+'\n'+''.join(lines[node.end_lineno:])
new=new.replace(OLD.name,STAGE).replace("'THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json'","'DUAL72_V85_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json'")
new=new.replace("dict(owner=q['owner_identity'],root=q['roots']['h1'],source_SHA=q['sources']['h1']['SHA'],GPU_UUID=q['specs']['h1']['GPU_UUID'],run_id=q['run_id'])","dict(owner=q['owner_identity'],run_id=q['run_id'])")
new=new.replace("('h1','e2','recovery')","('e2','recovery')")
new=new.replace('MIXED84_ACTUAL_GO_BASELINES_AND_NATIVE_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json','DUAL72_V85_ACTUAL_GO_NATIVE_E3_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json')
write('observe_dual72_V85_owner_native_E3_first_UNUSED.py',new,observer)

collector=read_source(OLD/'collect_mixed84_finals_original_cost_TEMPLATE.py','84_collector.py')
outer=ast.parse(collector);node=next(n for n in outer.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='READ210' for t in n.targets))
old_read=ast.literal_eval(node.value)
new_read=old_read.replace("owner=Path(q['owner_root']);h1=Path(q['roots']['h1']);","owner=Path(q['owner_root']);")
new_read=new_read.replace("a.startswith((str(owner)+'/',str(h1)+'/'))","a.startswith(str(owner)+'/')")
new_read=new_read.replace("ne=read(h1/'NODE_EXIT_ACTUAL.json');nt=read(h1/'NODE_TERMINAL_ACTUAL.json')\nassert ne['actual_all_own_children_waited'] and ne['validation_fcntl_released_if_acquired']\n",'')
new_read=new_read.replace("{'h1','e2','recovery'}","{'e2','recovery'}")
new_read=new_read.replace(",Path(q['specs']['h1']['private_lock'])",'')
new_read=new_read.replace("(('owner',owner),('h1',h1))","(('owner',owner),)")
new_read=new_read.replace('H1_node_exit=ne,H1_terminal=nt,','')
lines=collector.splitlines(keepends=True);new=''.join(lines[:node.lineno-1])+'READ210='+repr(new_read)+'\n'+''.join(lines[node.end_lineno:])
new=new.replace('MIXED84_ACTUAL_GO_BASELINES_AND_NATIVE_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json','DUAL72_V85_ACTUAL_GO_NATIVE_E3_UUID_CREATE_ARGV_VERIFIED_ACTUAL.json')
new=new.replace("'THREE_EXPERT_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json'","'DUAL72_V85_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json'")
start="        row=a['cohort']['rows']['h1'];final=row.get('final') or {};texts,models=capture(c,a,[final['final']] if final.get('passed') else [],'h1',route.PY);complete=dict(h1=models);c.close();c=None"
assert new.count(start)==1
new=new.replace(start,"        texts,unused=capture(c,a,[],'owner',route.PY);complete={};c.close();c=None",1)
new=new.replace("MIXED84_BASELINES_NATIVE_H1_AND_ORIGINAL_COST_RETURNED_ACTUAL.json","DUAL72_V85_NATIVE_E3_AND_ORIGINAL_COST_RETURNED_ACTUAL.json")
write('collect_dual72_V85_finals_original_cost_UNUSED.py',new,collector)

reviewer=read_source(OLD/'review_mixed84_baselines_native_fullstate_CPU_TEMPLATE.py','84_reviewer.py')
new=reviewer.replace('MIXED84_BASELINES_NATIVE_H1_AND_ORIGINAL_COST_RETURNED_ACTUAL.json','DUAL72_V85_NATIVE_E3_AND_ORIGINAL_COST_RETURNED_ACTUAL.json')
new=new.replace("{'h1','e2','recovery'}","{'e2','recovery'}",1).replace("for key in ('h1','recovery'):","for key in ('recovery',):",1)
begin=new.index("    diagpath=N/'current_three_closed_text/h1/")
end=new.index('    assert not torch.cuda.is_initialized()',begin)
new=new[:begin]+new[end:]
new=new.replace("assert set(models)=={'h1','recovery'}","assert set(models)=={'recovery'}")
new=new.replace('normal83B_H1_E3_baselines_and_separate_Fudan_native_H1_method','normal83B_E3_and_separate_Fudan_native_H1_method_H1_PPO_deferred')
new=new.replace('MIXED84_BASELINES_NATIVE_METHOD_AND_ORIGINAL_COST_CPU_ACTUAL.json','DUAL72_V85_NATIVE_E3_AND_ORIGINAL_COST_CPU_ACTUAL.json')
write('review_dual72_V85_native_E3_fullstate_CPU_UNUSED.py',new,reviewer)

with (HERE/'reports/V85_SOURCE_TEMPLATE_GENERATION_ACTUAL.json').open('x',encoding='utf8') as stream:
    json.dump(dict(epoch=time.time(),source_only=True,files=index,slots=['e2','recovery'],deferred=['h1'],
                   source_qualification_protocol_revision_V84_kept_byte_exact=True,
                   original_C_and_LOCKS_kept_source210=True,account_authority_migration_implemented=False,
                   binder_or_remote_scripts_executed=False,no_model_binary_read_or_copy=True,
                   Git_status='LOCAL_PENDING_ROOT_PHASE_ARCHIVE'),stream,indent=2)
print(json.dumps(dict(V85_source_templates_generated=True,no_live_actions=True)))
