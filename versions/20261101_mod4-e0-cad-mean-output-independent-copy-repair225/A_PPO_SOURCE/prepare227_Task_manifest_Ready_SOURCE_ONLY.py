"""ROOT metadata-only preparation after fresh admission; never GO or launch.

The first two inputs are saved original219 closing and NEWformal CPU reports.
The third is ROOT's new CNone/CIM/resource projection with actual receipt SHAs.
The emitted files go into a NEW local staging directory, then ROOT installs
and verifies them in one new sole-owner job. No selected PT is copied/hashed.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
from contract227 import (KIND, WORKER_KIND, SHA, SOURCE_BYTES, ITER, ADAM, LR,
    PRIOR_UPDATES, GENERATION, CPU_SHA, SOURCE_MODEL, metadata, qualified,
    fresh_admission, validate_task, validate_ready)


def encode(v):
    return json.dumps(v, indent=2, allow_nan=False).encode()


def main():
    p = argparse.ArgumentParser()
    for name in ('qualified-closing', 'qualified-cpu', 'fresh-admission', 'install-rows', 'out'):
        p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--job-root', required=True)
    p.add_argument('--run-id', required=True)
    a = p.parse_args()
    closing, cr = metadata(a.qualified_closing)
    cpu, qr = metadata(a.qualified_cpu)
    q = qualified(closing, cpu, qr['SHA'])
    fresh, fr = metadata(a.fresh_admission)
    fresh_admission(fresh, q['historical219_closed_epoch'])
    installation, ir = metadata(a.install_rows)
    assert installation['schema'] == 'mod4.227.install.v1'
    job = PurePosixPath(a.job_root)
    assert job.is_absolute() and str(job) != str(PurePosixPath(SOURCE_MODEL).parent.parent)
    assert a.run_id and fresh['run_id'] == a.run_id and fresh['new_job_root'] == str(job)
    files = [{k:r[k] for k in ('relative','bytes','SHA')} for r in installation['files']]
    byname = {r['relative']:r for r in files}
    assert all(not r['relative'].endswith(('.pt','.partial','.active')) for r in files)
    evidence = dict(kind='ROOT227_QUALIFIED_AND_FRESH_ACTUAL_JOIN', qualification=q,
                    saved_closing=cr, saved_NEWformal_CPU=qr, fresh_actual=fresh,
                    fresh_admission_ref=fr, installation_ref=ir,
                    historical219_owner_binding_is_not_current=True)
    evidence_raw = encode(evidence)
    evidence_sha = hashlib.sha256(evidence_raw).hexdigest()
    task = dict(kind=WORKER_KIND, launch_contract_kind=KIND, run_id=a.run_id,
        role_key='w35_72', num_envs=20000, GPU_UUID=fresh['GPU_UUID'], source_SHA=SHA,
        source_bytes=SOURCE_BYTES, source_iteration=ITER, source_Adam_step=ADAM, source_LR=LR,
        source_prior_new_PPO_updates=PRIOR_UPDATES, model_path=SOURCE_MODEL,
        original_canonical_generation=GENERATION, manifest_file='MANIFEST227.json',
        worker_SHA=byname['worker_full227.py']['SHA'], full_worker227_SHA=byname['worker_full227.py']['SHA'],
        selected219V3_fullstate_CPU_proof_SHA=CPU_SHA, selected219V3_fullstate_CPU_proof_reused=True,
        actual_scene0PT211_passed=True, actual_robot0PT212_passed=True,
        new_RM70_geometry_course_and_xyzw_source_reviewed=True,
        same_RM70_profile_fullstate_restore_required=True, actual_shared_material20k0PT_passed=True,
        actual_material_limit_error_count=0, actual_private_EX_held_by_parent=True,
        source_read_purpose=dict(physical_byte_opens=1, decodes=1, source_bytes=SOURCE_BYTES),
        max_parent_seconds=3900, save_after_seconds=3600, exit_headroom_seconds=300,
        launch_evidence_SHA=evidence_sha, actual_source_model_local_CPU_reads=0)
    validate_task(task)
    task_raw = encode(task)
    files.append(dict(relative='TASK.json', bytes=len(task_raw), SHA=hashlib.sha256(task_raw).hexdigest()))
    manifest = dict(kind='ROOT227_NEW_SOLE_JOB_SOURCE_MANIFEST', files=files,
        input_model_metadata=dict(path=SOURCE_MODEL, bytes=SOURCE_BYTES, SHA=SHA),
        source_scope='full actor35/critic38/STD6/17Adam649720/LR/D0-D7/RM70 assignment+commands;new physical episode')
    manifest_raw = encode(manifest)
    manifest_sha = hashlib.sha256(manifest_raw).hexdigest()
    ready = dict(passed=True, kind=KIND, manifest_SHA=manifest_sha, source_SHA=SHA,
        source_iteration=ITER, Adam_step=ADAM, source_LR=LR,
        source_fullstate_CPU_passed=True, source_saved_fullstate_CPU_SHA=CPU_SHA,
        all_actor_critic_optimizer_tensors_finite=True, actual_35_38_6_shapes=True,
        launch_evidence_SHA=evidence_sha, fresh_CNone_CIM_and_resources_passed=True,
        same_RM70_profile_fullstate_restore_required=True, actual_shared_material20k0PT_passed=True,
        actual_material_limit_error_count=0, status='METADATA_READY_ROOT_ORIGINAL_OWNER_ONLY_NO_GO')
    assert validate_ready(ready, dict(manifest_SHA=manifest_sha, launch_evidence_SHA=evidence_sha))
    spec = dict(key='w35_72', role='node', run_id=a.run_id, execution_backend='target72',
        GPU_UUID=fresh['GPU_UUID'], num_envs=20000, job_root=str(job), worker_script='worker227.py',
        source_SHA=SHA, source_iteration=ITER, source_Adamstep=ADAM, source_LR=LR, source_kind=KIND,
        max_parent_seconds=3900, exit_headroom_seconds=300, no_physics_change=True,
        prelaunch_control_snapshot_id=fresh['control_snapshot_id'], manifest_file='MANIFEST227.json',
        manifest_SHA=manifest_sha, launch_evidence_SHA=evidence_sha)
    # Python/private_lock/token/owner endpoint are supplied by the original ROOT
    # solo installer, never guessed here or taken from the historical219 owner.
    a.out.mkdir(exist_ok=False)
    for name, raw in [('PRELAUNCH227_ACTUAL_EVIDENCE.json',evidence_raw),('TASK.json',task_raw),
                      ('MANIFEST227.json',manifest_raw),('ADMISSION227_READY.json',encode(ready)),
                      ('SPEC227_ORIGINAL_OWNER_FIELDS.json',encode(spec))]:
        with (a.out/name).open('xb') as f:
            f.write(raw)
    print(json.dumps(dict(source_only=True, manifest_SHA=manifest_sha, launch_evidence_SHA=evidence_sha,
                          source_PT_reads=0, GO_created=False)))


if __name__ == '__main__':
    main()
