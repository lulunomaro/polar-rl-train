"""Reader-only V2: preserve original optional None fields; use actual own audit.

No runtime, package, checkpoint, GPU task or old case is changed/replayed.
"""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import sys
import time
import traceback

D=Path(__file__).resolve().parent
R=D/'reports'
CASE='s5_nominal_s20261002_single_eval_flat_120_v1'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    source=D/'audit_nominal_D0_and_retained_pressure_metadata_CPU.py'
    old=source.read_text(encoding='utf8')
    before="    if witness['kind']=='flat':\n        rows=[probe['mild_initial_parameters'],probe['mild_final_parameters']]\n    else:\n        rows=[probe['initial_parameter_audit'],probe['final_parameter_audit']]"
    after="""    optional_legacy_fields_absent=False
    if witness['kind']=='flat':
        initial_optional=probe['mild_initial_parameters'];final_optional=probe['mild_final_parameters']
        if initial_optional is None or final_optional is None:
            assert initial_optional is None and final_optional is None
            optional_legacy_fields_absent=True
            # These original optional fields deliberately describe MildDR, which
            # does not exist in nominal. Do not invent an initial audit object.
            rows=[probe['chassis_PD_audit']['parameter_auditor']]
        else:
            rows=[initial_optional,final_optional]
    else:
        rows=[probe['initial_parameter_audit'],probe['final_parameter_audit']]"""
    assert old.count(before)==1
    new=old.replace(before,after)
    new=new.replace('return dict(D0_nominal_initial_final_readback_exact=True,',
        'return dict(legacy_optional_flat_MildDR_fields_absent=optional_legacy_fields_absent,\n                independent_initial_final_witness_parameters_used=True,\n                own_nominal_audit_from_actual_chassis_PD_report_used_when_legacy_absent=optional_legacy_fields_absent,\n                no_missing_initial_audit_fabricated=True,\n                D0_nominal_initial_final_readback_exact=True,')
    target=D/'audit_nominal_D0_and_retained_pressure_metadata_CPU_v2.py'
    assert not target.exists();ast.parse(new);target.write_text(new,encoding='utf8')
    p=D/'review_nominal_original_physical_and_metrics_CPU.py';oldreader=p.read_text(encoding='utf8')
    newreader=oldreader.replace('from audit_nominal_D0_and_retained_pressure_metadata_CPU import audit',
                               'from audit_nominal_D0_and_retained_pressure_metadata_CPU_v2 import audit')
    before="  assert p['mild_initial_parameters']['profile']==p['mild_final_parameters']['profile']=='nominal'"
    after="""  if p['mild_initial_parameters'] is None or p['mild_final_parameters'] is None:
   assert p['mild_initial_parameters'] is None and p['mild_final_parameters'] is None
   assert p['chassis_PD_audit']['parameter_auditor']['profile']=='nominal'
  else:
   assert p['mild_initial_parameters']['profile']==p['mild_final_parameters']['profile']=='nominal'"""
    assert before in newreader;newreader=newreader.replace(before,after)
    newreader=newreader.replace('CPU_ACTUAL_READER_ORIGINAL_ERROR_','CPU_ACTUAL_READER_V2_ORIGINAL_ERROR_')
    newreader=newreader.replace('S5_NOMINAL_ABC_ORIGINAL_V8_COMPLETE_DATA_AND_OWN_MATCHED_PAIR_CPU_REVIEW',
                                'S5_NOMINAL_ABC_ORIGINAL_V8_COMPLETE_DATA_AND_OWN_MATCHED_PAIR_CPU_REVIEW_V2')
    reader=D/'review_nominal_original_physical_and_metrics_CPU_v2.py'
    assert not reader.exists();ast.parse(newreader);reader.write_text(newreader,encoding='utf8')
    # Actual first GPU-native saved probe, not a synthetic replacement of None.
    current=json.loads(sorted(R.glob(CASE+'_CURRENT_ACTUAL_*.json'))[-1].read_bytes())
    attempt=Path(next(x['local_path'] for x in current['collected_files'] if x['relative'].endswith('/PARENT_EXIT_RECEIPT.json'))).parent
    probe_path=attempt/'output/probe.json';probe=json.loads(probe_path.read_bytes())
    assert probe['mild_initial_parameters'] is None and probe['mild_final_parameters'] is None
    spec=importlib.util.spec_from_file_location('nominal_metadata_reader_V2',target)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result=module.audit(probe);assert result['legacy_optional_flat_MildDR_fields_absent']
    failures=[]
    for name in ('fake_single_optional_field','missing_own_nominal_audit','wrong_own_nominal_profile','fake_MildDR',
                 'fake_MildDR_RNG','wrong_nominal_mass','wrong_unity_motor_scale','D7_audit_missing'):
        bad=copy.deepcopy(probe);params=bad['native_readonly_witness']['final_physical_parameters']
        if name=='fake_single_optional_field':bad['mild_initial_parameters']={}
        elif name=='missing_own_nominal_audit':bad['chassis_PD_audit']['parameter_auditor']={}
        elif name=='wrong_own_nominal_profile':bad['chassis_PD_audit']['parameter_auditor']['profile']='white_v3'
        elif name=='fake_MildDR':params['mild_factor']=[1]*80
        elif name=='fake_MildDR_RNG':params['actual_captured_RNG_bytes']['_mild_dr/generator']={}
        elif name=='wrong_nominal_mass':params['mass'][0][0]+=.01
        elif name=='wrong_unity_motor_scale':params['motors']['legs']['episode_scale'][0][0]=.99
        else:bad['chassis_PD_audit']['parameter_auditor']['independent_pressure_audits'].pop('D7_PD')
        try:module.audit(bad)
        except (AssertionError,KeyError,TypeError,ValueError) as e:
            failures.append(dict(case=name,rejected=True,error=type(e).__name__))
        else:raise AssertionError('Bad saved metadata was accepted: '+name)
    value=dict(epoch=time.time(),passed=True,case=CASE,actual_saved_probe_SHA=H(probe_path),
               original_optional_fields_still_None=True,original_V1_TypeError_and_finite_ORIGINAL_ERROR_preserved=True,
               actual_own_final_chassis_PD_nominal_audit_plus_full_initial_final_witness_readback_used=True,
               no_initial_audit_object_or_MildDR_fabricated=True,strict_actual_saved_metadata_negatives=failures,
               V1_reader_SHA=H(p),V2_reader_SHA=H(reader),V1_metadata_SHA=H(source),V2_metadata_SHA=H(target),
               no_GPU_runtime_package_weights_or_original_mainloops_changed=True)
    with (R/'NOMINAL_FIRST_NATIVE_OPTIONAL_NONE_READER_V2_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(value,f,indent=2)
    print(json.dumps(dict(reader_V2_CPU_passed=True,saved_metadata_negatives=len(failures),attempt=str(attempt),no_GPU=True)))


if __name__=='__main__':
    try:main()
    except BaseException:
        with (R/('NOMINAL_OPTIONAL_NONE_V2_PREPARE_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x',encoding='utf8') as f:
            json.dump(dict(error=traceback.format_exc(),no_GPU_SSH_PPO_budget=True),f,indent=2)
        raise
