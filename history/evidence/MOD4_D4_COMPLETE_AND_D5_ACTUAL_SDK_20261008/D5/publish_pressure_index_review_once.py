"""Publish only the corrected joint-index conversion, preserving failed packages."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports'
assert not (R/'SPRING_PRESSURE_INDEX_REVIEW_PUBLISHED.json').exists()
error=json.loads((R/'PRESSURE_SDK_FIRST_INDEX_ERROR.json').read_text(encoding='utf8'));assert error['jobs'][0]['result']['phase']=='retained_failed'
assert "can't convert cuda:0 device type tensor to numpy" in error['jobs'][0]['last_error_log']
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect();root='/home/egde/rl_candidates/MOD4_D5_SPRING_LAW_PREPARE_20261008'
try:
    with c.open_sftp() as f:
        for n,p in [('spring_pressure_index_runtime.py',D/'spring_pressure_index_runtime.py'),('reports/PRESSURE_SDK_FIRST_INDEX_ERROR.json',R/'PRESSURE_SDK_FIRST_INDEX_ERROR.json')]:
            raw=p.read_bytes()
            with f.open(root+'/'+n,'wb') as out:out.write(raw)
            assert f.open(root+'/'+n).read()==raw
    code=r"""
from pathlib import Path
import json,hashlib,zipfile,os,time
D=Path('/home/egde/rl_candidates/MOD4_D5_SPRING_LAW_PREPARE_20261008');R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
read=lambda p:json.loads(p.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert not (R/'SPRING_PRESSURE_INDEX_REVIEW_PUBLISHED.json').exists()
approval=read(E/'reports/PLAN_APPROVAL.json');assert approval['approved'] and 'S2' in approval['allowed_stages'] and approval['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
old=(D/'spring_pressure_sdk_adapter.py').read_text();new=(D/'spring_pressure_index_runtime.py').read_text()
assert new==old.replace("        if hasattr(indices,'numpy'):indices=indices.numpy().tolist()","        if torch.is_tensor(indices):indices=indices.detach().cpu().tolist()\n        elif hasattr(indices,'numpy'):indices=indices.numpy().tolist()")
prior=read(R/'SPRING_PRESSURE_SDK_PUBLISHED.json');jobs=[]
for row in prior['jobs']:
 label=row['job_id'].rsplit('-',2)[-2]+'-'+row['job_id'].rsplit('-',1)[-1]
 assert label in ('00-off','01-on')
 base=Path(row['artifacts']['runtime']['path']);assert sha(base)==row['artifacts']['runtime']['sha256']
 with zipfile.ZipFile(base) as z:
  m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
 assert all(hashlib.sha256(payload[n]).hexdigest()==h for n,h in m['files'].items())
 n='runtime/isaac/mod4/frozen_history_flat.py';source=payload[n].decode();oldimport='from spring_pressure_sdk_adapter import SpringPressureSDK,PressureSpringReadback';assert source.count(oldimport)==1
 payload[n]=source.replace(oldimport,'from spring_pressure_index_runtime import SpringPressureSDK,PressureSpringReadback').encode()
 payload['runtime/isaac/mod4/spring_pressure_index_runtime.py']=new.encode()
 manifest=dict(m,files={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},actual_CUDA_joint_index_conversion_reviewed=True,base_immutable_SHA=sha(base),old_failed_source_kept=True,source_delta_only_CUDA_index_to_CPU_name_order_check=True)
 dest=E/'artifacts'/('d5-stiffness-index-review-sdk-'+label+'-frozen.zip');assert not dest.exists()
 with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
  for n,b in payload.items():z.writestr(n,b)
  z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
 os.replace(str(dest)+'.partial',dest)
 job='clk2500-closure-episode-d3-67-d5-stiffness-index-sdk-'+label;target=E/'eval_queue'/(job+'.json');assert not target.exists()
 newrow=dict(row,job_id=job,published_epoch=time.time(),role='New isolated CUDA index-codec review after constructor failure; same actual spring pressure SDK; original failed66 and unexecuted01 retained',artifacts=dict(row['artifacts'],runtime=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size)))
 tmp=target.with_suffix('.partial');tmp.write_text(json.dumps(newrow,indent=2));os.replace(tmp,target);jobs.append(newrow)
v=dict(epoch=time.time(),jobs=jobs,actual_SDK_pending=True,previous_failed_constructor_source_preserved=True,previous_01_never_executed_and_not_passed=True,no_4090_PPO_canonical_or_runtime_change=True)
(R/'SPRING_PRESSURE_INDEX_REVIEW_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
"""
    compile(code,'pressure CUDA index publication','exec')
    _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=40)
    raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
    v=json.loads(raw);(R/'SPRING_PRESSURE_INDEX_REVIEW_PUBLISHED.json').write_text(json.dumps(v,indent=2),encoding='utf8')
    print(json.dumps(dict(epoch=v['epoch'],jobs=[j['job_id'] for j in v['jobs']],packages=[j['artifacts']['runtime'] for j in v['jobs']])))
finally:c.close()
