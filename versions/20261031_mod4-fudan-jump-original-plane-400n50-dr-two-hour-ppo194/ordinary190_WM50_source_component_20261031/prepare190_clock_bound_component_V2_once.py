from pathlib import Path
import ast,hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports';R.mkdir(exist_ok=True)
with (R/'SOURCE190_V2_PREPARATION_ONCE.json').open('x') as f:json.dump(dict(epoch=time.time(),no_model_raw_SDK_remote_or_GPU=True),f)
p=N/'teacher_world_model50_core190.py';s=p.read_text(encoding='utf8')
s=s.replace("        self.device=torch.device(device);self.envs=envs;self.window=window;self.batch=batch", "        if not (isinstance(envs,int) and envs>0 and 1<=window<=64 and batch>0):raise ValueError('Invalid bounded replay dimensions')\n        self.device=torch.device(device);self.envs=envs;self.window=window;self.batch=batch\n        self.last_physics_tick=None")
s=s.replace("        self.updates=0;self.controls=0", "        self.updates=0;self.controls=0")
old="""    def add(self,transition):
        assert set(self.buffer.fields)<=set(transition)
        fields={key:transition[key][:self.envs].detach() for key in self.buffer.fields}
        assert all(value.shape[0]==self.envs for value in fields.values())
"""
new="""    def add(self,transition,*,physics_end_tick,physics_us,feedback_samples):
        # A protocol label alone cannot convert100Hz transitions into50Hz truth.
        if type(physics_end_tick) is not int or physics_end_tick<8 or physics_end_tick%8 or physics_us!=2500 or feedback_samples!=2:
            raise ValueError('Actual eight2500us callbacks and two100Hz feedback samples required')
        if self.last_physics_tick is not None and physics_end_tick!=self.last_physics_tick+8:
            raise ValueError('Duplicate, skipped, or100Hz transition clock')
        if not set(self.buffer.fields)<=set(transition):raise ValueError('Incomplete measured transition')
        fields={}
        for key,(width,dtype) in self.buffer.fields.items():
            value=transition[key]
            tail=(width,) if isinstance(width,int) else width
            if not torch.is_tensor(value) or value.ndim!=1+len(tail) or value.shape[0]<self.envs or tuple(value.shape[1:])!=tail or value.dtype!=dtype or value.device!=self.device:
                raise ValueError('Wrong transition shape/type/device '+key)
            if (value.is_floating_point() or value.is_complex()) and not torch.isfinite(value).all():raise ValueError('Nonfinite measured transition '+key)
            fields[key]=value[:self.envs].detach()
"""
assert old in s;s=s.replace(old,new)
s=s.replace("        self.buffer.add(fields);self.controls+=1", "        self.buffer.add(fields);self.controls+=1;self.last_physics_tick=physics_end_tick")
s=s.replace("                    physical_controls=self.controls,protocol=self.protocol,replay_saved=False,", "                    physical_controls=self.controls,last_physics_tick=self.last_physics_tick,protocol=self.protocol,replay_saved=False,")
ast.parse(s);dest=N/'teacher_world_model50_core190_v2.py'
with dest.open('x',encoding='utf8') as f:f.write(s)
source=T/'MOD4_H1_MATLAB_REFERENCE_IMAGINATION_TRACKING_RESOURCE_V165_20261030/payloads_v2/seed27/source'
inputs=[dest,p,source/'compact_episode_static31_v1.py',source/'supermimic_wheel_leg_v3/geometry.py',source/'supermimic_wheel_leg_v3/networks.py',source/'supermimic_wheel_leg_v3/replay.py',source/'supermimic_wheel_leg_v3/augmented_wheel_leg_world_model_v1.py']
rows=[dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()) for p in inputs]
with (R/'SOURCE190_V2_BOUNDED_LOCAL_CPU_PURPOSE_FROZEN.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),
 purpose='Check native augmented WM on synthetic127/31/6 pairs and20ms boundary before any actual expert/model/SDK data admission',
 inputs=rows,source_directory=str(source),synthetic_envs=4,window=32,batch=4,hidden=[32,32],optimizer_updates=1,
 maximum_CPU_seconds=90,model_checkpoint_reads=0,raw_NPZ_reference_reads=0,SDK_GPU_remote_calls=0,
 actual_skill_or_native_policy_training=False,production512_memory_not_tested=True),f,indent=2)
print(json.dumps(dict(prepared=True,inputs=len(rows))))
