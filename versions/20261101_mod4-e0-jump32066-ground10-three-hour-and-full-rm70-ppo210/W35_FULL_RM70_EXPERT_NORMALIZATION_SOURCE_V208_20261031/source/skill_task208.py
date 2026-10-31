"""Typed NEW208 frozen W35 skill caller, root binds actual job/GPU/receipts."""
import os

MODEL = 'ad504fec819b22f10fd1caf7befc59c1988c7609fe15373ab8851ef95942df3f'
MODEL_BYTES = 17619013
KIND = 'MOD4_W35_FULL_WORLD_SKILL208'
JOB = os.environ.get('MOD4_NEW208_FROZEN_JOB_ROOT', 'UNBOUND_NEW208_JOB')
GPU = os.environ.get('MOD4_NEW208_FROZEN_GPU_UUID', 'UNBOUND_NEW208_GPU')
CPU_REPORT = 'NEW208_TARGET_SOURCE_METADATA_ACTUAL.json'
CPU_WAIT = 'NEW208_TARGET_CPU_WAIT_ACTUAL.json'
FULLRESTORE = 'NEW208_W35_CUDA_FULLRESTORE_ACTUAL.json'
NATIVE = 'NEW208_W35_NATIVE24_ACTUAL.json'
QUEUE = 'NEW208_W35_NATIVE24_QUEUE_ACTUAL.json'
NATIVE_COMPLETE = 'NEW208_NATIVE24_PUBLICATIONS_CLOSED.json'
ORIGIN = 'NEW208_W35_INITIAL_REAL_ORIGIN_ACTUAL.json'
FINAL = 'NEW208_W35_FULL_WORLD_SKILL_ACTUAL.json'
CONTROL_COUNT = 1600
WARMUP = 100
ADAM = 648360
ITERATION = 32336
LR = .00011390625000000003


def validate_task(task):
    assert JOB != 'UNBOUND_NEW208_JOB' and GPU.startswith('GPU-')
    assert task['kind'] == KIND and task['source_SHA'] == MODEL
    assert task['num_envs'] == 20000 and task['controls'] == CONTROL_COUNT
    assert task['warmup_controls'] == WARMUP and task['maximum_worker_seconds'] == 1680
    assert task['no_optimizer_steps'] is True
    assert task['actual_target_SDK_source_admission_passed'] is True
    assert task['actual_private_GPU_EX_held_by_parent'] is True
    assert task['canonical72_known_owner_readonly_passed'] is True
    assert task['original_Adam'] == ADAM and task['original_RSL_iteration'] == ITERATION
    assert task['original_LR'] == LR
    assert task['original_rough_route_and_command_domain_unmodified'] is True
    assert task['early_original_event_required'] is True
    assert task['initial_start_must_not_be_fabricated'] is True
    assert task['new208_full_world_fields_required'] is True
    assert task['full_native_WM_dataset_claimed'] is False
