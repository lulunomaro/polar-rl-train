"""Independent missing50mm state components and actual targetCPU proof after full145 review."""
from second_io import *
import ast

TARGET='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_CPU_PREPARED_20261012'
SOURCE='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'

def main():
    assert not (R/'WAVE50_LEARNING_TARGET_CPU_PASSED.json').exists()
    reviewpath=sorted(R.glob('WAVE50_WORLDMESH_ACTUAL_REVIEW_[0-9]*.json'))[-1];v=json.loads(reviewpath.read_bytes());assert v['review_complete']
    a=next(iter(v['review'].values()))['review'];base=a['base_review'];assert base['ordinary']==0 and a['groups']['forward']['complete_envs']==11 and a['groups']['reverse']['complete_envs']==23
    cpath=Path(v['collection']);c=json.loads(cpath.read_bytes());row=next(iter(c['cases'].values()));jid=row['manifest']['job_id'];assert row['result']['phase']=='complete' and not row['result']['new_learning']
    decision=save('WAVE50_145_COMPLETE_SCOPE_DECISION.json',dict(epoch=time.time(),job_id=jid,review=str(reviewpath),collection=str(cpath),checkpoint=row['result']['checkpoint'],terrain_raw=row['probe']['full_route_raw'],forward_complete=11,reverse_complete=23,environments_each=27,standing26_not_required_to_cross=True,ordinary=0,unique_declared_truncations=base['unique_truncations'],closure_mm=base['closure_mm'],all_raw6000callbacks_groundcontactintegral_COMlink_hardware_original_tolerances_reviewed=True,query_NPZ_twohost_byteSHA_exact=True,query_original_ground1e6_passed=True,not_qualified50mm_scope=True,no70mm_progression=True,actual_need_for_new_isolated50mm_learning=True,all_valid_incomplete_prefixes_preserved=True,physics_process_wall_seconds=row['result']['physics_process_wall_seconds'],no_PPO_or_canonical_charge=True,saved_source_state_is35mm=True,new_scope_transition_required='explicit35_to50_geometry_assignment',no_third_same35mm_PPO=True))
    impl=D/'wave50_learning_CPU_payload';assert not impl.exists();impl.mkdir()
    old=W/'MOD4_E1_SLOPE5_INDEPENDENT_PREPARE_20261011/payload/isaac/mod4'
    for name in ('g4_cad_wave_geometry.py','g4_cad_profile.json'):(impl/name).write_bytes((D/'wave50_worldmesh_scope'/name).read_bytes())
    current=(W/'MOD4_E1_G3_LEARNING_PREPARE_20261010/payload/isaac/mod4/g3_terrain_checkpoint.py').read_text()
    tree=ast.parse(current);functions=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ('validate','current_state','identity')]
    text="import hashlib\nimport e1_terrain_checkpoint as old\nPROFILE='mod4_G4_CAD_derived_50mm_v1'\n"+'\n'.join(ast.unparse(x) for x in functions)
    text=text.replace('g3_cad_wave_geometry','g4_cad_wave_geometry').replace('G3_height','G4_height').replace('G3_profile','G4_profile').replace('G3_is','G4_is').replace('.035','.05').replace('0.035','0.05')
    (impl/'g4_current_state.py').write_text(text+'\n',encoding='utf8')
    runtime=(old/'slope5_retention_runtime.py').read_text().replace('slope5_geometry import configure_slope','g4_cad_wave_geometry import configure_g4').replace('configure_slope(cfg)','configure_g4(cfg)').replace('SLOPE','WAVE50')
    (impl/'g4_retention_runtime.py').write_text(runtime,encoding='utf8')
    migration=(old/'slope5_command_migration.py').read_text().replace('SLOPE','WAVE50');(impl/'g4_command_migration.py').write_text(migration,encoding='utf8')
    cp=(old/'slope5_full_checkpoint.py').read_text().replace('slope5','g4').replace('SLOPE','WAVE50').replace('3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',SOURCE).replace('verified_G3_to_independent_WAVE505','verified_G3_to_independent_WAVE50')
    (impl/'g4_full_checkpoint.py').write_text(cp,encoding='utf8')
    full=(old/'slope5_fullsave_cpu.py').read_text().replace('slope5_current_state','g4_current_state').replace('SLOPE','WAVE50').replace('mod4_WAVE50_derived5deg_2m_mirrored_v1','mod4_G4_CAD_derived_50mm_v1')
    (impl/'g4_fullsave_cpu.py').write_text(full,encoding='utf8')
    test=(old/'test_slope_fullstate_cpu.py').read_text().replace('slope5_command_migration','g4_command_migration').replace('SLOPE','WAVE50').replace('3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',SOURCE)
    test=test.replace("if __name__=='__main__':", "if __name__=='__main__':")
    (impl/'test_g4_fullstate_cpu.py').write_text(test,encoding='utf8')
    files=list(impl.iterdir());assert len(files)==8
    for p in files:
        if p.suffix=='.py':compile(p.read_text(),p.name,'exec')
    prep=save('WAVE50_LEARNING_CPU_COMPONENTS_PREPARED.json',dict(epoch=time.time(),target=TARGET,source_count_expected=377,previous_source_count=369,source_checkpoint_SHA=SOURCE,source35_geometry_command_identity_must_be_exact_before_new50_binding=True,new_assignment_identity_not_same35_or_PhysX_resume=True,files={p.name:dict(bytes=p.stat().st_size,sha256=H(p.read_bytes())) for p in files},full50_CUDA_SDK_native_PPO_fresh_formal_not_deployed=True,new_budget_seconds=0))
    n,w=io.connect_both()
    try:
        cloned=run(n,r'''from pathlib import Path
import json,hashlib,ast,shutil,time
old=Path(ROOT_TOKEN);new=Path(TARGET_TOKEN);freeze=json.loads((old/'reports/SOURCE_FREEZE.json').read_bytes())['sha256'];assert len(freeze)==369 and not new.exists()
new.mkdir();(new/'reports').mkdir()
for name,h in freeze.items():
 p=old/name;raw=p.read_bytes();assert hashlib.sha256(raw).hexdigest()==h;out=new/name;out.parent.mkdir(parents=True,exist_ok=True);out.write_bytes(raw)
print(json.dumps(dict(target=str(new),old369_all_SHA_exact=True,old_source_unchanged=True,no_GPU_PPO_budget_write=True)))
'''.replace('ROOT_TOKEN',repr(ROOT)).replace('TARGET_TOKEN',repr(TARGET)))
        save('WAVE50_LEARNING_CPU_SOURCE_CLONED.json',cloned)
        with n.open_sftp() as f:
            for p in files:io.put(f,TARGET+'/isaac/mod4/'+p.name,p.read_bytes())
            io.put(f,TARGET+'/reports/CPU_COMPONENTS_PREPARED.json',prep.read_bytes())
            io.put(f,TARGET+'/reports/FROZEN145_COMPLETE_SCOPE_DECISION.json',decision.read_bytes())
        result=run(n,r'''from pathlib import Path
import json,sys,hashlib,time,ast,contextlib,io
D=Path(TARGET_TOKEN);old=Path(ROOT_TOKEN);CODE=D/'isaac/mod4';sys.path[:0]=[str(CODE),str(D)]
before=json.loads((old/'reports/SOURCE_FREEZE.json').read_bytes())['sha256'];prep=json.loads((D/'reports/CPU_COMPONENTS_PREPARED.json').read_bytes());source=Path(SOURCE_PATH_TOKEN);assert hashlib.sha256(source.read_bytes()).hexdigest()==prep['source_checkpoint_SHA']
files=dict(before)
for name,row in prep['files'].items():
 rel='isaac/mod4/'+name;assert rel not in files;files[rel]=row['sha256']
assert len(files)==377
for name,h in files.items():
 p=D/name;assert hashlib.sha256(p.read_bytes()).hexdigest()==h
 if p.suffix=='.py':ast.parse(p.read_text())
import test_g4_fullstate_cpu as test
capture=io.StringIO()
with contextlib.redirect_stdout(capture):test.main(str(source))
proof=json.loads(capture.getvalue());assert proof['passed'] and proof['source']['finite_tensors']==102 and proof['no_CUDA_initialized']
import g4_fullsave_cpu
info=g4_fullsave_cpu.fullsave(source);assert info['finite_tensors']==102
freeze=dict(epoch=time.time(),sha256=files,old369_all_SHA_exact=True,new_independent8_components=True)
p=D/'reports/SOURCE_FREEZE.json';assert not p.exists();p.write_text(json.dumps(freeze,indent=2))
result=dict(epoch=time.time(),passed=True,target=str(D),source_count=377,source_checkpoint=info,proof=proof,all_target_source_SHA_exact=True,old369_bytes_preserved=True,actual_target_CPU_only_no_CUDA=True,no50_SDK_native_PPO_fresh_or_formal_deployed=True,not_actual_CUDA_fullrestore_admission=True)
p=D/'reports/WAVE50_TARGET_CPU_PASSED.json';assert not p.exists();p.write_text(json.dumps(result,indent=2));print(json.dumps(result))
'''.replace('TARGET_TOKEN',repr(TARGET)).replace('ROOT_TOKEN',repr(ROOT)).replace('SOURCE_PATH_TOKEN',repr(json.loads((R/'WAVE143_COMPLETE_OBSERVED_SCOPE_DECISION.json').read_bytes())['own_checkpoint']['path'])))
        save('WAVE50_LEARNING_TARGET_CPU_PASSED.json',result);print(json.dumps(dict(target=TARGET,source377=True,actual_targetCPU_passed=True,no_CUDA_SDK_native_PPO_formal_deployed=True)))
    finally:io.cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('WAVE50_LEARNING_CPU_PREPARE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_blind_replay=True,no_GPU_or_budget_write=True));raise
