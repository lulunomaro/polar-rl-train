"""New R3 source binding; preserve failed R2 roots and every original false receipt."""
from pathlib import Path
import ast,json,hashlib,shutil,time,traceback
N=Path(__file__).resolve().parent;T=N.parent;L=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027';R=N/'reports'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_bytes())
def put(p,v):
    p=Path(p);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('x',encoding='utf8') as f:json.dump(v,f,indent=2,allow_nan=False)
def copy(src,dst):
    dst=Path(dst);assert not dst.exists();dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
def main():
    q=read(R/'AVAILABLE_TWO_NATIVE87R2_SOURCE_PREPARED_ACTUAL.json');D=N/'payloads_r3';C=N/'controllers_r3';assert not D.exists() and not C.exists();D.mkdir();C.mkdir()
    A=L/'native87_role_metadata_closure_v1'
    files={'native87_protocol_v1.py':'f533670097f268357440a553937fe856f92682ab71ba09484f1971f09a632250','native87_source_guard_v1.py':'f995df6cde57d09fe93f2b92b904ea18ee408dcbe51b51af290aa7eaa7a2f6ce','target_native87_source_sdk_cpu_v1.py':'8a7b8c1b1a078ec9aaec83abe8575108eeafbdd2c3866c13b51ea271d8c49fd5','native87_role_metadata_closure_v1.py':'3aeee77b4f65255add3cf3c706a2486089551303b8402f475a3c45c96c0f5234'}
    for name,digest in files.items():assert H(A/name)==digest
    binding=T/'H1_STEP270_THREE_GPU_NATIVE_CONTINUATION_RESOURCE_V86B_20261026/payloads/h1/OWNER72_CONTROL_DEPENDENCIES_BINDING_ACTUAL.json';assert H(binding)=='14271a0c033e98c88b434513fff7ad614996a94386e4a6fbbd6b926f319fd621'
    for p in (N/'controllers_r2').iterdir():
        if p.is_file():copy(p,C/p.name)
    copy(C/'native87_protocol_v1.py',C/'native87_protocol_v1.py.before_role_closure.txt');(C/'native87_protocol_v1.py').write_bytes((A/'native87_protocol_v1.py').read_bytes())
    specs={};payloads={};roots={k:root.replace('2610v87r2/','2610v87r3/') for k,root in q['roots'].items()}
    for key in ('h1','recovery'):
        old=Path(q['payloads'][key]);P=D/key;P.mkdir();m=read(old/'THREE_SLOT_COMPLETE_MANIFEST_V1.json');old_rows={r['relative']:r for r in m['files']}
        for row in m['files']:
            p=old/row['relative'];assert p.stat().st_size==row['bytes'];copy(p,P/row['relative'])
        changed={}
        for name,digest in files.items():
            p=P/name
            if p.exists():copy(p,P/'prebind87R3_exact_history'/(name+'.original_bytes.txt'));p.write_bytes((A/name).read_bytes())
            else:copy(A/name,p)
            changed[name]=digest
        if key=='h1':copy(binding,P/binding.name);changed[binding.name]=H(binding)
        c=read(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json');c['candidate_pins']=dict(c['candidate_pins'],**changed)
        c['approved_python']={p.relative_to(P).as_posix():H(p) for p in P.rglob('*.py')}
        c['source_repair_R3']='Role-required source210 control binding closure and actual installed dependency CPU verification; original control/learning/physical unchanged'
        copy(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json',P/'prebind87R3_exact_history/NATIVE87_SOURCE_CONTRACT_ACTUAL.json.original_bytes.txt')
        (P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json').write_text(json.dumps(c,indent=2),'utf8')
        t=read(P/'job0/TASK.json');copy(P/'job0/TASK.json',P/'prebind87R3_exact_history/TASK.json.original_bytes.txt');t['id']='H1_OWN_FUDAN_NATIVE87R3_'+key;t['native87_contract_SHA']=H(P/'NATIVE87_SOURCE_CONTRACT_ACTUAL.json');t['R3_role_metadata_closure_required']=True
        if key=='h1':t['owner_control_dependency_binding_SHA']=H(binding)
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
        m['files']=rows;m['R3_role_metadata_closure_required']=True;put(P/'THREE_SLOT_COMPLETE_MANIFEST_V1.json',m)
        specs[key]=dict(q['specs'][key],candidate_pins=c['candidate_pins'],native87_contract_SHA=t['native87_contract_SHA'],manifest_SHA=H(P/'THREE_SLOT_COMPLETE_MANIFEST_V1.json'));payloads[key]=str(P)
    new=dict(q,epoch=time.time(),specs=specs,payloads=payloads,roots=roots,controllers_relative='controllers_r3',owner_root=q['owner_root'].replace('2610v87r2/','2610v87r3/'),
        previous_failed_R2_roots=q['roots'],previous_failed_R2_owner=q['owner_root'],previous_failed_R2_allout_report_SHA=H(R/'NATIVE87R2_ALL_OWN_STARTUP_ERROR_TEXT_RETURNED_ACTUAL.json'),
        source_scope='R3 new unused namespaces after actual R2 preGO/no-fee failure; no old source CPU or node rearm',human_deferred_busy_GPU_confirmed=True,
        actual_target_CPU_or_GPU_or_GO=False,old_H1_CPU_proof_not_reused_for_changed_source=True)
    put(R/'AVAILABLE_TWO_NATIVE87R3_SOURCE_PREPARED_ACTUAL.json',new)
    print(json.dumps(dict(passed=True,source_only=True,roots=roots,h1_control_binding_in_required_closure=True)))
if __name__=='__main__':
    try:main()
    except BaseException:
        put(R/('NATIVE87R3_LOCAL_BIND_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(error=traceback.format_exc(),no_remote_or_GO=True));raise
