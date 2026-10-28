"""Synthetic sampler plumbing and actual closed93 evidence, no model access."""
from pathlib import Path
from types import SimpleNamespace
import ast, hashlib, json, os, sys, time
HERE=Path(__file__).resolve().parent; L=HERE.parent; T=L.parent
N=T/'MOD4_H1_FLAT05_TERMINAL_EXPOSURE_RESOURCE_V93_20261028'
P=N/'payloads/h1/source'

def read(p): return json.loads(Path(p).read_bytes())
def put(name, value):
    with (HERE/name).open('x',encoding='utf8') as f:
        json.dump(value,f,indent=2,ensure_ascii=False,allow_nan=False)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
    put('SOURCE_CPU_STARTED_ACTUAL.json',dict(epoch=time.time(),models_read=0,source_only=True))
    import torch
    sys.path[:0]=[str(HERE),str(P)]
    from flat95_task_focused_starts_v1 import focused_mask,attach_task_focused_starts,CONTRACT
    from private_phase_frame_v1 import encode
    done=read(N/'reports/THREE93_COMPLETE_FINALS_OR_PARTIALS_ORIGINAL_COST_RETURNED_ACTUAL_V1.json')
    cpu=read(N/'reports/NATIVE93_FORMAL_NATIVE_FULLSTATE_INITIAL_CPU_AND_COST_ACTUAL.json')
    events=read(N/'reports/NATIVE93_FORMAL_COMPLETED_PHYSICS_EVENTS_TEXT_SCOPE_ACTUAL.json')
    assert cpu['passed'] and done['canonical_None'] and events['coverage_matches_complete_controls']
    pub=done['published']['h1']; count=cpu['progress']['counters']
    assert count['native_iteration']==10692 and count['world_updates']==106920 and count['policy_updates']==10372
    covrow=next(r for r in done['all_original_texts_full_case_safe'] if r['relative'].endswith('/NATIVE_POLICY_PHASE_SAMPLE_COVERAGE_ACTUAL.json'))
    coverage=read(covrow['local_path']); assert coverage['diagnostic_valid'] and not coverage['errors']
    frames=encode(torch.tensor([179,180,200,220,221,429,430,450,470,471,499,500]),torch.zeros(12,dtype=torch.long))
    assert focused_mask(frames).tolist()==[False,True,True,True,False,False,True,True,True,False,False,False]
    delayed=encode(torch.tensor([242,243,263,283,284]),torch.full((5,),63,dtype=torch.long))
    assert focused_mask(delayed).tolist()==[False,True,True,True,False]
    assert not focused_mask(torch.tensor([-1,256*1024+200])).any()
    scopes=['actual_closed93_and_method_lineage_metadata','exact_private_delay_and_preparation_flight_boundaries']
    def make(frames):
        learner=SimpleNamespace(); state={'draws':0}; originals=[]
        def sample(n):
            state['draws']+=1
            f=frames[:n].clone(); ids=torch.arange(n)+state['draws']*10000
            start=dict(f=f,s=torch.stack((ids,ids+1000),-1),done=torch.zeros(n,dtype=torch.bool))
            history=dict(f=f[:,None].expand(n,3).clone(),s=ids[:,None,None].expand(n,3,2).clone())
            originals.append((start,history,{k:v.clone() for k,v in start.items()},{k:v.clone() for k,v in history.items()}))
            return start,history
        learner._sample_valid_starts=sample
        return learner,state,originals
    l,s,originals=make(torch.tensor([200,201,202,203,10,11,12,13]))
    notices=[]; totals=attach_task_focused_starts(l,diagnostic=notices.append); a,h=l._sample_valid_starts(8)
    assert s['draws']==1 and totals['selected_focus']==4 and totals['returned_starts']==8
    assert torch.equal(a['s'][:,0],h['s'][:,0,0]) and torch.equal(a['f'],h['f'][:,0])
    for x,y,bx,by in originals:
        assert all(torch.equal(x[k],v) for k,v in bx.items()) and all(torch.equal(y[k],v) for k,v in by.items())
    scopes.append('focused_half_paired_rows_and_original_input_immutability')
    l,s,_=make(torch.tensor([200,10,11,12,13,14,15,16])); totals=attach_task_focused_starts(l)
    a,h=l._sample_valid_starts(8)
    assert s['draws']==4 and totals['selected_focus']==4 and torch.equal(a['s'][:,0],h['s'][:,0,0])
    scopes.append('focused_rows_from_multiple_original_draws_keep_histories_paired')
    l,s,_=make(torch.arange(8)); totals=attach_task_focused_starts(l); a,h=l._sample_valid_starts(8)
    assert s['draws']==8 and totals['selected_focus']==0 and totals['fallback_uniform']==4
    assert torch.equal(a['s'][:,0],h['s'][:,0,0]) and a['f'].tolist()==list(range(8))
    scopes.append('bounded_eight_draw_uniform_fallback_no_hang_or_fake_transition')
    try: attach_task_focused_starts(l)
    except AssertionError: pass
    else: raise AssertionError('duplicate attachment accepted')
    assert not torch.cuda.is_initialized(); scopes.append('duplicate_attachment_rejected_and_CPU_only')
    put('SOURCE_CPU_ACTUAL.json',dict(passed=True,epoch=time.time(),source_only_not_installed=True,
        source_contract=CONTRACT,source_SHA=sha(HERE/'flat95_task_focused_starts_v1.py'),scopes=scopes,
        actual93_phase_coverage=coverage,actual93_flat_lifetime=events['original_events']['flat_real_physics_events']['lifetime'],
        actual93_full_coverage_controls=3654,qualified_method_source=pub,source_progress=count,
        requested_flight_start_fraction=coverage['bands']['requested_flight']/coverage['sampled_starts'],
        horizon_request_fraction=coverage['imagined_horizon_intersects_request']/coverage['sampled_starts'],
        hypothesis='Increase task-relevant BPTT start weight after full93 zero-takeoff result; this does not establish the sole failure cause or learning gain.',
        immutable_scopes=['WM architecture and training','Policy and Critic parameters','normalizer buffers','three optimizers','physical controls and resets','reward and goal schedule','terminal93 fix','real flat and270 success criteria'],
        integration_required=['new93->95 typed lineage and producer','saved learning seed27 vs physical seed','sourceSDK and full initial-state admission','bounded actualGPU window and real event validation'],
        no_model_read_hash_forward_GPU_physics_remote_or_budget_IO=True))
    put('HANDOFF.json',dict(selected_source=str(HERE/'flat95_task_focused_starts_v1.py'),source_CPU=str(HERE/'SOURCE_CPU_ACTUAL.json'),
        attach_after='install_restored_window and before attach_optional_policy_phase_coverage',
        task_GO_contract=CONTRACT,source_is_candidate_only=True,no95_payload_owner_GO_or_fee=True,
        source_learning_seed=27,physical_seed_must_be_separately_pinned=True,
        latest_qualified_native93_SHA=pub['SHA'],progress=count))
    rows=[]
    for p in sorted(HERE.iterdir()):
        if p.is_file(): rows.append(dict(path=p.name,bytes=p.stat().st_size,SHA=sha(p)))
    put('FROZEN_SOURCE_INDEX_ACTUAL.json',dict(frozen=True,entries=rows,models_read=0))
    print(json.dumps(dict(passed=True,source_only=True,CPU_scopes=len(scopes))))

if __name__=='__main__': main()
