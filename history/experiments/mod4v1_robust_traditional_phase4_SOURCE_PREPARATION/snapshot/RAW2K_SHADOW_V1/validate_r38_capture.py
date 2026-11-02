"""Independent structural/source/mean QA of NEW R38 data, no physics replay.
Reads raw for schema/time/consumer-contract validation, not archive-only hashing.
Only the allowlisted shadow file is admitted as future estimator input.
"""
from pathlib import Path
import hashlib
import itertools
import json
import sys
import numpy as np
HERE=Path(__file__).resolve().parent
R=HERE.parent
sys.path.insert(0,str(HERE))
from publisher import validate_projection
D=HERE/'capture_qa001'
D.mkdir(parents=True,exist_ok=False)
batch=json.loads((R/'batches/r38_raw2k_shadow6/BATCH_RESULT.json').read_bytes())
reports=[]
manifest=[]
checks=0

def check(value):
    global checks
    checks+=1
    assert value,checks

for index,case in enumerate(batch['rows']):
    folder=R/'results'/case['case']
    previous_source=None
    payloads={}
    frames=0;duplicates=0;boot=0;total_samples=0;unique_samples=0
    mean_error={k:0. for k in ('gyro_body','accel_proper_body','joint_vel4','wheel_vel2')}
    source_ages=set()
    mapping={'gyro_body':'raw_gyro','accel_proper_body':'raw_accel','joint_vel4':'encoder_rate4','wheel_vel2':'wheel_rate2'}
    with(folder/'sensor_shadow.jsonl').open('r',encoding='utf-8')as sf,(folder/'trace.jsonl').open('r',encoding='utf-8')as tf:
        for sr,tr in itertools.zip_longest(sf,tf):
            check(sr is not None and tr is not None)
            frame=json.loads(sr);trace=json.loads(tr)
            check(validate_projection(frame))
            source=frame['source_epoch_us']
            check(source==int(round(trace['sensor_timestamp_s']*1e6)))
            check(frame['arrival_us']==int(round(trace['estimate_time']*1e6)))
            check(previous_source is None or source>=previous_source)
            previous_source=source
            source_ages.add(frame['arrival_us']-source)
            frames+=1;boot+=frame['mean_mode']==0
            total_samples+=len(frame['samples'])
            if source in payloads:
                check(payloads[source]==frame['payload_SHA'])
                check(frame['duplicate_source']is True)
                duplicates+=1
            else:
                check(frame['duplicate_source']is False)
                payloads[source]=frame['payload_SHA']
                unique_samples+=len(frame['samples'])
            for key,tracekey in mapping.items():
                authoritative=np.asarray(trace[tracekey],float)
                check(np.array_equal(authoritative,np.asarray(frame['mean'][key])))
                mean=np.mean([s[key]for s in frame['samples']],axis=0)
                error=float(np.max(np.abs(mean-authoritative)))
                mean_error[key]=max(mean_error[key],error)
                check(error<=4e-12*(1.+float(np.max(np.abs(authoritative)))))
            check(np.array_equal(np.asarray(frame['endpoint_joint_pos4']),np.asarray(trace['encoder4'])))
    check(frames==case['controls']==case['shadow']['frames'])
    check(duplicates==case['publisher']['duplicate_frames'])
    check(not case['publisher']['fault_latched'])
    report=dict(case=case['case'],frames=frames,boot_frames=boot,duplicate_source_frames=duplicates,unique_source_windows=len(payloads),published_samples_including_repeated_boot=total_samples,unique_source_samples=unique_samples,source_age_us=sorted(source_ages),maximum_recomputed_mean_error=mean_error,packet_mean_array_exact=True,projection_valid=True,raw_read_purpose='new schema/time/source/mean QA not archive-only rehash',no_full_raw_SHA_recomputed=True)
    reports.append(report)
    manifest.append(dict(id=f'C{index}',path=str(folder/'sensor_shadow.jsonl'),frames=frames,bytes=case['shadow']['bytes'],producer_SHA=case['shadow']['SHA'],payload='only allowlisted noisy sensors/time/quality; no truth/DR/clean/offset',controller_use='not used for original actuation',hardware_binding=False))
result=dict(kind='R38_NEW_INFORMATION_SHADOW_CAPTURE_QA',checks=checks,failures=0,physics_cases=6,physics_steps_already_executed=batch['physics_steps'],new_physics_steps_during_QA=0,control_frames=batch['shadow_frames'],all_complete=all(r['complete']for r in batch['rows']),base_screen_pass=all(r['base_gate']for r in batch['rows']),not_new_control_or_hardware_qualification=True,published_samples=sum(r['published_samples_including_repeated_boot']for r in reports),unique_source_samples=sum(r['unique_source_samples']for r in reports),cases=reports)
with(D/'RESULT.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
with(HERE/'SENSOR_ONLY_MANIFEST.json').open('x',encoding='utf-8')as f:json.dump(dict(kind='ONLY_R38_SENSOR_SHADOW_PATHS_ADMITTED_NO_PRIVATE_TRACE',information_enhancement=True,correlated_window_noise=True,hardware_binding=False,actuation_used=False,files=manifest,consumer_notes=['Discard/deduplicate instant boot when joining contiguous mean-mode1 samples.','2k sample q/qd/gyro/proper align at dynamics-stage pre-step time; final sample=source epoch-500us.','Original endpoint_joint_pos4 is at source epoch; original mean qd/gyro is not instantaneous endpoint velocity.','Select aligned 2k endpoint samples for window identities; do not mix q endpoint with old mean rates as synchronized.','Common offset cancels within-window differences, exposing extra information; across-window offsets still jump.','Only bounds/trust gates explicitly validated later may become cues; original confidence caps remain unchanged.']),f,indent=2)
with(R/'reports/R38_RAW2K_SHADOW_FACTS.json').open('x',encoding='utf-8')as f:json.dump(result,f,indent=2)
print(json.dumps(result,indent=2))
