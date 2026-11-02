"""Seal this new prototype only; no tests, simulation, IO backend or Git calls."""
from pathlib import Path
import ast,dataclasses,hashlib,json,re,sys
R=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def meta(p):p=Path(p);return {'path':str(p),'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
def create(p,obj):
    if p.exists():
        assert json.loads(p.read_text(encoding='utf-8'))==obj,str(p)+' differs from preserved output'
        return
    p.write_text(json.dumps(obj,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
    assert not (R/'INDEX.json').exists()
    results=[json.loads((R/'attempts'/f'{n:03d}'/'RESULT.json').read_text(encoding='utf-8')) for n in (1,2,3)]
    final=results[-1];assert final['all_passed'] and final['python']['tests']==63 and len(final['python']['modes_seen'])==11
    for item in final['source_files']:assert sha(R/item['name'])==item['sha256'],item['name']+' changed after final tests'
    for path,digest in final['protected_hashes'].items():assert sha(path)==digest,path+' protected hash changed'
    sys.path.insert(0,str(R));import fsm_detector as fd
    core=ast.parse((R/'fsm_detector.py').read_text(encoding='utf-8'));imports=[]
    for node in ast.walk(core):
        if isinstance(node,ast.Import):imports += [x.name for x in node.names]
        elif isinstance(node,ast.ImportFrom):imports.append(node.module)
    assert set(imports)<={'dataclasses','enum','math','typing'}
    create(R/'PROPOSED_THRESHOLDS.json',{'role':fd.ROLE,'defaults':dataclasses.asdict(fd.Config()),'units':'seconds, radians, output-joint radians/rad_s, N, A, degC, W as named','electrical_limits_None_are_unbound_not_zero_or_infinite_ratings':True,'launch_and_recovery_default_disabled':True,'front_binding_default_false':True,'user_acceptance_thresholds':False,'C_API_time_unit':'uint64 monotonic us, explicit adapter required','Python_time_unit':'relative monotonic seconds;1e-12deadline comparison slack is numerical only'})
    links=[]
    for p in R.glob('*.md'):
        for value in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf-8')):
            path=Path(value.split('#')[0]);path=path if path.is_absolute() else p.parent/path
            # INDEX is the last new container to be written below, not a source.
            assert path.exists() or path.resolve() in {(R/'INDEX.json').resolve(),(R/'VALIDATION.json').resolve()},(p,value)
            links.append({'document':p.name,'target':value})
    validation={'status':'SYNTHETIC_PYTHON_FSM_PASS_AND_C_HEADER_SYNTAX_PASS_NOT_PHYSICAL','python_final':final['python'],'C_header_final':final['C_header'],'all11_requested_modes_seen':True,'core_imports':imports,'protected_files_unchanged':True,'protected_hashes':final['protected_hashes'],'source_sha_bound_to_final_attempt':True,'markdown_link_count':len(links),'negative_fixture_tests_are_expected_guard_cases_not_real_device_faults':True,'physics_steps':0,'robot_episodes':0,'C_FSM_runtime_implemented':False,'board_or_CAN':False,'Git_calls_this_module':0,'SSH':False,'claim_exclusions':['contact calibration','actual freeflight/contact truth','closed-loop recovery/jump','270mm','ARM/BSP','C runtime','WCET','full safety qualification']}
    create(R/'VALIDATION.json',validation)
    paths=sorted(p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='INDEX.json')
    index={'module':'FSM_DETECTOR_V1','status':validation['status'],'core':meta(R/'fsm_detector.py'),'C_interface_proposal':meta(R/'fsm_detector_v1.h'),'test_source':meta(R/'test_fsm_detector.py'),'threshold_role':fd.ROLE,'mode_ids':{m.name:m.value for m in fd.Mode},'profile_ids':{m.name:m.value for m in fd.Profile},'phase_ids':{m.name:m.value for m in fd.Phase},'valid_bits':{m.name:m.value for m in fd.Valid},'attempts':[{'id':n+1,'actual_result':x['python'],'source_hashes':x['source_files'],'C_header':x['C_header'],'result_path':f'attempts/{n+1:03d}/RESULT.json'} for n,x in enumerate(results)],'input_authority':'Sensor-only declared reference/validity/freshness; no contacts/root/worldXYZ/top truth','observability':'Proxy/model-based support hypotheses, not physical contact/air/landing proof; unknown stays uncertain','trajectory_binding':'All launch/recovery disabled/unbound by default; opt-in simulation/fixture only; no motor output','source_references_read_only':final['protected_hashes'],'new_simulation_steps':0,'new_robot_episodes':0,'new_C_runtime_or_board_runs':0,'scope':'Only this new directory written; no parent/frozen source/Git/SSH/physical rerun','git_status':'Parent later archive pending; no Git action requested or run for this module','files':[meta(p) for p in paths]}
    create(R/'INDEX.json',index)
    for p in R.glob('*.md'):
        for value in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf-8')):
            path=Path(value.split('#')[0]);assert (path if path.is_absolute() else p.parent/path).exists()
    print(json.dumps({'core':meta(R/'fsm_detector.py'),'header':meta(R/'fsm_detector_v1.h'),'README':meta(R/'README.md'),'INDEX':meta(R/'INDEX.json'),'VALIDATION':meta(R/'VALIDATION.json'),'final_tests':final['python'],'new_physics_steps':0,'C_runtime':False,'protected_files_unchanged':True},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
