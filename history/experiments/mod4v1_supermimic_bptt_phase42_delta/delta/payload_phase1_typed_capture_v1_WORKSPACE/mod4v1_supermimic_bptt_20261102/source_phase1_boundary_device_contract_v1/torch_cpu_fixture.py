"""Parent-run SYNTHETIC Torch CPU fixture; this SOURCE package never runs Torch.

Caller supplies the already-imported CPU Torch module and optionally the complete
fixed canonical source path. No SDK/bridge/env construction, GPU, model or files
other than the canonical Python source are needed during this function.
"""
import random
from boundary_device_contract import load_full_canonical


def run_torch_cpu_fixture(torch_module,canonical_source=None):
    t=torch_module
    core,source=load_full_canonical(canonical_source)
    cpu=t.device('cpu')
    python_rng_before=random.getstate()
    torch_rng_before=t.get_rng_state().clone()
    term=t.zeros(80,dtype=t.bool,device=cpu);trunc=t.zeros(80,dtype=t.bool,device=cpu)
    term[::3]=True;trunc[1::5]=True
    term_before=term.clone();trunc_before=trunc.clone();term_id=id(term);trunc_id=id(trunc)
    action=t.zeros((80,6),dtype=t.float32,device=cpu)
    expected=(term|trunc).clone()
    assert tuple(term.shape)==tuple(trunc.shape)==(80,) and term.dtype==trunc.dtype==t.bool
    assert term.device==trunc.device==cpu and term.device!='cpu'

    def rejects(fn):
        try:fn()
        except core.IntegrationError as exc:return str(exc)
        raise AssertionError('original strict canonical predicate unexpectedly accepted negative case')

    # Explicit synthetic old worker contract: string device, CPU tensors.
    old=core.OriginalEpisodeBoundary(t,'cpu',n=80)
    old_mask=old.for_action()
    assert bool(old_mask.all()) and old_mask is old.next_start
    old_steps=0
    def old_step(received):
        nonlocal old_steps
        assert received is action;old_steps+=1
        return term,trunc
    original_term,original_trunc=old_step(action)
    assert original_term is term and original_trunc is trunc
    old_error=rejects(lambda:old.after_original_step(original_term,original_trunc))
    assert old_error=='separate original bool term/trunc N80 required' and old_steps==1

    # Match the original bridge's preexisting normalized device, not env getter.
    synthetic_existing_bridge_device=cpu
    fixed=core.OriginalEpisodeBoundary(t,synthetic_existing_bridge_device,n=80)
    steps=0
    def original_step(received):
        nonlocal steps
        assert received is action;steps+=1
        return term,trunc
    initial=fixed.for_action()
    assert initial is fixed.next_start and bool(initial.all())
    flags=original_step(action)
    assert flags[0] is term and flags[1] is trunc
    fixed.after_original_step(*flags)
    assert t.equal(fixed.next_start,expected) and fixed.next_start is not term and fixed.next_start is not trunc
    following=fixed.for_action()
    assert following is fixed.next_start and t.equal(following,expected)
    flags=original_step(action);fixed.after_original_step(*flags)
    receipt=fixed.receipt()
    assert steps==receipt['actions']==receipt['original_step_transitions']==2
    assert receipt['pending_original_step'] is False and t.equal(fixed.next_start,expected)

    negative_errors={}
    for label,bad in (('shape79',t.zeros(79,dtype=t.bool,device=cpu)),
                      ('shape80x1',t.zeros((80,1),dtype=t.bool,device=cpu)),
                      ('float32',t.zeros(80,dtype=t.float32,device=cpu)),
                      ('int32',t.zeros(80,dtype=t.int32,device=cpu))):
        boundary=core.OriginalEpisodeBoundary(t,cpu,n=80);boundary.for_action()
        negative_errors[label]=rejects(lambda:boundary.after_original_step(bad,trunc))
        boundary=core.OriginalEpisodeBoundary(t,cpu,n=80);boundary.for_action()
        negative_errors[label+'_truncated']=rejects(lambda:boundary.after_original_step(term,bad))
    boundary=core.OriginalEpisodeBoundary(t,cpu,n=80)
    negative_errors['step_without_action']=rejects(lambda:boundary.after_original_step(term,trunc))
    boundary.for_action();negative_errors['two_actions_without_step']=rejects(boundary.for_action)
    negative_errors['non_N80']=rejects(lambda:core.OriginalEpisodeBoundary(t,cpu,n=79))
    assert id(term)==term_id and id(trunc)==trunc_id
    assert t.equal(term,term_before) and t.equal(trunc,trunc_before)
    assert t.equal(t.get_rng_state(),torch_rng_before) and random.getstate()==python_rng_before
    return dict(kind='PHASE1_BOUNDARY_DEVICE_SYNTHETIC_TORCH_CPU_V1',scope='SYNTHETIC_CPU_ONLY_NOT_SDK_NOT_ACTUAL_V3_FLAGS',
        canonical=source,Torch_version=str(t.__version__),num_envs=80,device='cpu',
        complete_original_module_and_class=True,canonical_predicate_unchanged=True,
        old_string_device_reproduced=True,old_error=old_error,old_attempted_action_steps=(1,old_steps),
        existing_normalized_device_passed=True,positive_original_step_calls=steps,boundary=receipt,
        first_mask_all_true=True,next_mask_true_term_OR_true_trunc=True,
        negative_cases=len(negative_errors),negative_errors=negative_errors,
        original_input_objects_identical=True,input_values_unchanged=True,
        global_Torch_CPU_RNG_unchanged=True,global_Python_RNG_unchanged=True,
        actual_env_device_type=None,actual_V3_flags_shape_dtype_device=None,
        actual_V3_root_cause_confirmed=False,SDK_or_native=False,model_PT_reads=0,GPU_operations=0)


def main(argv=None):
    """Explicit parent CLI; never called by SOURCE audit/import."""
    import argparse
    import json
    from pathlib import Path
    parser=argparse.ArgumentParser(description='Synthetic CPU device contract; not SDK/native flags')
    parser.add_argument('--canonical-source',required=True,help='Complete fixed 37927-byte/7a092 canonical Python module')
    parser.add_argument('--output',help='Optional NEW .json receipt, exclusive creation; otherwise stdout only')
    args=parser.parse_args(argv)
    load_full_canonical(args.canonical_source)  # Full pin before Torch import.
    target=Path(args.output) if args.output else None
    if target is not None and (target.suffix!='.json' or target.exists()):raise ValueError('new JSON receipt path required')
    import torch
    receipt=run_torch_cpu_fixture(torch,args.canonical_source)
    text=json.dumps(receipt,indent=2,allow_nan=False)+'\n'
    if target is not None:
        with target.open('x',encoding='utf-8') as stream:stream.write(text)
    print(text,end='')
    return receipt


if __name__=='__main__':main()
