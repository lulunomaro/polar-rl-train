"""Read-only cross-project support audit and causal replay of archived sensors."""
import json
from pathlib import Path
import numpy as np
import torch
from fsm_paths import HERE, SOFT_DIR
from fsm_io import put, sha256
from manual_fsm_core import DetectorConfig, ManualFSM, Phase


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    torch.set_num_threads(1)
    baseline = read(SOFT_DIR/'BASELINE_AUDIT.json')
    stage1 = read(SOFT_DIR/'STAGE1_RESULT.json')
    sources = [(name, data['rows']) for name,data in baseline['policies'].items()]
    for name,key in (('softmoe_r9','parent_heldout'),('softmoe_r10','heldout_path')):
        data=read(SOFT_DIR/stage1[key])
        policy=next(iter(data['policies'].values()))
        sources.append((name,policy['rows']))
    audit=[]
    for name,rows in sources:
        stairs=[r for r in rows if r['course'] not in ('flat60','flat','rough_L9')]
        audit.append(dict(policy=name,total=len(rows),passed=sum(bool(r['passed']) for r in rows),
            stair_total=len(stairs),stair_passed=sum(bool(r['passed']) for r in stairs),
            nonstair_passed=sum(bool(r['passed']) for r in rows if r not in stairs)))
    put(HERE/'evidence/STAGE2_SUPPORT_CONTRACT_AUDIT.json',dict(rows=audit,
        baseline_sha256=sha256(SOFT_DIR/'BASELINE_AUDIT.json'),
        historical_contract='160 consecutive raw 2.5 ms samples; not the 20 ms mean-load acceptance contract',
        formal_contract='400 Hz signed normal forces -> nonoverlapping 8-substep means, >5 N each wheel, >=20 final windows after E0 handoff; >=5 first-tread windows on doubles',
        interpretation='The archived obstacle scores are all zero under the raw-substep contract; nonstair successes cannot establish obstacle competence.'))

    folder=HERE/'evidence/stair_r9_009m_contract'
    rows=[r for r in read(folder/'RESULT.json')['rows'] if not r.get('force_at_s')]
    raw=[]
    for r in rows:
        with np.load(folder/'traces'/(r['id']+'.npz')) as data:
            raw.append(data['control'].copy())
    longest=max(map(len,raw))
    frames=np.stack([np.pad(x[:,1:36],((0,longest-len(x)),(0,0)),mode='edge') for x in raw])
    c=DetectorConfig(**read(HERE/'DETECTOR.json')['config'])
    fsm=ManualFSM(len(rows),config=c)
    first=np.full(len(rows),np.nan)
    false=np.zeros(len(rows),dtype=int)
    reasons=np.zeros(len(rows),dtype=int)
    with torch.inference_mode():
        for tick in range(longest):
            obs=torch.tensor(frames[:,tick],dtype=torch.float32)
            phase=fsm.update(obs,mode=True,forward=obs[:,0]>.01)
            hit=(phase.numpy()==Phase.STAIR_CLIMB_ACTIVE)&np.isnan(first)
            for i in np.flatnonzero(hit):
                if tick>=len(raw[i]):continue
                first[i]=float(raw[i][tick,0]-.02)
                reasons[i]=int(fsm.trigger_reason[i])
                face=rows[i]['first_face_contact_s']
                false[i]=int(raw[i][tick,48]>.10 and (face is None or first[i]<face))
    results=[]
    for i,r in enumerate(rows):
        face=r['first_face_contact_s']
        t=None if np.isnan(first[i]) else float(first[i])
        results.append(dict(id=r['id'],course=r['course'],dr=r['dr'],speed=r['speed'],
            archived_first_climb_s=r['first_climb_s'],first_face_contact_s=face,
            replay_first_climb_s=t,reason=int(reasons[i]),precontact_false_trigger=bool(false[i]),
            delay_ms=1000*(t-face) if t is not None and face is not None else None))
    put(HERE/'evidence/STAGE2_DETECTOR_ARCHIVE_REPLAY.json',dict(rows=results,
        false_cases=int(false.sum()),cases=len(rows),
        limitation='Replay of archived observations only; closed-loop new-policy verification remains necessary.'))
    print(json.dumps(audit,indent=2))
    print('Replay false cases:',int(false.sum()))
    for r in results:
        if r['id']=='stair_0052_rm27_west_dr3141' or (r['course'] in ('rm27_west','rm27_east') and not r['dr']):
            print(r)


if __name__=='__main__':main()
