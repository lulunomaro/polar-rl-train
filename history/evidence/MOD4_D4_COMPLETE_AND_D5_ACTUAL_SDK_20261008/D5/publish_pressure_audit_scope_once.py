"""Publish only the new pressure-aware actual-value observer; reuse valid off SDK."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'SPRING_PRESSURE_AUDIT_SCOPE_PUBLISHED.json').exists()
old=json.loads((R/'PRESSURE_SDK_SECOND_FIXED_BASELINE_ERROR.json').read_text(encoding='utf8'))
assert old['jobs'][0]['result']['phase']=='complete' and old['jobs'][1]['result']['phase']=='retained_failed'
assert 'gas_springs_stiffness_error' in old['jobs'][1]['last_error_log']
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D5_SPRING_LAW_PREPARE_20261008'
try:
    with c.open_sftp() as f:
        for n,p in [('spring_pressure_audit_runtime.py',D/'spring_pressure_audit_runtime.py'),('reports/PRESSURE_SDK_SECOND_FIXED_BASELINE_ERROR.json',R/'PRESSURE_SDK_SECOND_FIXED_BASELINE_ERROR.json')]:
            raw=p.read_bytes()
            with f.open(root+'/'+n,'wb') as out:out.write(raw)
            assert f.open(root+'/'+n).read()==raw
    code=r"""
from pathlib import Path
import json,hashlib,zipfile,os,time
D=Path('/home/egde/rl_candidates/MOD4_D5_SPRING_LAW_PREPARE_20261008');R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'SPRING_PRESSURE_AUDIT_SCOPE_PUBLISHED.json').exists()
a=read(E/'reports/PLAN_APPROVAL.json');assert a['approved'] and 'S2' in a['allowed_stages'] and a['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
prior=read(R/'SPRING_PRESSURE_INDEX_REVIEW_PUBLISHED.json');row=prior['jobs'][1];base=Path(row['artifacts']['runtime']['path']);assert sha(base)==row['artifacts']['runtime']['sha256']
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(hashlib.sha256(payload[n]).hexdigest()==h for n,h in m['files'].items())
name='runtime/isaac/mod4/frozen_history_flat.py';source=payload[name].decode();old='from spring_pressure_index_runtime import SpringPressureSDK,PressureSpringReadback';assert source.count(old)==1
payload[name]=source.replace(old,'from spring_pressure_audit_runtime import SpringPressureSDK,PressureSpringReadback').encode()
payload['runtime/isaac/mod4/spring_pressure_audit_runtime.py']=(D/'spring_pressure_audit_runtime.py').read_bytes()
manifest=dict(m,files={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},base_immutable_SHA=sha(base),D5_expected_gas_stiffness_from_independent_D5_state=True,all_other_D0_parameter_checks_unchanged=True,original_nominal_baseline_restored_after_audit=True,original_mild_dr_py_byte_exact=True,valid67_off_evidence_reused=True,old67_on_rejection_preserved=True)
dest=E/'artifacts/d5-stiffness-pressure-aware-audit-sdk-on-frozen.zip';assert not dest.exists()
with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(dest)+'.partial',dest)
job='clk2500-closure-episode-d3-68-d5-stiffness-audit-sdk-on';target=E/'eval_queue'/(job+'.json');assert not target.exists()
new=dict(row,job_id=job,published_epoch=time.time(),role='D5 SDK pressure-aware expected stiffness observer after unchangedD0 fixed3500-reference rejection; all other D0 checks retained; valid67-off reused',artifacts=dict(row['artifacts'],runtime=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size)))
tmp=target.with_suffix('.partial');tmp.write_text(json.dumps(new,indent=2));os.replace(tmp,target)
v=dict(epoch=time.time(),job=new,valid_67_off_reused=True,old_failed_sources_and_actual_results_preserved=True,no_repeated_offSDK_or_PPO_or_canonical_write=True,actual_new_on_scope_pending=True)
(R/'SPRING_PRESSURE_AUDIT_SCOPE_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
"""
    compile(code,'pressure-aware actual observer publication','exec')
    _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=40)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);(R/'SPRING_PRESSURE_AUDIT_SCOPE_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    print(json.dumps(dict(epoch=v['epoch'],job=v['job']['job_id'],runtime=v['job']['artifacts']['runtime'],valid_off_reused=True)))
finally:c.close()
