"""Publish a new immutable sensor scope to the existing single-GPU evaluator."""
from pathlib import Path
import sys,json,shlex
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent
assert not (R/'SENSOR_ASYNC_PACKAGE_AND_JOBS.json').exists()
sys.path.insert(0,str(W/'MOD4_AUTONOMY_SLEEP_20261003'));from remote_io import connect
c=connect()
try:
 code=r"""
from pathlib import Path
import json,hashlib,zipfile,os,time
E=Path('/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007');S=Path('/home/egde/rl_candidates/MOD4_E0_SENSOR_DR_STAGE1_20261007');R=E/'reports';A=E/'artifacts';Q=E/'eval_queue'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
receipt=R/'SENSOR_ASYNC_PACKAGE_AND_JOBS.json';assert not receipt.exists()
approval=json.loads((R/'PLAN_APPROVAL.json').read_text());assert approval['approved'] and 'S0E' in approval['allowed_stages'] and 'S2' in approval['allowed_stages']
assert approval['approved_plan_sha256']=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
assert json.loads((S/'reports/SENSOR_ACTUAL_SDK_PASSED.json').read_text())['real_manager_formula_tick_selected_reset_cleancritic_verified']
selection=json.loads((R/'S1A_ARCHITECTURE_SELECTION.json').read_text());source=selection['selected_source'];assert selection['selected_architecture']=='A0' and sha(Path(source['path']))==source['sha256']
freeze=json.loads((S/'reports/SOURCE_FREEZE.json').read_text())['sha256'];assert len(freeze)==199
payload={};files={};aliases={}
for n,h in freeze.items():
 p=S/n;assert sha(p)==h,n;payload['runtime/'+n]=p.read_bytes()
for kind in ('flat','spin','world'):
 original=(S/'isaac/mod4'/('sensor_'+kind+'_probe.py')).read_text();derived=original
 if kind=='flat':
  marker='from sensor_a0_runtime import SensorMod4Env as Mod4Env';assert derived.count(marker)==1
  instrumentation='''from sensor_a0_runtime import SensorMod4Env
class Mod4Env(SensorMod4Env):
    def step(self,action):
        result=super().step(action)
        if self.num_envs==10:
            if not hasattr(self,'_platform_sensor_sdk'):self._platform_sensor_sdk=[];self._platform_sensor_reset=None
            if len(self._platform_sensor_sdk)==100:
                ids=torch.tensor([1,4,7],device=self.device);other=torch.tensor([0,2,3,5,6,8,9],device=self.device)
                s=self._sensor_mild;bias=s.bias.clone();episode=s.episode.clone();tick=self.common_step_counter
                self._reset_idx(ids)
                assert torch.equal(bias[other],s.bias[other]) and torch.equal(episode[other],s.episode[other]) and bool((s.episode[ids]==episode[ids]+1).all()) and tick==self.common_step_counter
                result=(self.observation_manager.compute(),*result[1:])
                self._platform_sensor_reset=dict(ids=[1,4,7],other_bias_episode_exact=True,global_tick_unchanged=True)
            self._platform_sensor_sdk.append(self.sensor_sdk_audit())
        return result
'''
  derived=derived.replace(marker,instrumentation)
 marker="    result['sensor_recipe']=env._sensor_mild.receipt()";assert marker in derived
 extra="\n    result['sensor_actual_manager_audit']=env.sensor_sdk_audit()"
 if kind=='flat':extra+="\n    result['sensor_platform_sdk']=dict(rows=getattr(env,'_platform_sensor_sdk',[]),selected_reset=getattr(env,'_platform_sensor_reset',None),diagnostic_reset_only_for_10env=True)"
 derived=derived.replace(marker,marker+extra)
 compile(derived,'platform_sensor_'+kind,'exec')
 alias='runtime/isaac/mod4/frozen_history_'+kind+'.py';payload[alias]=derived.encode();aliases[alias]=dict(original_path='isaac/mod4/sensor_'+kind+'_probe.py',original_sha256=sha(S/'isaac/mod4'/('sensor_'+kind+'_probe.py')),added_diagnostic_manager_audit=True,selected_reset_only_10env=(kind=='flat'))
oldpack=json.loads((R/'CLOCK1000_PACKAGE_STAGED.json').read_text());assert sha(Path(oldpack['package']['path']))==oldpack['package']['sha256']
with zipfile.ZipFile(oldpack['package']['path']) as z:
 oldmanifest=json.loads(z.read('SOURCE_MANIFEST.json'))
 for name,h in oldmanifest['files'].items():
  if name.startswith('assets/'):
   raw=z.read(name);assert hashlib.sha256(raw).hexdigest()==h;payload[name]=raw
assert hashlib.sha256(payload['assets/robot.usd']).hexdigest()=='694e9d5414401972d9186c44baef25aa785e1e07409ce9acf1ef553b9279dd87'
files={n:hashlib.sha256(raw).hexdigest() for n,raw in payload.items()}
manifest=dict(files=files,original_runtime_source_count=199,source_freeze_sha256=sha(S/'reports/SOURCE_FREEZE.json'),original199_files_exact=True,probe_alias_deltas=aliases,
 clock=dict(physics_dt_s=.001,control_dt_s=.01,decimation=10,force_bin_s=.005,force_history=3),sensor_profile='noise_bias_mild_v1',actor_feedback_only=True,clean_critic=True,
 allowed_windows_adapter=['RM_MOD4_USD'],asset_originals_unchanged=True,scope_not_yet_platform_accepted=True)
package=A/'clock1000-s2-sensor199-frozen.zip';assert not package.exists()
with zipfile.ZipFile(str(package)+'.partial','w',compression=zipfile.ZIP_DEFLATED) as z:
 for n,raw in payload.items():z.writestr(n,raw)
 z.writestr('SOURCE_MANIFEST.json',json.dumps(manifest,indent=2))
os.replace(str(package)+'.partial',package)
runtime=dict(path=str(package),bytes=package.stat().st_size,sha256=sha(package));checkpoint={k:oldpack['sources']['A0'][k] for k in ('path','bytes','sha256')};assert checkpoint['sha256']==source['sha256'] and sha(Path(checkpoint['path']))==source['sha256']
rows=[('sdk','flat',10,300)]+[(kind,kind,80 if kind=='flat' else 88,1500) for kind in ('flat','spin','world')];jobs=[]
for label,kind,count,steps in rows:
 job='clk1000-s2sensor-'+label;target=Q/(job+'.json');assert not target.exists()
 row=dict(job_id=job,stage='S0E',immutable=True,plan_id=approval['plan_id'],plan_sha256=approval['approved_plan_sha256'],published_epoch=time.time(),kind=kind,
  profile='white_v3',sensor_profile='noise_bias_mild_v1',seed=20261002,num_envs=count,steps=steps,max_wall_seconds=1800,architecture_variant='A0',role='S2 sensor baseline A0',physics_dt_s=.001,control_dt_s=.01,
  protocol='New sensor feedback scope: actual manager/cache/selected reset SDK, then firstseed white3 frozen flat/spin/world. Full15s tasks unchanged. Not platform acceptance or trained improvement.',
  artifacts=dict(runtime=runtime,checkpoint=checkpoint),no_learning=True,canonical_write_authority=False,GPU_concurrency=1,platform_scope_not_yet_accepted=True)
 temp=target.with_suffix('.json.partial');temp.write_text(json.dumps(row,indent=2));os.replace(temp,target);jobs.append(row)
proof=dict(epoch=time.time(),package=runtime,checkpoint=checkpoint,source_manifest=manifest,jobs=jobs,total_jobs=4,new_learning=False,new_budget_seconds=0,existing_worker_unchanged=True,no_additional_worker_or_task=True,platform_scope_pending=True)
receipt.write_text(json.dumps(proof,indent=2));(S/'reports/SENSOR_ASYNC_PACKAGE_AND_JOBS.json').write_text(json.dumps(proof,indent=2))
print(json.dumps(proof))
"""
 _,o,e=c.exec_command('/home/egde/anaconda3/envs/fangzhen-isaaclab/bin/python -c '+shlex.quote(code),timeout=90)
 raw=o.read();err=e.read();assert o.channel.recv_exit_status()==0,(raw+err).decode();v=json.loads(raw)
 (R/'SENSOR_ASYNC_PACKAGE_AND_JOBS.json').write_text(json.dumps(v,indent=2))
 print(json.dumps(dict(epoch=v['epoch'],package=v['package'],job_ids=[x['job_id'] for x in v['jobs']],existing_worker_unchanged=True)))
finally:c.close()
