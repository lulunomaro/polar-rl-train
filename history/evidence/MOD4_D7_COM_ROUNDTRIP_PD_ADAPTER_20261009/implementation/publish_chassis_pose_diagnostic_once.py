"""Retain exact failure and measure actual setter pose changes before any acceptance change."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';receipt=R/'D7_COM_POSE_DIAGNOSTIC_PUBLISHED.json';assert not receipt.exists()
sys.path.insert(0,str(D.parent/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r'''
from pathlib import Path
import json,zipfile,hashlib,os,time
D=Path('/home/egde/rl_candidates/MOD4_D7_COM_PD_PREPARE_20261009');R=D/'reports';E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();read=lambda p:json.loads(p.read_text())
assert not (R/'D7_COM_POSE_DIAGNOSTIC_PUBLISHED.json').exists()
prior=read(E/'eval_queue/clk2500-closure-episode-d3-92-d7-com-buffer-sdk-on.json');base=Path(prior['artifacts']['runtime']['path']);assert sha(base)==prior['artifacts']['runtime']['sha256']
with zipfile.ZipFile(base) as z:
 m=json.loads(z.read('SOURCE_MANIFEST.json'));payload={n:z.read(n) for n in m['files']}
assert all(hashlib.sha256(payload[n]).hexdigest()==h for n,h in m['files'].items())
key='runtime/isaac/mod4/chassis_com_buffer_sdk_adapter.py';t=payload[key].decode();needle='            assert torch.equal(tensor(self.robot.root_view.get_coms()).to(expected.device)[...,3:],before_orientation)'
assert t.count(needle)==1
replacement="""            after_orientation=tensor(self.robot.root_view.get_coms()).to(expected.device)[...,3:].clone()
            diff=(after_orientation!=before_orientation).any(-1); indices=diff.nonzero().cpu().tolist()
            diag=dict(max_abs_component_delta=float((after_orientation-before_orientation).abs().max()),
                      mismatch_count=len(indices),poses=[dict(env=i,body=b,name=self.robot.body_names[b],before=before_orientation[i,b].cpu().tolist(),after=after_orientation[i,b].cpu().tolist()) for i,b in indices[:12]],
                      before_norm_range=[float(before_orientation.norm(dim=-1).min()),float(before_orientation.norm(dim=-1).max())],
                      after_norm_range=[float(after_orientation.norm(dim=-1).min()),float(after_orientation.norm(dim=-1).max())])
            assert torch.equal(after_orientation,before_orientation),diag"""
t=t.replace(needle,replacement);compile(t,key,'exec');payload[key]=t.encode()
manifest=dict(m,files={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()},actual_pose_change_diagnostic_only=True,exact_orientation_assertion_not_relaxed=True)
dest=E/'artifacts/d7-chassis-com-setter-pose-diagnostic-on-frozen.zip';assert not dest.exists()
with zipfile.ZipFile(str(dest)+'.partial','w',zipfile.ZIP_DEFLATED) as z:
 for n,b in payload.items():z.writestr(n,b)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(dest)+'.partial',dest)
job='clk2500-closure-episode-d3-92-d7-com-setter-pose-diagnostic-sdk-on';row=dict(prior,job_id=job,published_epoch=time.time(),role='Diagnostic-only actual setter quaternion mismatch measurement; exact invariant retained, no learning or accepted D7 scope',artifacts=dict(prior['artifacts'],runtime=dict(path=str(dest),sha256=sha(dest),bytes=dest.stat().st_size)))
target=E/'eval_queue'/(job+'.json');assert not target.exists();temp=target.with_suffix('.partial');temp.write_text(json.dumps(row,indent=2));os.replace(temp,target)
v=dict(epoch=time.time(),job=row,diagnostic_only=True,old_failures_preserved=True,original_orientation_exact_assert_not_relaxed=True,no_learning_PPO_or_canonical_changes=True)
(R/'D7_COM_POSE_DIAGNOSTIC_PUBLISHED.json').write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''
 _,o,e=c.exec_command('/usr/bin/python3 -c '+shlex.quote(code),timeout=40);raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode(errors='replace')
 v=json.loads(raw);receipt.write_text(json.dumps(v,indent=2),encoding='utf8');print(json.dumps(dict(job=v['job']['job_id'],package=v['job']['artifacts']['runtime'],exact_assertion_preserved=True)))
finally:c.close()
