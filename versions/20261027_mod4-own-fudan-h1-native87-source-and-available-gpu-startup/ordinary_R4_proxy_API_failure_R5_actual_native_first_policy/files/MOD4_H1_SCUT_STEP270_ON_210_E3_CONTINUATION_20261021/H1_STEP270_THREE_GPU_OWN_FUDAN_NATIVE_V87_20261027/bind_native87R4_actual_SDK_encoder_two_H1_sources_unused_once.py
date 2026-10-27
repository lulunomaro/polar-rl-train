"""New unused R4 source only; do not relabel any R3 error or its original costs."""
from pathlib import Path
import ast,json,hashlib,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
SDK_SHA='de7c9b2c6b6e0bdb431a0574727982feebe72142ebf41b1140dce624b932d6b8'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def copy(src,dst):
    dst=Path(dst);assert not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def main():
    q=read(R/'AVAILABLE_TWO_NATIVE87R3_SOURCE_PREPARED_ACTUAL.json');D=N/'payloads_r4';C=N/'controllers_r4';assert not D.exists() and not C.exists();D.mkdir();C.mkdir()
    A=L/'native87_encoder_actual_SDK_API_fix_v1'
    additions={'source/native_own_fudan87_training.py':(A/'native_own_fudan87_training.py','e1f3346c05ad5fc81ba657a803cc8443a81b2ac2444b376164f5010fe4dda9ad'),
        'source/native87_encoder_actual_sdk_adapter_v1.py':(A/'native87_encoder_actual_sdk_adapter_v1.py','5cd1a07abbd90d2c2535b7db7f0a815317a0385d018228f10bf74d2b3e5ecdaf'),
        'target_native87_source_sdk_cpu_v1.py':(A/'target_native87_source_sdk_cpu_v1.py','81882ed335c624225f2b02bc556ab6d014df4c2601c492c56826edea57d812f4')}
    for src,digest in additions.values():assert H(src)==digest
    for p in (N/'controllers_r3').iterdir():
        if p.is_file():copy(p,C/p.name)
    specs={};payloads={};roots={k:root.replace('2610v87r3/','2610v87r4/') for k,root in q['roots'].items()}
    for key in ('h1','recovery'):
        old=Path(q['payloads'][key]);P=D/key;P.mkdir();m=read(old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');old_rows={x['relative']:x for x in m['files']}
        for row in m['files']:
            p=old/row['relative'];assert p.stat().st_size==row['bytes'];copy(p,P/row['relative'])
        changed={}
        for rel,(src,digest) in additions.items():
            p=P/rel
            if p.exists():copy(p,P/'prebind87R4_exact_history'/(rel+'.original_bytes.txt'));p.write_bytes(src.read_bytes())
            else:copy(src,p)
            changed[rel]=digest
        c=read(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json');c['candidate_pins']=dict(c['candidate_pins'],**changed);c['expected_actual_SDK_observation_manager_SHA']=SDK_SHA
        c['approved_python']={p.relative_to(P).as_posix():H(p) for p in P.rglob('*.py')}
        c['source_repair_R4']='Actual installed ObservationManager property and resolved-term config access; remove nonexistent get_term_cfg; source API CPU before model load'
        copy(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json',P/'prebind87R4_exact_history/NATIVE87_SOURCE_CONTRACT_ACTUAL.json.original_bytes.txt')
        (P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json').write_text(json.dumps(c,indent=2),'utf8')
        t=read(P/'job0/TASK.json');copy(P/'job0/TASK.json',P/'prebind87R4_exact_history/TASK.json.original_bytes.txt');t['id']='H1_OWN_FUDAN_NATIVE87R4_'+key;t['native87_contract_SHA']=H(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json');t['expected_actual_SDK_observation_manager_SHA']=SDK_SHA;t['actual_encoder_source_API_admission_required']=True
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
        m['files']=rows;m['source_migration_version']='native87R4_actual_installed_encoder_API'
        if 'fresh_R2_source_only' in m:m['historical_inherited_source_preparation_flags']={'fresh_R2_source_only':m.pop('fresh_R2_source_only')}
        put(P/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',m)
        specs[key]=dict(q['specs'][key],candidate_pins=c['candidate_pins'],native87_contract_SHA=t['native87_contract_SHA'],manifest_SHA=H(P/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'),expected_actual_SDK_observation_manager_SHA=SDK_SHA);payloads[key]=str(P)
    cost_report=R/'CURRENT_ACTUAL87R3_GO_BUT_PRECONTROL_SDK_API_FAILURE_CLOSED_ORIGINAL_COST_WORK_ORDER.json';cost=read(cost_report)
    assert cost['closing_remaining_snapshot']==576916.5355293751 and cost['owner_nodes_children_out_and_original_fee_settled'] and cost['sum_once']==139.45133090019226
    new=dict(q,epoch=time.time(),specs=specs,payloads=payloads,roots=roots,controllers_relative='controllers_r4',owner_root=q['owner_root'].replace('2610v87r3/','2610v87r4/'),
        previous_failed_R3_roots=q['roots'],previous_failed_R3_owner=q['owner_root'],previousR3costreportSHA=H(cost_report),
        launch_remaining_snapshot=576916.5355293751,sole72_finite_balance_snapshot=576916.5355293751,
        source_scope='R4 new unused source namespaces after R3 actual precontrol original error and original independent fees; no same-root retry',
        actual_target_CPU_or_GPU_or_GO=False,SDK_source_API_probe_required=True,old_source_or_model_reread_for_Git=False)
    put(R/'AVAILABLE_TWO_NATIVE87R4_SOURCE_PREPARED_ACTUAL.json',new)
    print(json.dumps(dict(passed=True,source_only=True,roots=roots,current_original_balance=576916.5355293751)))
if __name__=='__main__':
    try:main()
    except BaseException:
        put(R/('NATIVE87R4_LOCAL_BIND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_remote_or_GO=True));raise
