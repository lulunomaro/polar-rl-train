"""Seal existing offline results and hashes; no tests/SDK/physics/Git rerun."""
from pathlib import Path
import ast,dataclasses,hashlib,json,re,sys
R=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def meta(p):p=Path(p);return {'path':str(p),'relative':p.relative_to(R).as_posix(),'bytes':p.stat().st_size,'sha256':sha(p)}
def new(p,x):
    assert not p.exists(),str(p)+' already exists'
    p.write_text(json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def main():
    assert not (R/'INDEX.json').exists()
    check=json.loads((R/'attempts/001/RESULT.json').read_text(encoding='utf-8'));qa=json.loads((R/'attempts/001/STATIC_QA.json').read_text(encoding='utf-8'));probe=json.loads((R/'model_probes/001/RESULT.json').read_text(encoding='utf-8'))
    assert check['all_passed'] and check['synthetic_units']['tests']==32 and qa['physics_steps']==0
    for s in check['source_files']:assert sha(R/s['name'])==s['sha256'],s['name']+' changed after tests'
    for p,digest in check['protected_hashes'].items():assert sha(p)==digest,'protected source changed: '+p
    runtime_imports={}
    for name in ['nominal_model.py','contact_proxy.py']:
        imports=[]
        for node in ast.walk(ast.parse((R/name).read_text(encoding='utf-8'))):
            if isinstance(node,ast.Import):imports += [a.name for a in node.names]
            elif isinstance(node,ast.ImportFrom):imports.append(node.module)
        assert not any(x and any(bad in x.lower() for bad in ('mujoco','isaac','kinematics','torch')) for x in imports)
        runtime_imports[name]=imports
    sys.path.insert(0,str(R));from contact_proxy import Config,ROLE
    new(R/'PROPOSED_THRESHOLDS.json',{'role':ROLE,'default':dataclasses.asdict(Config()),'fractions_change_uncertainty_only_not_nominal_model':True,'confidence_not_calibrated_probability':True,'normal_is_chassis_Z_not_terrain_truth':True,'user_acceptance_thresholds':False})
    validation={'status':'NOMINAL_SENSOR_PROXY_MATH_AND_STATIC_QA_PASS_NOT_MEASURED_FORCE','synthetic_units':check['synthetic_units'],'static_QA':check['static_QA'],'initial_nominal_algebra_force_body_xz_N2':probe['force']['force_body_xz_N2'],'runtime_imports':runtime_imports,'public_constant_SHA':sha(R/'PUBLIC_NOMINAL_CONSTANTS.json'),'runtime_DR_contacts_rootGT_inputs':False,'fresh_public_model_static_forwards':qa['static_forwards'],'physics_steps':0,'new_robot_episodes':0,'protected_sources_unchanged':True,'protected_hashes':check['protected_hashes'],'source_sha_bound_to_tested_attempt':True,'qualification_exclusions':['measured torque calibration','actual wheel/guide contact identity','whole-robot airborne state','terrain normal','complete dynamic RNE','D0/D5/D2 guarantee','jump/270mm/RM/board/firmware','real-time/WCET']}
    new(R/'VALIDATION.json',validation)
    files=sorted(p for p in R.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='INDEX.json')
    index={'module':'CONTACT_PROXY_NOMINAL_V1','status':validation['status'],'model_runtime':meta(R/'nominal_model.py'),'observer_runtime':meta(R/'contact_proxy.py'),'public_constants':meta(R/'PUBLIC_NOMINAL_CONSTANTS.json'),'README':meta(R/'README.md'),'validation':meta(R/'VALIDATION.json'),'source_xml_SHA':'0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324','q_and_tau_order':['Lhip','Lcrank_absolute','Rhip','Rcrank_absolute'],'input_authority':'declared sensor/effort-domain data only; fixed public parameters, no episode/DR/rootGT/contact/top-truth overrides','observable_output':'leg-equivalent XZ load assuming wheel-center external load path; normal is chassis-Z; guide/other support unobserved','default_unbound_design_torque_rejected':True,'confidence_proposed_not_calibrated_probability':True,'default_confidence_cap':.55,'all_attempts_preserved':['model_probes/001','attempts/001','ADMIN_EVENTS.json'],'modelProbe_original_source_is_earlier_revision':True,'test_attempts':[{'id':'synthetic_static_001','actual_result':check['synthetic_units'],'static_QA':check['static_QA'],'source_hashes':check['source_files']}],'new_physics_steps':0,'new_robot_episodes':0,'Git_status':'Pending parent PHASE2 archive; no Git/SSH performed for prototype','unchanged_FSM_and_parent_source_hashes':check['protected_hashes'],'files':[meta(p) for p in files]}
    new(R/'INDEX.json',index)
    links=[]
    for p in R.glob('*.md'):
        for s in re.findall(r'\]\(<([^>]+)>\)',p.read_text(encoding='utf-8')):
            target=Path(s.split('#')[0]);target=target if target.is_absolute() else p.parent/target;assert target.exists(),(p,s);links.append(s)
    print(json.dumps({'core':meta(R/'contact_proxy.py'),'model':meta(R/'nominal_model.py'),'README':meta(R/'README.md'),'INDEX':meta(R/'INDEX.json'),'VALIDATION':meta(R/'VALIDATION.json'),'test':check['synthetic_units'],'static':check['static_QA'],'links_checked':len(links),'physics_steps':0,'protected_sources_unchanged':True},indent=2))
if __name__=='__main__':main()
