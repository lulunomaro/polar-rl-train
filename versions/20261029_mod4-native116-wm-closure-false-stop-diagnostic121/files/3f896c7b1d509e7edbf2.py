"""Seal a new necessary CPU diagnostic purpose; never decode actual inputs here."""
from pathlib import Path
import ast
import hashlib
import json
import os
import subprocess
import time
import traceback

T=Path(__file__).resolve().parent
S=T/'H1_NATIVE116_WM_CLOSURE_FALSE_STOP_CPU_V121_20261029'
R=S/'reports'
PARENT=T/'H1_NATIVE116_LATEST_USER_MUJOCO_MOTION_WM_V118_20261029/PURPOSE118_TYPED_DISPLAY_BINDING.json'


def H(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read(path):
    return json.loads(Path(path).read_bytes())


def put(path, value):
    assert not path.exists(), str(path)
    path.write_bytes((json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode('utf-8'))


def main():
    R.mkdir(exist_ok=True)
    assert not (S/'PURPOSE121_TYPED_WM_CLOSURE_BINDING.json').exists()
    assert not (S/'FROZEN_UNUSED121_SOURCE_AND_PURPOSE_INDEX.json').exists()
    q=read(PARENT);B=Path(q['source_payload'])
    assert q['formal_SHA']=='78f5840ec3db38a3fe2c8c16852b81a5bc7f02b445acd4a7901dafc7078d9976'
    assert q['formal_bytes']==256240073 and Path(q['formal_local_path']).stat().st_size==q['formal_bytes']
    assert Path(q['raw_control_producer']['local_path']).stat().st_size==q['raw_control_producer']['bytes']
    case=read(q['actual_case_report'])
    assert case['actual_waited_exit']==0 and case['case']['passed'] and not case['errors']
    assert case['case']['result']['controls']==431
    text_root=PARENT.parent/'actual_case_text'
    fresh_paths=list(text_root.glob('*FRESH_N1_SOURCE_SDK_RESET_GAS_BEFORE_FORWARD_ACTUAL.json'))
    render_paths=list(text_root.glob('*ACTUAL_RENDER_GEOMETRY.json'))
    assert len(fresh_paths)==len(render_paths)==1
    fresh=read(fresh_paths[0]);render=read(render_paths[0])
    contract=B/'job0/assets/import_contract.json'
    own=B/'source/OWN_STEP_WHEEL_GEOMETRY_FROM_R2_SOURCE.json'
    physical=B/'job0/runtime/isaac/mod4/mod4_task.py'
    run_manifest=B/'job0/original_run_manifest.json'
    grace=int(read(run_manifest)['env'].get('RM_SPAWN_GRACE_STEPS','10'))
    assert grace==10
    d120=T/'MOD4_H1_OVERNIGHT_FUDAN_SUPERMIMIC_REPAIR_GOAL_20261027/native120_original_closure_vs_imagined_stop_CPU_review_v1'
    candidate=d120/'native120_imagined_original_closure_stop_SOURCE_ONLY.py'
    assert H(candidate)=='38f0297ebfb00bf70740e031be1f288effb0f2e3613a642ab6f6738d7a94793b'
    extra=[PARENT,Path(q['qualified116_CPU']),Path(q['actual_case_report']),
        fresh_paths[0],render_paths[0],contract,own,physical,run_manifest,candidate]
    for p in [*S.glob('*.py'),Path(__file__)]:
        ast.parse(p.read_bytes().decode('utf-8-sig'))
    cpu=Path('C:/Users/lulu/miniconda3/envs/env_isaaclab/python.exe')
    env=os.environ.copy();env['CUDA_VISIBLE_DEVICES']=''
    fixture=S/'qualify121_source_synthetic_before_inputs_once.py'
    result=subprocess.run([str(cpu),'-u','-B','-X','utf8',str(fixture)],env=env,capture_output=True)
    put(R/'SOURCE121_SYNTHETIC_EXECUTION_RECEIPT.json',dict(epoch=time.time(),
        executable=str(cpu),argv=['-u','-B','-X','utf8',str(fixture)],
        returncode=result.returncode,stdout=result.stdout.decode('utf-8'),stderr=result.stderr.decode('utf-8'),
        checkpoint_or_control_raw_reads=0))
    assert result.returncode==0, 'source fixture refused; preserve error, do not load actual inputs'
    assert read(R/'SOURCE121_SYNTHETIC_TYPED_DOMAIN_AND_ACTUAL_ACTION_SEQUENCE_CPU.json')['passed_source_CPU_only']
    binding=dict(phase='NEW121_actual_action_WM_closure_false_stop_CPU',
        purpose='Calibrate source120 original2mm closure mask against actual118 original body-anchor flags, actual-q FK and qualified116 WM predicted-q over all physically contiguous1/8/32 actual-action windows before considering any new H1 learning.',
        source_payload=str(B),manifest=q['manifest'],manifest_SHA=q['manifest_SHA'],source_PY_rows=q['source_PY_rows'],
        parent_display_binding=str(PARENT),parent_display_binding_SHA=H(PARENT),
        qualified116_CPU=q['qualified116_CPU'],qualified116_CPU_SHA=q['qualified116_CPU_SHA'],
        formal_local_path=q['formal_local_path'],formal_SHA=q['formal_SHA'],formal_bytes=q['formal_bytes'],
        expected_header=dict(iteration=20809,world_updates=208090,policy_updates=19977),
        expected_controls=431,raw_control_producer=q['raw_control_producer'],
        import_contract=str(contract),own_geometry=str(own),original_physics_source=str(physical),
        actual_joint_names=fresh['actual_names'],actual_body_names=render['body_names'],
        original_threshold_m=.002,original_grace_controls=grace,
        horizons=[1,8,32],CPU_wall_budget_seconds=480,maximum_checkpoint_decodes=1,maximum_control_raw_reads=1,
        maximum_separate_normal86_reads=0,only_WM_forward=True,
        no_Pi_Critic_optimizer_GPU_SDK_physics_SSH_account_Task_GO=True,
        one_step_actual_action6_before_original_PD_queue_with_aux54_last_processed_state=True,
        static_DR_xi31_each_offset_not_future_dynamic_truth=True,
        request_onset_crossing_separate_from_same_request_phase_windows=True,
        no_27cm_or_general_WM_accuracy_or_unique_root_cause_claim=True,
        additional_small_source_and_receipts=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p)) for p in extra])
    put(S/'PURPOSE121_TYPED_WM_CLOSURE_BINDING.json',binding)
    source_files=[dict(path=str(p),bytes=p.stat().st_size,SHA=H(p))
        for p in sorted([*S.glob('*.py'),Path(__file__).resolve()])]
    put(S/'FROZEN_UNUSED121_SOURCE_AND_PURPOSE_INDEX.json',dict(epoch=time.time(),
        status='FROZEN_UNUSED_NEW_NUMERICAL_PURPOSE_NOT_TRAINING',source_files=source_files,
        binding_SHA=H(S/'PURPOSE121_TYPED_WM_CLOSURE_BINDING.json'),
        source_fixture_report_SHA=H(R/'SOURCE121_SYNTHETIC_TYPED_DOMAIN_AND_ACTUAL_ACTION_SEQUENCE_CPU.json'),
        control_raw_reads=0,checkpoint_decodes=0,all_actual_input_reads_only_in_new_selected_entry=True))
    print(json.dumps(dict(passed_source_and_typed_purpose=True,source_files=len(source_files),
        source_rows=len(q['source_PY_rows']),controls=431,formal_SHA=q['formal_SHA'],
        raw_reads=0,model_decodes=0)),flush=True)


if __name__=='__main__':
    try:
        main()
    except BaseException:
        R.mkdir(exist_ok=True)
        put(R/('SOURCE121_PREPARATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json'),
            dict(epoch=time.time(),traceback=traceback.format_exc(),checkpoint_raw_NPZ_reads=0,no_retry=True))
        raise
