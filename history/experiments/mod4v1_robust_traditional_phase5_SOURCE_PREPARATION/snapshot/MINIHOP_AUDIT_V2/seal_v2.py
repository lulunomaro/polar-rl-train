"""Read-only saved-evidence checks; write only new v2 metadata/archive. No test rerun."""
from pathlib import Path
import ast,copy,hashlib,json,math,re,zipfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parent
RUNTIME=['__init__.py','schema_v2.py','contact_grade_v2.py','provenance_v2.py','physics_bridge_minihop_flat_v2.py','physics_bridge_minihop_rm_v2.py','run_minihop_case_v2.py']
FUTURE={'SOURCE_CLOSURE.json','minihop_audit_v2_source.zip','INDEX.json','VALIDATION.json','MANIFEST.json','seal_01.log'}

def sha(p):
    with Path(p).open('rb')as f:return hashlib.file_digest(f,'sha256').hexdigest()
def record(p):
    p=Path(p).resolve();return dict(path=str(p),bytes=p.stat().st_size,sha256=sha(p))
def load(p):return json.loads(Path(p).read_bytes())
def dump(p,v):
    with Path(p).open('x',encoding='utf-8')as f:json.dump(v,f,indent=2,allow_nan=False)
def same(a,b):return ast.dump(a,include_attributes=False)==ast.dump(b,include_attributes=False)
def method(p):return next(n for n in ast.walk(ast.parse(Path(p).read_text(encoding='utf-8')))if isinstance(n,ast.FunctionDef)and n.name=='apply_torque_request')
class Strip(ast.NodeTransformer):
    def __init__(self):self.hooks=[]
    def visit_Expr(self,n):
        v=n.value
        if isinstance(v,ast.Call)and isinstance(v.func,ast.Attribute)and isinstance(v.func.value,ast.Name)and v.func.value.id=='self'and v.func.attr in ('_capture_drivepoint','_grade_minihop_sample'):
            self.hooks.append(v.func.attr);assert not v.keywords
            if v.func.attr=='_capture_drivepoint':assert [a.id for a in v.args]==['actual_dq','bounded']
            else:assert not v.args
            return None
        return self.generic_visit(n)
def finite_json(v):
    if isinstance(v,float):assert math.isfinite(v)
    elif isinstance(v,list):
        for a in v:finite_json(a)
    elif isinstance(v,dict):
        for a in v.values():finite_json(a)
def prefix_verify(p):
    receipt=load(p)
    for k in ('trace_prefix','physics_prefix'):
        r=receipt[k];path=Path(r['path']);assert path.resolve().is_relative_to(HERE)
        assert path.stat().st_size==r['bytes']==r['producer']['bytes']and sha(path)==r['SHA']==r['producer']['SHA']and r['actual_prefix_matches_producer']
        rows=[json.loads(s)for s in path.read_bytes().splitlines()];assert len(rows)==r['producer']['successful_rows']
        for row in rows:finite_json(row)
    assert not receipt['partial_trial_passed']and not receipt['invalid_values_replaced_by_zero'];return receipt

def main():
    frozen=load(HERE/'SOURCE_FREEZE.json');counts={}
    for group in ('old_files','sources','model_assets'):
        for r in frozen[group]:assert Path(r['path']).stat().st_size==r['bytes']and sha(r['path'])==r['sha256'],r['path']
        counts[group]=len(frozen[group])
    assert counts==dict(old_files=1078,sources=26,model_assets=279)
    unit1=load(HERE/'UNIT_RESULT_01.json');unit=load(HERE/'UNIT_RESULT_02.json');boot=load(HERE/'BOOT_ADMISSION_01.json')
    assert unit1['checks']==917 and unit1['failures']==0 and unit['checks']==936 and unit['failures']==0
    assert unit['calls']['step']==unit['calls']['forward']==0 and not unit['full_model_constructed']
    for r,folder in ((unit1,'unit_attempt_01'),(unit,'unit_attempt_02')):
        for n,wanted in r['sources'].items():assert sha(HERE/folder/n)==wanted,(folder,n)
        prefix_verify(HERE/folder/'synthetic_ERROR.json')
    for n,wanted in unit['sources'].items():assert sha(HERE/n)==wanted,n
    assert boot['status']=='ADMITTED_ZERO_STEP_ONLY'and boot['checks']==39 and boot['failures']==0 and boot['physics_steps']==0
    assert boot['unit_receipt_SHA']==sha(HERE/'UNIT_RESULT_02.json')and not boot['old_preflight_executed']and not boot['runner_executed']and not boot['trajectory_qualified']
    assert boot['calls']['mj_forward']==60 and all(v==0 for k,v in boot['calls'].items()if k!='mj_forward')
    for n in ['boot_admission_v2.py','contact_grade_v2.py','schema_v2.py','provenance_v2.py','run_minihop_case_v2.py','physics_bridge_minihop_flat_v2.py','physics_bridge_minihop_rm_v2.py']:assert sha(HERE/'boot_attempt_01'/n)==sha(HERE/n),n
    admitted_paths={r['path']for r in frozen['old_files']+frozen['sources']+frozen['model_assets']}|{str((HERE/n).resolve())for n in RUNTIME+['boot_admission_v2.py']}
    for r in boot['records']:
        assert r['physics_steps']==r['physics_grade_rows']==0 and r['operator_default_disabled']and not r['control_cycle_executed']
        manifest=load(HERE/'boot_attempt_01'/f"{r['scene']}_SOURCE_PREEXEC.json")
        assert sha(HERE/'boot_attempt_01'/f"{r['scene']}_SOURCE_PREEXEC.json")==r['source_manifest_SHA']
        for f in manifest['files']+manifest['model_assets']:assert sha(f['path'])==f['SHA']and Path(f['path']).stat().st_size==f['bytes']
        for observed in r['loaded_workspace_modules']:assert observed['path']in admitted_paths,observed
    for scene,base in [('flat','physics_bridge_v3.py'),('rm','physics_bridge_rm_buffer_v1.py')]:
        node=method(HERE/f'physics_bridge_minihop_{scene}_v2.py');assert same(node,method(ROOT/f'physics_bridge_minihop_{scene}_v1.py'))
        strip=Strip();assert same(strip.visit(copy.deepcopy(node)),method(ROOT/base))and strip.hooks==['_capture_drivepoint','_grade_minihop_sample']
    def loop(p):return next(n for n in ast.walk(ast.parse(p.read_text(encoding='utf-8')))if isinstance(n,ast.For)and isinstance(n.target,ast.Name)and n.target.id=='k')
    assert same(loop(HERE/'run_minihop_case_v2.py'),loop(ROOT/'run_minihop_case_v1.py'))
    contract=load(HERE/'GRADING_CONTRACT.json')
    for folder in ('unit_attempt_01','unit_attempt_02'):assert sha(HERE/folder/'GRADING_CONTRACT.json')==sha(HERE/'GRADING_CONTRACT.json')
    assert contract['air_total_normal_N_lte']==1. and contract['minimum_air_interval_s']==.02 and contract['physics_dt_s']==.0005
    assert not load(HERE/'PROTO_DISABLED.json')['hop']['operator_enable']
    inventory=[Path(s).resolve()for s in(HERE/'DISCOVERED_FILES.txt').read_text(encoding='utf-8').splitlines()if s.strip()]
    assert len(inventory)==len(set(inventory))and all(p.is_relative_to(HERE)and p.is_file()for p in inventory)
    for p in inventory:
        if p.suffix=='.py':ast.parse(p.read_text(encoding='utf-8'))
    links=[]
    for name in ('README.md','ERROR_REPORT.md','SCOPE.md'):
        for dst in re.findall(r'\]\(<([^>]+)>\)',(HERE/name).read_text(encoding='utf-8')):
            p=Path(dst.split('#')[0]);assert p.is_absolute()
            assert p.is_file()or(p.parent==HERE and p.name in FUTURE),(name,dst)
            links.append(dict(source=name,target=str(p)))
    closure=dict(kind='MINIHOP_AUDIT_V2_PRIVATE_RUNTIME_SOURCE_CLOSURE',current_runtime=[record(HERE/n)for n in RUNTIME],original_source_references=frozen['sources'],model_assets=frozen['model_assets'],controller=record(ROOT/'MINIHOP_V1/controller.py'),both_scene_superset=True,observed_boot_workspace_modules_all_covered=True,framework_versions=dict(python='3.14.3 x64',numpy='2.4.5',mujoco=boot['mujoco_version']),no_episode_or_old_score_replay=True,current_PH4_cutoff_excludes_v2=True,PH5_and_later_pending=True)
    dump(HERE/'SOURCE_CLOSURE.json',closure)
    members=RUNTIME+['PROTO_DISABLED.json','GRADING_CONTRACT.json','SOURCE_FREEZE.json','SOURCE_CLOSURE.json','BRIDGE_AST.json','RUNNER_AST.json','BUILD.txt']
    with zipfile.ZipFile(HERE/'minihop_audit_v2_source.zip','x',compression=zipfile.ZIP_DEFLATED)as z:
        for n in members:z.write(HERE/n,'MINIHOP_AUDIT_V2/'+n)
    with zipfile.ZipFile(HERE/'minihop_audit_v2_source.zip')as z:
        assert set(z.namelist())=={'MINIHOP_AUDIT_V2/'+n for n in members}
        for n in members:assert hashlib.sha256(z.read('MINIHOP_AUDIT_V2/'+n)).hexdigest()==sha(HERE/n)
    # These receipts are independent of INDEX/metadata/log self hashes.
    primary=RUNTIME+['README.md','ERROR_REPORT.md','BUILD.txt','PROTO_DISABLED.json','GRADING_CONTRACT.json','SOURCE_FREEZE.json','SOURCE_CLOSURE.json','BRIDGE_AST.json','RUNNER_AST.json','UNIT_RESULT_02.json','BOOT_ADMISSION_01.json','minihop_audit_v2_source.zip']
    dump(HERE/'MANIFEST.json',dict(status='SEALED_PRIVATE_AUDIT_AND_ZERO_STEP_ADMISSION_ONLY',files=[record(HERE/n)for n in primary],physics_steps=0))
    validation=dict(status='SEALED_PRIVATE_AUDIT_AND_ZERO_STEP_ADMISSION_ONLY',valid=True,unchanged=counts,unit01_checks=917,unit02_checks=936,unit_failures=0,real_boot_checks=39,boot_failures=0,all_integration_calls=0,initialization_forward_calls=60,physics_steps=0,episodes_launched=0,old_preflight_reexecuted=False,R39_results_parsed_or_regraded=False,actuator_full_AST_equal=True,runner_control_loop_AST_equal=True,unit2_and_boot_current_source_hashes_equal=True,contract_unchanged=True,raw_prefix_receipts_verified=True,observed_boot_workspace_modules_all_covered=True,operator_default_disabled=True,private_contact_only_not_complete_trueCOMproper=True,public_sensor_projection_changed=False,contact_FSM_MPC_permission_added=False,root_active_world_leg_imported_or_modified=False,blocked_IO_touched=False,PH5_and_later_pending=True,current_PH4_cutoff_excludes_v2=True,metadata_is_saved_evidence_check_not_test_or_physics_rerun=True)
    dump(HERE/'VALIDATION.json',validation)
    allpaths=sorted(set(inventory)|{HERE/n for n in FUTURE})
    unhashed={'INDEX.json','VALIDATION.json','MANIFEST.json','seal_01.log'}
    rows=[]
    for p in allpaths:
        if p.name in unhashed and p.parent==HERE:rows.append(dict(path=str(p.relative_to(HERE)),sha256=None,reason='metadata_closure_or_self_or_active_seal_transcript'))
        else:rows.append(dict(path=str(p.relative_to(HERE)),bytes=p.stat().st_size,sha256=sha(p)))
    index=dict(status=validation['status'],file_count=len(rows),files=rows,live_markdown_links=links,live_link_count=len(links),validation=validation,manifest_SHA=sha(HERE/'MANIFEST.json'),self_hash_policy='Four metadata/self/active-transcript rows are explicitly unhashed; all other indexed bytes are fixed.')
    dump(HERE/'INDEX.json',index)
    for link in links:assert Path(link['target']).is_file(),link
    print(json.dumps(dict(status=validation['status'],indexed_files=len(rows),links=len(links),unchanged=counts,unit02_checks=936,real_boot_checks=39,physics_steps=0,README_SHA=sha(HERE/'README.md'),INDEX_SHA=sha(HERE/'INDEX.json'),ZIP_SHA=sha(HERE/'minihop_audit_v2_source.zip')),indent=2))
if __name__=='__main__':main()
