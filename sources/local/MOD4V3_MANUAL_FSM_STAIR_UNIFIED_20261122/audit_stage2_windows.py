"""Independently rebuild both support metrics from saved 400 Hz force traces."""
from argparse import ArgumentParser
from pathlib import Path
import json
import numpy as np
from fsm_paths import HERE
from fsm_io import put


def longest(samples):
    count=np.zeros(samples.shape[1],dtype=np.int64);peak=count.copy()
    for row in samples:
        count=np.where(row,count+1,0)
        peak=np.maximum(peak,count)
    return peak.tolist()


def main():
    p=ArgumentParser(description=__doc__);p.add_argument('folder',type=Path);args=p.parse_args()
    rows=json.loads((args.folder/'RESULT.json').read_text())['rows'];out=[]
    for row in rows:
        with np.load(args.folder/'traces'/(row['id']+'.npz')) as data:
            trace=data['reference_trace'];physics=data['physics']
        stages=max(1,len(row['stage_crossed']))
        forces=trace[:,21:21+stages*2].reshape(-1,stages,2)
        assert len(forces)%8==0
        recovered=np.isin(physics[:,1],(0,1,4))
        mean=forces.reshape(-1,8,stages,2).mean(1)
        eligible=recovered.reshape(-1,8).all(1)
        windows=longest((mean>5.).all(2))
        e0_windows=longest((mean>5.).all(2)&eligible[:,None])
        raw=longest((forces>5.).all(2))
        raw_e0=longest((forces>5.).all(2)&recovered[:,None])
        body_edge=physics[:,11] if physics.shape[1]>11 else trace[:,11:13].max(1)
        body_crossed=bool((physics[:,10]>body_edge).any())
        final=None
        if stages==2:
            final_mean=physics[:,7:9].reshape(-1,8,2).mean(1)
            geometry=physics[:,9].astype(bool).reshape(-1,8).all(1)
            final=longest(((final_mean>5.).all(1)&eligible&geometry)[:,None])[0]
        passed=(windows==row['longest_bilateral_support_windows_20ms'] and
                e0_windows==row['longest_e0_bilateral_support_windows_20ms'] and
                raw==row['raw_contiguous_2p5ms_substeps']['all_phases'] and
                raw_e0==row['raw_contiguous_2p5ms_substeps']['e0'] and
                (final is None or final==row['final_deck_best_windows_20ms']))
        out.append(dict(id=row['id'],passed=passed,windows=windows,e0_windows=e0_windows,
            body_first_edge_crossed=body_crossed,strict_pass_requires_body_crossing=not row['passed'] or body_crossed,
            final_e0_windows=final,raw_substeps=raw,raw_e0_substeps=raw_e0,samples=len(forces)))
    result=dict(passed=all(r['passed'] for r in out),cases=len(out),
        all_recorded_strict_passes_have_body_crossing=all(r['strict_pass_requires_body_crossing'] for r in out),
        mean_window_substeps=8,physics_hz=400,control_hz=50,
        no_substep_omission=True,nonoverlapping_windows=True,rows=out)
    put(args.folder/'WINDOW_RECONSTRUCTION_AUDIT.json',result)
    print('Independent raw/window reconstruction:',sum(r['passed'] for r in out),'/',len(out))
    if not result['passed']:raise RuntimeError('Saved force traces disagree with the evaluator')


if __name__=='__main__':main()
