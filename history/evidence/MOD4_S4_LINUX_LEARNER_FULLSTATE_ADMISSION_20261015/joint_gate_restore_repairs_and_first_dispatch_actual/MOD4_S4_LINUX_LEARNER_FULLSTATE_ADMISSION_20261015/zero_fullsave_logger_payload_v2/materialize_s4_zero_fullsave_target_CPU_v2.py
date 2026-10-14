"""New source-bound 20k native/fullrestore target. This entry point is CPU only."""
from pathlib import Path
import json,hashlib,os,sys,time,shutil,fcntl,subprocess,traceback

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):
    with Path(p).open('x') as f:json.dump(v,f,indent=2);f.flush();os.fsync(f.fileno())
def walk(x):
    import torch
    if torch.is_tensor(x):yield x
    elif isinstance(x,dict):
        for v in x.values():yield from walk(v)
    elif isinstance(x,(tuple,list)):
        for v in x:yield from walk(v)

def main(ctx):
    assert os.environ.get('CUDA_VISIBLE_DEVICES')==''
    root=Path(ctx['target_root']);stage=Path(ctx['upload_stage']);assert not root.exists()
    for name,h in ctx['files'].items():
        p=stage/name;assert p.resolve().is_relative_to(stage.resolve()) and sha(p)==h
        if p.suffix=='.py':compile(p.read_bytes(),str(p),'exec')
    sys.path.insert(0,str(stage));from s4_missing_zero_fullsave_parent_v2 import LOCKS,B,guard
    owned=[];created=False
    try:
        for p in LOCKS:
            f=p.open('r+b');fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB);owned.append(f)
        # guard() uses its own directory only for durable free; all target paths
        # are on the same authorized durable mount.
        resources=guard();budget_before=sha(B)
        import torch,inspect
        from rsl_rl.utils.logger import Logger
        assert sha(inspect.getfile(Logger))==ctx['actual_logger_source_SHA']
        first=Path('/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013/left_exploration20k_first_formal_v1')
        original=json.loads((first/'LEFT_FORMAL_ADMISSION_MANIFEST.json').read_bytes())
        assert len(original['sourcefreeze'])==522
        refs=ctx['refs'];assert refs[0]['sha256']=='b10958d2a8631b12c0f9502bf7fa9230d9a7a1ae9863443bb68388604bed61f8'
        assert refs[1]['sha256']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
        for r in refs:assert sha(r['local_path'])==r['sha256']
        w35=torch.load(refs[1]['local_path'],map_location='cpu',weights_only=False)
        tensors=list(walk(w35));floats=[v for v in tensors if v.is_floating_point()]
        assert len(floats)==102 and all(torch.isfinite(v).all() for v in floats)
        assert all(v.device.type=='cpu' for v in tensors)
        assert w35['sensor_DR_state']['n']==20000
        assert w35['E1_terrain_state']['profile']=='mod4_G3_CAD_derived_35mm_v1'
        assert w35['E1_terrain_state']['geometry_triangles_sha256']=='05a70e57eae5cd7a502324ad7c256ff2722b7043869b72524c6eb4516af6b419'
        assert w35['E1_terrain_state']['reset_bank_sha256']=='78af9fa47686204ef370271a2da580d762aa9fda1c7a49844ced318b264e6b83'
        assert w35['E1_retained_flat_command_state']['num_envs']==20000
        root.mkdir();created=True;runtime=root/'base_runtime';runtime.mkdir()
        rows=[]
        for row in original['sourcefreeze']:
            p=Path(row['path']);assert p.resolve().is_relative_to(first.resolve()) and sha(p)==row['sha256']
            relative=p.relative_to(first);out=runtime/relative;out.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,out)
            assert sha(out)==row['sha256'];rows.append(dict(path=str(out),relative=str(relative),bytes=out.stat().st_size,sha256=row['sha256']))
        for name,h in ctx['files'].items():shutil.copy2(stage/name,root/name);assert sha(root/name)==h
        # This is a complete original source roundtrip only, never a new training source.
        cpu_rng=torch.get_rng_state().clone();out=root/'W35_WHOLESTATE_CPU_EVIDENCE_NOT_SOURCE.pt';torch.save(w35,out)
        loaded=torch.load(out,map_location='cpu',weights_only=False)
        from s4_original_fullstate_migration_v1 import same
        assert same(w35,loaded)
        for a,b in zip(walk(w35),walk(loaded)):
            if a.numel():assert a.untyped_storage().data_ptr()!=b.untyped_storage().data_ptr()
        assert torch.equal(cpu_rng,torch.get_rng_state()) and not torch.cuda.is_initialized()
        manifest_path=Path(refs[1]['local_path']).parent/'run_manifest.json'
        assert sha(manifest_path)==ctx['original_W35_manifest_SHA']
        m=json.loads(manifest_path.read_bytes());environment=dict(m['env'])
        assert environment['RM_PHYSICS_DT_S']=='0.0025' and environment['RM_SOLVER_POS']=='32' and environment['RM_SOLVER_VEL']=='4'
        assert environment['RM_KEEP_STD']=='1' and environment['RM_SCHEDULE']=='adaptive'
        assert environment['RM_ENTROPY_COEF']=='0.005' and environment['RM_VALUE_LOSS_COEF']=='2.0'
        # Original source uses an absolute protected USD path; bind its actual bytes too.
        usd=Path(environment['RM_MOD4_USD']);assert usd.is_file()
        assert sha(B)==budget_before
        result=dict(epoch=time.time(),passed=True,target_root=str(root),approved_GPU_now=False,approved_PPO=False,
            native_fullrestore_cases_not_yet_dispatched=True,original_wholeW35_CPU_roundtrip_independent_storage=True,
            original_float_tensors=len(floats),original_all_tensors=len(tensors),original_perenv_tensors=sum(v.ndim>0 and v.shape[0]==20000 for v in tensors),
            refs=refs,original_environment=environment,original_manifest_SHA=sha(manifest_path),
            original_absolute_USD=dict(path=str(usd),bytes=usd.stat().st_size,sha256=sha(usd)),
            runtime_files=rows,active_files=ctx['files'],resources=resources,canonical_bytes_unchanged=budget_before,
            original522_runtime_assets_byteexact=True,old_source_core_not_512128or50=True,
            first_gpu_scope_original_fivefamily_W35_integration_only=True,learning_exposure_not_admitted=True)
        write(root/'S4_NATIVE_FULLSTATE_TARGET_CPU_ACTUAL.json',result)
        print(json.dumps(dict(passed=True,target_root=str(root),receipt_SHA=sha(root/'S4_NATIVE_FULLSTATE_TARGET_CPU_ACTUAL.json'),original_float102=True,runtime522=True,no_GPU=True)))
    except BaseException:
        write((root if created else stage)/('S4_TARGET_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),dict(epoch=time.time(),error=traceback.format_exc(),GPU=False,no_budget_write=True));raise
    finally:
        for f in reversed(owned):fcntl.flock(f,fcntl.LOCK_UN);f.close()

if __name__=='__main__':main(CONTEXT)
