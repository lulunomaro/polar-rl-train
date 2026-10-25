"""V2 context proof and synthetic fixture only; never reads the real bank."""
import os
os.environ['CUDA_VISIBLE_DEVICES']=''
import ast,hashlib,importlib.util,json,sys,time,traceback
from pathlib import Path
from unittest import mock
import numpy as np
import torch

B=Path(__file__).resolve().parent;V1=B.parent
E=B/'payloads/recovery/job0/runtime/isaac/mod4'
sys.path.insert(0,str(B/'verification/original_sources'))
R=B/'reports/V2_CONTEXT_AST_SYNTHETIC_CPU_ACTUAL.json'


def mod(name,path):
    spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec)
    sys.modules[name]=m;spec.loader.exec_module(m);return m


def dump(tree):return ast.dump(tree,include_attributes=False)


def H(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    assert not R.exists(),'Never overwrite an original attempt'
    report=dict(trial_id='MOD4_SAMPLING_IMPLEMENTATION_V2_CONTEXT_CPU_20261025',epoch=time.time(),status='running',
                device='cpu',no_GPU_SDK_policy_physics_or_host=True,actual_32MB_bank_read_count=0,
                real_bank_evidence=str(V1/'reports/INTEGRATED_H1_E3_REAL_BANK_CPU_V1_ACTUAL.json'),Git='pending root')
    def put():R.write_text(json.dumps(report,indent=2),encoding='utf8')
    put()
    try:
        torch.set_num_threads(1)
        oldcache=V1/'payloads/recovery/job0/runtime/isaac/mod4/e3_reset_bank_cache_v1.py'
        newcache=E/'e3_reset_bank_cache_v1.py'
        oldtree,newtree=ast.parse(oldcache.read_text()),ast.parse(newcache.read_text())
        cls=next(n for n in newtree.body if isinstance(n,ast.ClassDef) and n.name=='E3ResetBankCache')
        init=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
        assert [dump(n) for n in init.decorator_list]==[dump(ast.parse('torch.inference_mode(False)',mode='eval').body),dump(ast.parse('torch.no_grad()',mode='eval').body)]
        init.decorator_list=[]
        assert dump(newtree)==dump(oldtree),'V2 cache changed beyond constructor context decorators'
        helper_rel='payloads/h1/sampling_trace_npz_lossless_v1.py'
        a,b=ast.parse((V1/helper_rel).read_text()),ast.parse((B/helper_rel).read_text())
        assert isinstance(a.body[0],ast.Expr) and isinstance(b.body[0],ast.Expr)
        a.body=a.body[1:];b.body=b.body[1:];assert dump(a)==dump(b)
        for rel in ('payloads/h1/h1_production_control_prefix_trace_v1.py','payloads/recovery/job0/runtime/isaac/mod4/e3_recovery_runtime_v1.py'):
            assert (B/rel).read_bytes()==(V1/rel).read_bytes()
        report['AST_proof']=dict(cache_only_two_constructor_context_decorators_changed=True,H1_helper_docstring_only=True,
                                 both_integrated_runtime_sources_byte_identical_to_V1=True,
                                 all_V1_AST_allowlist_and_real_bank_output_evidence_transferred_by_unchanged_code=True)
        # Use an explicitly separate synthetic bank to exercise context construction.
        # Test-only expected constants are monkeypatched, never written into payload.
        evidence=json.loads((V1/'reports/INTEGRATED_H1_E3_REAL_BANK_CPU_V1_ACTUAL.json').read_text())
        names=evidence['actual_bank']['bank_joint_names']
        folder=B/'cpu_fixtures';folder.mkdir(exist_ok=False)
        fixture=folder/'SYNTHETIC_BANK_FOR_CONTEXT.npz'
        rng=np.random.Generator(np.random.PCG64(20261025))
        np.savez_compressed(fixture,root_height=np.array([.2,.25,.3]),joint_names=np.array(names),
                            q=rng.normal(size=(3,30)),points_root=rng.normal(size=(3,25200,3)).astype(np.float32)*.25)
        fixture_sha=H(fixture);fixture_bytes=fixture.stat().st_size
        module_v1=mod('cache_v1_rejected_inference_fixture',oldcache)
        module_v2=mod('cache_v2_context_candidate',newcache)
        cpu_before=torch.random.get_rng_state().clone();np_before=np.random.get_state()
        with mock.patch.object(module_v1,'EXPECTED_BANK_SHA',fixture_sha),mock.patch.object(module_v1,'EXPECTED_BANK_BYTES',fixture_bytes):
            try:
                with torch.inference_mode():module_v1.E3ResetBankCache(fixture,names,'cpu')
            except RuntimeError:
                report['V1_original_inference_constructor_error']=traceback.format_exc()
                assert 'Inference tensors do not track version counter' in report['V1_original_inference_constructor_error']
            else:raise AssertionError('V1 inference hazard was not reproduced')
        report['context_cases']=[]
        with mock.patch.object(module_v2,'EXPECTED_BANK_SHA',fixture_sha),mock.patch.object(module_v2,'EXPECTED_BANK_BYTES',fixture_bytes):
            reference=None
            for inference_construct in (False,True):
                with torch.inference_mode(inference_construct):cache=module_v2.E3ResetBankCache(fixture,names,'cpu')
                versions=[value._version for value in (cache._q,cache._quat,cache._minimum,cache._initial)]
                recipe=torch.arange(520,dtype=torch.long)%13
                with torch.inference_mode():selected=cache.selected_geometry(recipe,names)
                cache.validate(names)
                if reference is None:reference=[x.clone() for x in selected]
                else:assert all(torch.equal(a,b) and a.dtype==b.dtype and a.shape==b.shape for a,b in zip(reference,selected))
                # Fresh returned tensors have no aliases into protected normal caches.
                before=cache._q.clone();selected[0].zero_();assert torch.equal(before,cache._q)
                cache.validate(names)
                cache._minimum.add_(1.)
                try:cache.validate(names)
                except RuntimeError:mutation_rejected=True
                else:raise AssertionError('Context wrapper weakened cache immutability')
                report['context_cases'].append(dict(inference_mode_during_constructor=inference_construct,
                   inference_mode_during_selection=True,cache_has_version_counters=versions,
                   normal_and_inference_outputs_equal=True,selected_mutation_does_not_alias_cache=True,
                   cache_inplace_mutation_rejected=mutation_rejected))
        assert torch.equal(cpu_before,torch.random.get_rng_state())
        np_after=np.random.get_state();assert np_before[0]==np_after[0] and np.array_equal(np_before[1],np_after[1]) and np_before[2:]==np_after[2:]
        report.update(status='V2_context_AST_and_synthetic_inference_checks_passed',
                      synthetic_fixture=dict(path=str(fixture),bytes=fixture_bytes,SHA=fixture_sha,test_constants_patched_only_in_memory=True),
                      global_CPU_torch_and_numpy_RNG_unchanged=True,
                      actual_robot_joint_order_unknown_until_installed_source_receipt=True,
                      evidence_scope='V1 actual bank normal-mode source comparison; V2 only context AST change; synthetic V2 inference compatibility. No actual CUDA/SDK claim.',
                      source_SHA=dict(old_cache=H(oldcache),new_cache=H(newcache)),completed_epoch=time.time())
        put();print(json.dumps(report))
    except BaseException:
        report.update(status='original_error_retained',original_error=traceback.format_exc());put();raise


if __name__=='__main__':main()
