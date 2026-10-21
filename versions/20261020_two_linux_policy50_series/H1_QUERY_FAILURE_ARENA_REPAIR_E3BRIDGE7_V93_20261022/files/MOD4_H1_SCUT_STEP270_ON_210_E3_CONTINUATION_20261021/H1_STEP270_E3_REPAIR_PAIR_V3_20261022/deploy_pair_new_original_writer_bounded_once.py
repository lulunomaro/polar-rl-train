from pathlib import Path
import hashlib, importlib.util, json, secrets, sys, time, traceback
N=Path(__file__).resolve().parent;T=N.parent;W=T.parent;R=N/'reports'
sys.path.insert(0,str(W/'MOD4_TWO_LINUX_POLICY50_COHORT_52_20261021'))
import deploy_two50_reconciled_original_writer_once as d
def put(name,v):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)

H1_INSTALL=r'''
from pathlib import Path
import fcntl,json,os,psutil,shutil,subprocess,time
B=Path(v['root']);s=v['spec'];owned=Path('/mnt/mod4_linux_durable_20261013')
assert B.resolve().is_relative_to(owned.resolve()) and owned.is_mount() and not B.exists()
mount=subprocess.check_output(['findmnt','-n','-o','UUID,FSTYPE,OPTIONS','--target',str(owned)],text=True).strip()
assert 'EF3105C85DD986BD' in mount.upper() and 'ntfs3' in mount and 'rw' in mount.split()[-1].split(',')
old=Path(s['previous_runtime_root']);query=Path(v['query_root']);previous_owner=Path(v['previous_owner'])
for root in (old,query):
 e=json.loads((root/'PARENT_EXIT_ACTUAL.json').read_bytes());p=json.loads((root/'PARENT_COMPLETE_ACTUAL.json').read_bytes());assert e['all_own_children_waited'] and e['own_eval_lease_released'] and p['actual_child_waited'] and p['returncode']==0 and p['passed'] and not p['errors']
assert json.loads((previous_owner/'OWNER_EXIT_ACTUAL.json').read_bytes())['original_cost_settled']
assert json.loads((previous_owner/'COHORT_FINAL.json').read_bytes())['original_cost_settled']

failed=owned/'H1step270_joint_2110v1/h1';fe=json.loads((failed/'NODE_EXIT_ACTUAL.json').read_bytes());fr=json.loads((failed/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row']
assert fe['actual_all_own_children_waited'] and fr['terminal_all_own_children_waited'] and fr['original_error'] and fr['final'] is None
assert not any(p.pid!=os.getpid() and any(x.startswith(str(failed)+'/') for x in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']))

e2=owned/'T2policy50_2010v52/e2';e=json.loads((e2/'NODE_EXIT_ACTUAL.json').read_bytes());r=json.loads((e2/'NODE_TERMINAL_ACTUAL.json').read_bytes())['row'];assert e['actual_all_own_children_waited'] and r['returncode']==0 and r['final']['passed'] and not r['errors']
for p in psutil.process_iter(['pid','cmdline']):
 try:assert p.pid==os.getpid() or not any(a.startswith(tuple(str(x)+'/' for x in (old,query,previous_owner,e2))) for a in p.info['cmdline'] or [])
 except psutil.NoSuchProcess:pass
C=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');c=json.loads(C.read_bytes())
assert c['active_segment'] is None and c['authorized_training_seconds']==1548000 and len(c['budget_extensions'])==8 and c['remaining_training_seconds']>82512.86069250107
for lock in (Path(s['private_lock']),C.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with lock.open('rb+') as f:fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(f,fcntl.LOCK_UN)
compute=subprocess.check_output(['nvidia-smi','--query-compute-apps=gpu_uuid,pid,used_gpu_memory','--format=csv,noheader,nounits'],text=True)
assert not any(s['GPU_UUID'] in x for x in compute.splitlines())
line=next(x for x in subprocess.check_output(['nvidia-smi','--query-gpu=uuid,memory.free','--format=csv,noheader,nounits'],text=True).splitlines() if s['GPU_UUID'] in x)
assert int(line.split(',')[-1])>15669 and psutil.virtual_memory().available>8*1024**3 and shutil.disk_usage(owned).free>25*1024**3
prior={x['relative']:x for x in json.loads((old/'SOURCE_MANIFEST.json').read_bytes())['files']}
B.mkdir(parents=True);need=[];copied=0
for row in v['manifest']['files']:
 rel=row['relative'];dest=B/rel;assert dest.resolve().is_relative_to(B.resolve());dest.parent.mkdir(parents=True,exist_ok=True)
 candidate=old/rel;before=prior.get(rel)
 if before and before['SHA']==row['SHA'] and before['bytes']==row['bytes'] and candidate.is_file() and not candidate.is_symlink():
  assert candidate.stat().st_size==row['bytes'];shutil.copy2(candidate,dest);copied+=1
 elif rel=='job0/source/'+s['source_filename']:
  src=Path(v['source']['path']);assert src==old/'job0/source.pt' and src.stat().st_size==row['bytes']
  assert prior['job0/source.pt']['SHA']==s['source_SHA']==row['SHA'];shutil.copy2(src,dest);copied+=1
 else:need.append(row)
print(json.dumps(dict(epoch=time.time(),root=str(B),need_upload=need,source_files_reused=copied,actual_original_mount=mount,GPU_line=line,durable_free=shutil.disk_usage(owned).free,canonical_None_two_locks_and_H1_lease_free=True,previous_E2_native_query_and_owner_allout=True,no_GO_or_account_write=True)))
'''

def install_h1(c,q):
    spec=q['specs']['h1'];root=q['roots']['h1'];local=Path(q['payloads']['h1'])
    manifest=json.loads((local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json').read_bytes())
    result=d.code(c,d.t.PY,H1_INSTALL,dict(root=root,spec=spec,manifest=manifest,source=q['sources']['h1'],
        query_root='/mnt/mod4_linux_durable_20261013/H1step270_cookedquery_full20k_2110v9',
        previous_owner=q['previous_owner_root']),timeout=120)
    put('H1_FRESH_RESOURCE_UNUSED_ROOT_SOURCE_INSTALL_ACTUAL.json',result)
    sf=c.open_sftp();sf.get_channel().settimeout(90)
    try:
        for row in result['need_upload']:sf.put(str(local/row['relative']),root+'/'+row['relative'])
        sf.put(str(local/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),root+'/THREE_SLOT_COMPLETE_MANIFEST_V1.json')
    finally:sf.close()
    cpu=d.code(c,d.t.PY,"import runpy,sys;sys.argv=['target_H1_step270_source_sdk_cpu_review_v1.py',v['root']];runpy.run_path(v['root']+'/target_H1_step270_source_sdk_cpu_review_v1.py',run_name='__main__')",dict(root=root),timeout=240)
    put('H1_FULL_INSTALLED_SOURCE_SDK_RSL_CPU_ACTUAL.json',cpu)
    admitted=d.code(c,d.t.PY,"from pathlib import Path;import sys,json;sys.path.insert(0,v['root']);from admitted_existing_same_source_native_CPU_v1 import load;print(json.dumps(load(v['spec'],Path(v['root']))))",dict(root=root,spec=spec),timeout=90)
    put('H1_EXISTING_NATIVE3_QUERY9_AND_PRODUCTION_CPU_ADMITTED_ACTUAL.json',admitted)

def main():
    q=json.loads((R/'TWO50_LATEST_CLOSED_SOURCES_PAYLOADS_CPU_PREPARED_ACTUAL.json').read_bytes())
    receipt=json.loads((R/'ORIGINAL_ACCOUNT_PENDING_RECONCILIATION_ACTUAL.json').read_bytes());q['previous_owner_root']='/mnt/mod4_linux_durable_20261013/H1s270_E3bridge_2210v7/owner'
    assert q['passed'] and set(q['specs'])=={'h1','recovery'} and receipt['passed']
    put('PAIR_DEPLOY_STARTED_ACTUAL.json',dict(epoch=time.time(),specs=q['specs'],sources=q['sources'],one_original_writer=True))
    d.put=put
    module=importlib.util.spec_from_file_location('memory',W/'MOD4_BUDGET_ADD100H_EIGHTH_20261021/run_authorized_cohort50_with_existing_hidden_stdin_memory.py')
    memory=importlib.util.module_from_spec(module);module.loader.exec_module(memory)
    secret=memory.recover();c=None;cfg=None
    try:
        c=d.connect72(secret);d.upload(c,d.PY72,'recovery',q);c.close();c=None
        c=d.t.connect();install_h1(c,q)
        boundary=d.code(c,d.t.PY,d.OWNER,dict(root=q['owner_root'],receipt=receipt),timeout=90)
        put('PAIR_ORIGINAL_OWNER_FRESH_CANONICAL_TWO_LOCKS_ACTUAL.json',boundary)
        sf=c.open_sftp()
        try:
            for name in ('three_slot_common_v1.py','three_slot_finite_owner_v1.py'):
                sf.put(str(N/'controllers'/name),q['owner_root']+'/'+name)
        finally:sf.close()
        cfg=dict(role='owner',experts=q['specs'],scheduling_authority='human_requested_available_experts',
                 deferred_experts=['e2'],run_id='H1_STEP270_RECOVERY_ORIGINAL_'+str(time.time_ns()),token=secrets.token_hex(32))
        owner=d.launch(c,d.t.PY,q['owner_root'],'three_slot_finite_owner_v1.py',cfg)
        ready=d.code(c,d.t.PY,"from pathlib import Path;import json,psutil,socket,time;B=Path(v['root']);until=time.monotonic()+20\nwhile not (B/'OWNER_IDENTITY.json').exists() and time.monotonic()<until:time.sleep(.1)\np=psutil.Process(v['pid']);assert str(B/'three_slot_finite_owner_v1.py') in p.cmdline()\nwith socket.create_connection(('10.24.4.210',29754),timeout=5):pass\nprint(json.dumps(dict(epoch=time.time(),owner=json.loads((B/'OWNER_IDENTITY.json').read_bytes()),actual_listener_ready=True)))",
                     dict(root=q['owner_root'],pid=owner['detached_pid']),timeout=30)
        put('PAIR_OWNER_ACTUAL_READY.json',ready)
        h1=d.launch(c,d.t.PY,q['roots']['h1'],'three_slot_finite_node_v1.py',
                    dict(q['specs']['h1'],role='node',run_id=cfg['run_id'],token=cfg['token']))
        c.close();c=None
        c=d.connect72(secret);secret=None
        recovery=d.launch(c,d.PY72,q['roots']['recovery'],'three_slot_finite_node_v1.py',
                          dict(q['specs']['recovery'],role='node',run_id=cfg['run_id'],token=cfg['token']))
        result=dict(epoch=time.time(),owner=owner,owner_identity=ready['owner'],nodes=dict(h1=h1,recovery=recovery),
                    roots=q['roots'],owner_root=q['owner_root'],specs=q['specs'],sources=q['sources'],run_id=cfg['run_id'],
                    both_installed_source_CPU_and_H1_actual_native_query_reuse=True,not_learning_until_actual_GO_PPO=True)
        put('PAIR_ORIGINAL_ACCOUNT_DETACHED_ACTUAL.json',result)
        print(json.dumps(dict(owner=owner,nodes=result['nodes'],not_learning_until_GO_PPO=True)))
    finally:
        secret=None
        if cfg:cfg.clear()
        if c:c.close()
if __name__=='__main__':
    try:main()
    except BaseException:
        put('PAIR_DEPLOY_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',
            dict(epoch=time.time(),error=traceback.format_exc(),no_retry_same_root_or_owner_or_refund=True))
        raise
