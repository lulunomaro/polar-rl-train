"""New publisher mathematical/schema/queue tests only; zero MuJoCo/physics.
Mock clean samples stay producer-side. No original benchmark is replayed.
"""
from pathlib import Path
from types import SimpleNamespace
import copy
import hashlib
import json
import traceback
import numpy as np
from publisher import CHANNELS,MEAN_KEYS,ROOT_KEYS,ShadowPublisher,validate_projection
D=Path(__file__).resolve().parent/'attempts/001'
D.mkdir(parents=True,exist_ok=False)
checks=0

def check(condition):
    global checks
    checks+=1
    assert condition,checks

def fails(function):
    global checks
    checks+=1
    try:function()
    except (ValueError,TypeError):return
    raise AssertionError(('expected invalid',checks))

def window(epoch,instant=False):
    count=1 if instant else 20
    begin=epoch if instant else epoch-10000
    records=[]
    for i in range(count):
        values={k:(np.arange(n)*.07+np.sin(i*.13)*.012+epoch*1e-7).tolist()for k,n in CHANNELS.items()}
        stamp=epoch if instant else begin+500*i
        values.update(sampled_us=stamp,encoder_pos_sampled_us=stamp,encoder_rate_sampled_us=stamp)
        records.append(values)
    mean={k:np.mean([r[k]for r in records],axis=0)for k in MEAN_KEYS}
    endpoint=np.asarray(records[-1]['joint_pos4'])+(0. if instant else .001)
    offsets={k:np.linspace(-.1,.1,n)for k,n in CHANNELS.items()}
    offsets['joint_pos4']=np.array([.006,-.004,.008,-.003])
    return records,mean,endpoint,offsets

def packet(epoch,arrival,mean,endpoint,offsets):
    values={k:mean[k]+offsets[k]for k in MEAN_KEYS}
    values['joint_pos4']=endpoint+offsets['joint_pos4']
    return SimpleNamespace(time_s=epoch*1e-6,arrival_s=arrival*1e-6,validity=True,**values)

source=[]
for p in (Path(__file__),Path(__file__).resolve().parent/'publisher.py'):
    raw=p.read_bytes();source.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
with(D/'SOURCE_PREEXEC.json').open('x',encoding='utf-8')as f:json.dump(source,f,indent=2)
try:
    pub=ShadowPublisher()
    r0,m0,q0,b0=window(0,True)
    pub.register(0,0,r0,m0,q0,True)
    p0=packet(0,0,m0,q0,b0)
    out0=pub.publish(p0)
    check(validate_projection(out0))
    check(out0['count']==1 and out0['mean_mode']==0 and out0['sample_weight_us']==0)
    check(set(out0)==ROOT_KEYS)
    check(out0['hardware_binding']is False and out0['actuation_used']is False)
    r1,m1,q1,b1=window(10000)
    pub.register(10000,0,r1,m1,q1)
    delayed_boot=pub.publish(packet(0,10000,m0,q0,b0))
    check(delayed_boot['source_epoch_us']==0 and delayed_boot['arrival_us']==10000)
    check(delayed_boot['duplicate_source']is True)
    check(delayed_boot['sequence']==out0['sequence'])
    check(delayed_boot['payload_SHA']==out0['payload_SHA'])
    check(delayed_boot['samples']==out0['samples'])
    out0['samples'][0]['gyro_body'][0]=777.
    same_again=pub.publish(packet(0,10000,m0,q0,b0))
    check(same_again['samples']==delayed_boot['samples'])
    r2,m2,q2,b2=window(20000)
    pub.register(20000,10000,r2,m2,q2)
    out1=pub.publish(packet(10000,20000,m1,q1,b1))
    check(out1['source_epoch_us']==10000 and out1['sequence']==2)
    check(out1['count']==20 and out1['aperture_us']==10000)
    check(out1['samples'][0]['sampled_us']==0 and out1['samples'][-1]['sampled_us']==9500)
    check(out1['endpoint_joint_pos4']==(q1+b1['joint_pos4']).tolist())
    for k in MEAN_KEYS:
        error=float(np.max(np.abs(np.mean([s[k]for s in out1['samples']],axis=0)-np.asarray(out1['mean'][k]))))
        check(error<1e-12)
    for k in CHANNELS:
        differences=np.asarray([s[k]for s in out1['samples']])-np.asarray([r[k]for r in r1])
        check(np.max(np.abs(differences-b1[k]))<1e-12)
        check(np.max(np.abs(np.diff(np.asarray([s[k]for s in out1['samples']]),axis=0)-np.diff(np.asarray([r[k]for r in r1]),axis=0)))<1e-12)
    check(json.loads(json.dumps(out1))['mean']==out1['mean'])
    for name in ('clean','offset','root','contact','DR','seed','true_pose'):
        bad=copy.deepcopy(out1);bad[name]=0
        fails(lambda bad=bad:validate_projection(bad))
        bad=copy.deepcopy(out1);bad['samples'][0][name]=0
        fails(lambda bad=bad:validate_projection(bad))
    for mutate in (lambda x:x['mean']['gyro_body'].__setitem__(0,float('nan')),lambda x:x.__setitem__('count',19),lambda x:x.__setitem__('dropped_count',1),lambda x:x['samples'][0].__setitem__('sampled_us',1),lambda x:x.__setitem__('payload_SHA','0'*64),lambda x:x.__setitem__('hardware_binding',True),lambda x:x.__setitem__('actuation_used',True),lambda x:x.__setitem__('arrival_us',30000)):
        bad=copy.deepcopy(out1);mutate(bad)
        fails(lambda bad=bad:validate_projection(bad))
    # Changed duplicate faults, and later correct input cannot silently clear it.
    broken=copy.deepcopy(packet(10000,20000,m1,q1,b1));broken.gyro_body[0]+=.001
    fails(lambda:pub.publish(broken))
    check(pub.fault_latched)
    fails(lambda:pub.publish(packet(10000,20000,m1,q1,b1)))
    fresh=ShadowPublisher()
    fresh.register(10000,0,r1,m1,q1)
    fails(lambda:fresh.register(10000,0,r1,m1,q1))
    invalid=copy.deepcopy(r1);invalid[3]['joint_pos4'][0]=float('nan')
    fails(lambda:ShadowPublisher().register(10000,0,invalid,m1,q1))
    invalid=copy.deepcopy(r1);invalid[4]['encoder_rate_sampled_us']+=500
    fails(lambda:ShadowPublisher().register(10000,0,invalid,m1,q1))
    fails(lambda:ShadowPublisher().register(10000,0,r1[:19],m1,q1))
    altered=copy.deepcopy(m1);altered['gyro_body'][0]+=.01
    fails(lambda:ShadowPublisher().register(10000,0,r1,altered,q1))
    unknown=ShadowPublisher();unknown.register(10000,0,r1,m1,q1)
    fails(lambda:unknown.publish(packet(0,10000,m0,q0,b0)))
    check(unknown.fault_latched)
    summary=dict(kind='RAW2K_PUBLISHER_MOCK_CONTRACT_ONLY_NOT_PHYSICS_OR_HARDWARE',checks=checks,failures=0,physics_steps=0,mean_preservation='roundoff bounded, not bit-identical',noise_model='one shared original post-mean offset per channel/window, not iid2k',within_window_differences_reveal_extra_information=True,projection_unknown_fields_rejected=True,changed_duplicates_latch=True,receipt=pub.receipt(),source=source)
    with(D/'RESULT.json').open('x',encoding='utf-8')as f:json.dump(summary,f,indent=2,allow_nan=False)
    print(json.dumps(summary,indent=2))
except BaseException:
    with(D/'ERROR.txt').open('x',encoding='utf-8')as f:f.write(traceback.format_exc())
    raise
