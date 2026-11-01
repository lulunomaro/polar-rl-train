"""Verify planned endpoint hold behavior against all original real reference rows."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
from pathlib import Path
import hashlib,importlib.util,json,time,xml.etree.ElementTree as ET
N=Path(__file__).resolve().parent;T=N.parent;D=T/'REFERENCE_TERMINAL_HOLD_LABEL_REPAIR_V315_20261102';R=D/'reports'
def put(n,x):
    with(R/n).open('x',encoding='utf8')as f:json.dump(x,f,indent=2,ensure_ascii=False,allow_nan=False)
assert not(R/'CPU315_ONCE_CONSUMED.json').exists()
put('CPU315_ONCE_CONSUMED.json',dict(epoch=time.time(),purpose='Verify unused new terminal hold label against exact originalreference;0checkpoints/SDK/network/optimizer/physicalsteps'))
try:
    import numpy as np,torch
    def module(n,p):
        s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
    old=module('original315_reference',T/'REFERENCE_TRACKING_REAL_VALUE_V305_20261101/source/tracking_reference305.py')
    new=module('repaired315_reference',D/'source/tracking_reference315.py')
    task=json.loads((T/'REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V311_20261102/TASK311_FROZEN.json').read_bytes())
    refpath=T/'REFERENCE_INITIAL_STATE_PHYSICS_PROBE_V311_20261102/reference305.npz'
    with np.load(refpath,allow_pickle=False)as a:names=a['joint_names'].tolist()
    tree=ET.fromstring(Path('F:/RMPOLAR-RL/traditional_control_20261101/model/mod4_400N.xml').read_bytes());bodies={b.get('name'):b for b in tree.find('worldbody').iter('body')}
    hips=torch.tensor([[float(x)for x in bodies[s+'_thigh'].get('pos').split()]for s in('left','right')])
    a=old.Reference305(refpath,task['reference'],names,'cpu',hips);b=new.Reference315(refpath,task['reference'],names,'cpu',hips)
    phase=torch.arange(250);envs=torch.zeros(250,dtype=torch.long);target=torch.tensor([[.8,0.,.27,0.]])
    oldlabel=a.labels(phase,envs,target);newlabel=b.labels(phase,envs,target)
    assert all(torch.equal(oldlabel[k],newlabel[k])for k in oldlabel)
    hphase=torch.tensor([250,251,400,1000]);henv=torch.zeros(4,dtype=torch.long)
    held=b.labels(hphase,henv,target);before=a.labels(hphase,henv,target)
    assert torch.equal(held['state'][:,:12],before['state'][:,:12])and torch.equal(held['state'][:,18:48],before['state'][:,18:48])
    assert torch.count_nonzero(held['state'][:,12:18])==torch.count_nonzero(held['state'][:,48:78])==0
    assert all(torch.equal(held[k],before[k])for k in('wheel_world','L','theta','support','phase'))
    state=(held['state'][:,:3],held['state'][:,3:12].reshape(-1,3,3),held['state'][:,12:15],held['state'][:,15:18],held['state'][:,18:48],held['state'][:,48:78],torch.zeros(4,151))
    goals=b.goals(state,hphase,henv,target)
    assert goals.shape==(4,59)and torch.isfinite(goals).all()
    put('CPU315_TERMINAL_HOLD_LABEL_REPAIR_VALIDATION.json',dict(epoch=time.time(),passed=True,all250originalendpointlabels_byte_equal=True,holdphase=[250,251,400,1000],heldpose_joints_wheels_support_unchanged=True,held_rootlinear_angular_andjointvelocities_allzero=True,goal59_finite=True,physical_steps=0,SDK=0,model_reads=0,optimizer_steps=0,network=0,deployed=False,source314='terminal velocity .01091649m/s/angular.05253669rad/s/legdqmax.04481297 preservedbyoldclamp',actual_skill_change='not measured; no earlyfall cause claimed'))
    print(json.dumps(dict(passed=True,original250labels_unchanged=True,held_velocity_zero=True,model_reads=0,deployed=False)))
except BaseException:
    import traceback
    put('CPU315_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),consumed=True));raise
