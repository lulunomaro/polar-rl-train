from pathlib import Path
import ast,hashlib,json,math,sys,time,zipfile
import torch
D=Path(__file__).resolve().parent
P=D/'repair_payload/v6a_audited_cpu_payload'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    assert not torch.cuda.is_initialized()
    pairs=[('windows4090_repair_worker_audited_v6.py','windows4090_repair_worker.py'),('windows4090_training_runtime_audited_v6.py','windows4090_training_runtime.py'),('run_windows4090_stage_audited_v6_once.py','run_windows4090_stage_once.py'),('prepare_windows20k_sdk_manifest_audited_v6_cpu_once.py','prepare_windows20k_sdk_manifest_cpu_once.py')]
    transformed=[]
    for wrapper,original in pairs:
        module=ast.parse((P/wrapper).read_bytes());f=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='transform')
        ns={'ast':ast};exec(compile(ast.Module(body=[f],type_ignores=[]),str(P/wrapper),'exec'),ns)
        t=ns['transform'](ast.parse((P/original).read_bytes()));compile(ast.fix_missing_locations(t),wrapper+'#reviewed','exec')
        transformed.append(dict(wrapper=wrapper,wrapper_sha256=H(P/wrapper),original=original,original_sha256=H(P/original),transformed_AST_sha256=hashlib.sha256(ast.dump(t,include_attributes=False).encode()).hexdigest()))
    sys.path.insert(0,str(P))
    import materialize_windows20k_target_audited_v6_cpu_once as m
    assert m.SCOPE_NAME=='training_scope_full20k_left_repair_audited_v6a_20261013'
    assert callable(m.H) and callable(m.ref) and callable(m.fresh_json)
    for name in m.original.EXECUTABLES:assert (P/name).is_file(),name
    original=P/'v6_closed_source_wrapper.py';ns={};exec(compile(ast.parse(original.read_bytes()),str(original),'exec'),ns)
    for name,sha in ns['ORIGINAL_SHA'].items():assert H(P/name)==sha
    SDK=Path('F:/isaacsim/IsaacLab/source/isaaclab/isaaclab')
    mathpath=SDK/'utils/math.py';tree=ast.parse(mathpath.read_bytes());f=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='quat_apply');f.decorator_list=[]
    math_ns={'torch':torch};exec(compile(ast.fix_missing_locations(ast.Module(body=[f],type_ignores=[])),str(mathpath)+'#CPU_function_only','exec'),math_ns)
    ckpath=D/'repair_payload/CPU_SOURCE_ASSEMBLY_FIXTURE_V5_FINAL_BOUND_SOURCE/immutable_source459/source459/checkpoint/model_32264_d05c.pt'
    assert H(ckpath)=='d05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a'
    ck=torch.load(ckpath,map_location='cpu',weights_only=False);xy=ck['E1_terrain_state']['spawn_xy'];assert xy.shape==(20000,2) and xy.dtype==torch.float32
    ns={'torch':torch};observer=ast.parse((P/'windows4090_substep_readback_v6.py').read_bytes());rotate=next(n for n in observer.body if isinstance(n,ast.FunctionDef) and n.name=='rotate_wxyz');exec(compile(ast.Module(body=[rotate],type_ignores=[]),'independent_rotation_cpu','exec'),ns)
    root=torch.cat([xy,torch.full((20000,1),.25)],-1);local=torch.tensor([.003,-.004,.005]).expand(20000,3);max_rounded=0.;max_double=0.;max_velocity=0.
    before=torch.get_rng_state().clone()
    for yaw in (0.,.25,1.2,math.pi/2,math.pi):
        q=torch.tensor([math.cos(yaw/2),0.,0.,math.sin(yaw/2)]).expand(20000,4)
        api=root+math_ns['quat_apply'](q,local)
        independent=root.double()+ns['rotate_wxyz'](q.double(),local.double())
        max_rounded=max(max_rounded,float((independent.to(api.dtype)-api).abs().max()))
        max_double=max(max_double,float((independent-api.double()).abs().max()))
        omega=torch.tensor([0.,0.,60.]).expand(20000,3)
        api_vel=torch.cross(omega,math_ns['quat_apply'](q,-local),dim=-1)
        independent_vel=torch.cross(omega.double(),-ns['rotate_wxyz'](q.double(),local.double()),dim=-1)
        max_velocity=max(max_velocity,float(torch.linalg.vector_norm(independent_vel-api_vel.double(),dim=-1).max()))
    assert max_rounded<1e-5 and max_velocity<=.001 and torch.equal(before,torch.get_rng_state())
    assert not torch.cuda.is_initialized()
    report=P/'reports/V6A_CLOSED_WRAPPERS_ACTUAL_SOURCE_MATH_CPU_PASSED.json';assert not report.exists()
    result=dict(epoch=time.time(),passed=True,CPU_only=True,actual_remote_target_CPU_and_GPU_pending=True,closed_wrappers=transformed,actual_source20k_spawn_fixture=True,SDK_quat_function_source=dict(path=str(mathpath),sha256=H(mathpath)),actual_API_output_dtype='float32',independent_rounded_COM_position_max_error_m=max_rounded,unrounded_double_quantization_diagnostic_m=max_double,independent_local_leverarm_COM_link_velocity_max_error_m_s=max_velocity,original_COM_tolerances_unchanged=True,no_new_CPU_RNG_draw_or_CUDA=True,max_formal_updates=256,maximum_periodic_plus_final_checkpoints=129,trace_retained_upper_bytes=256*24*20000*16*4,trace_incremental_stack_upper_bytes=48*20000*16*4)
    report.write_text(json.dumps(result,indent=2),encoding='utf8')
    package=D/'WINDOWS4090_TARGET_V6A_AUDITED_CPU_PREPARED_20261013.zip';assert not package.exists()
    files=[p for p in P.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.suffix not in ('.pt','.npz','.zip')]
    rows=[dict(archive='repair_payload_v6a/'+p.relative_to(P).as_posix(),bytes=p.stat().st_size,sha256=H(p)) for p in sorted(files)]
    manifest=dict(epoch=time.time(),file_rows=rows,target_scope=m.SCOPE_NAME,CPU_only=True,target_CPU_and_GPU_admission_pending=True,global_gpu_OSlock_environment_root=True,original_V5_and_V6_sources_retained=True)
    with zipfile.ZipFile(package,'x',compression=zipfile.ZIP_DEFLATED) as z:
        for p,row in zip(sorted(files),rows):z.write(p,row['archive'])
        z.writestr('V6A_AUDITED_CPU_BUNDLE_MANIFEST.json',json.dumps(manifest,indent=2))
    with zipfile.ZipFile(package) as z:
        assert z.testzip() is None
        for row in rows:assert hashlib.sha256(z.read(row['archive'])).hexdigest()==row['sha256']
    out=D/'reports/V6A_AUDITED_CPU_HANDOFF_ACTUAL.json';assert not out.exists()
    v=dict(epoch=time.time(),passed=True,CPU_prepared_not_GPU=True,package=dict(path=str(package),bytes=package.stat().st_size,sha256=H(package)),manifest=manifest,closed_math_CPU_report=dict(path=str(report),sha256=H(report)),remote_target_CPU_not_executed=True,SDK_native_fullrestore_PPO_pending=True)
    out.write_text(json.dumps(v,indent=2),encoding='utf8')
    print(json.dumps(dict(package=v['package'],CPU_math=result,files=len(rows))))
if __name__=='__main__':main()
