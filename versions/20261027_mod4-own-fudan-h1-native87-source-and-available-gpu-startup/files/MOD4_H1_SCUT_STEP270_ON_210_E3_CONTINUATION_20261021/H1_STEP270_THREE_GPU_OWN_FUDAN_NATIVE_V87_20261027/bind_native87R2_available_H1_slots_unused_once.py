"""Two new unused R2 source namespaces, new exact exec capture and encoder mapping."""
from pathlib import Path
import ast,json,hashlib,shutil,sys,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def copy(src,dst):
    dst=Path(dst);assert not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def main():
    q=read(R/'THREE_H1_NATIVE87_LOCAL_BOUND_SOURCE_PREPARED_ACTUAL.json');D=N/'payloads_r2';C=N/'controllers_r2';assert not D.exists() and not C.exists()
    v4=L/'native87_dispatcher_v4/native87_closed_source_CPU_v1.py';entry=L/'root_native_entry_actual_encoder_order_v2/native_own_fudan87_training.py'
    assert H(v4)=='89cba5ea5b0de7571c0c285bc6899d87ec6d10fe7f8bff54c9b2bfb41e12e431' and H(entry)=='4c27adaf9995e8718a461138e2e3dd5d65204c12d65e9c73d7d012ebb71c7e65'
    D.mkdir();C.mkdir();specs={};payloads={};roots=dict(h1='/mnt/mod4_linux_durable_20261013/H1step270_own_fudan_native_2610v87r2/h1',recovery='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_own_fudan_native_2610v87r2/recovery')
    for p in (N/'controllers').glob('*.py'):copy(p,C/p.name)
    copy(C/'native87_closed_source_CPU_v1.py',C/'native87_closed_source_CPU_v1.py.V3_original_bytes.txt');(C/'native87_closed_source_CPU_v1.py').write_bytes(v4.read_bytes())
    A=L/'native87_available_two_schedule_source'
    owner_script='three_slot_finite_owner_NATIVE87_AVAILABLE_TWO_authority72.py'
    for name in (owner_script,'native87_available_two_schedule_v1.py'):copy(A/name,C/name)
    boundary=R/'NATIVE87_DUAL72_ACTUAL_GPU_RESOURCE_BOUNDARY_RETURNED_ACTUAL.json';copy(boundary,C/'AVAILABLE_TWO_RESOURCE_BOUNDARY_ACTUAL.json')
    for key in ('h1','recovery'):
        old=Path(q['payloads'][key]);P=D/key;P.mkdir();m=read(old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');old_rows={x['relative']:x for x in m['files']}
        for row in m['files']:
            p=old/row['relative'];assert p.is_file() and p.stat().st_size==row['bytes'];copy(p,P/row['relative'])
        changed={}
        for src,rel in ((v4,'native87_closed_source_CPU_v1.py'),(entry,'source/native_own_fudan87_training.py')):
            p=P/rel;copy(p,P/'prebind87R2_exact_history'/(rel+'.original_bytes.txt'));p.write_bytes(src.read_bytes());changed[rel]=H(p)
        c=read(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json');c['candidate_pins']=dict(c['candidate_pins'],**changed)
        c['approved_python']={p.relative_to(P).as_posix():H(p) for p in P.rglob('*.py')}
        c['source_repair_R2']='Exact own exec snapshots use fresh psutil Process instances, old failure retained; actual sensor encoder order independent from actuator order'
        old_contract=(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json').read_bytes();copy(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json',P/'prebind87R2_exact_history/NATIVE87_SOURCE_CONTRACT_ACTUAL.json.original_bytes.txt')
        (P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json').write_text(json.dumps(c,indent=2),'utf8')
        t=read(P/'job0/TASK.json');copy(P/'job0/TASK.json',P/'prebind87R2_exact_history/TASK.json.original_bytes.txt');t['id']='H1_OWN_FUDAN_NATIVE87R2_'+key;t['native87_contract_SHA']=H(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json');t['R2_original_attempts_preserved']=True
        (P/'job0/TASK.json').write_text(json.dumps(t,indent=2),'utf8')
        changed.update({'NATIVE87_SOURCE_CONTRACT_ACTUAL.json':H(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json'),'job0/TASK.json':H(P/'job0/TASK.json')})
        rows=[]
        for p in sorted(P.rglob('*')):
            if not p.is_file():continue
            rel=p.relative_to(P).as_posix()
            if rel in old_rows and rel not in changed:
                row=old_rows[rel];assert row['bytes']==p.stat().st_size;rows.append(row)
            else:rows.append(dict(relative=rel,bytes=p.stat().st_size,SHA=H(p)))
            if p.suffix=='.py':ast.parse(p.read_text('utf8'))
        m['files']=rows;m['fresh_R2_source_only']=True;put(P/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',m)
        s=dict(q['specs'][key],candidate_pins=c['candidate_pins'],native87_contract_SHA=t['native87_contract_SHA'],manifest_SHA=H(P/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'))
        specs[key]=s;payloads[key]=str(P)
    new=dict(passed=True,epoch=time.time(),specs=specs,payloads=payloads,roots=roots,sources={k:q['sources'][k] for k in specs},
        controllers_relative='controllers_r2',owner_root='/home/lc01/Zonglin Li/zonglin2/tasks/H1step270_own_fudan_native_2610v87r2/owner',owner_script=owner_script,
        deferred_experts=['e2'],resource_boundary_SHA=H(boundary),resource_boundary_relative='AVAILABLE_TWO_RESOURCE_BOUNDARY_ACTUAL.json',
        all_active_slots_only_H1_repair=True,actual_target_CPU_or_GPU_or_GO=False,old_N87_actual_source_reports_not_relabelled=True,
        old_H1_CPU_proof_not_reused_for_changed_source=True,sole72_finite_balance_snapshot=577055.9868602753,source_model_local_reload_or_hash=False)
    put(R/'AVAILABLE_TWO_NATIVE87R2_SOURCE_PREPARED_ACTUAL.json',new)
    print(json.dumps(dict(passed=True,source_only=True,active=list(specs),deferred=['e2'],roots=roots)))
if __name__=='__main__':
    try:main()
    except BaseException:
        put(R/('NATIVE87R2_LOCAL_BIND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_remote_or_GO=True));raise
