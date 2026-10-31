"""ROOT saved-metadata Task builder, no model/asset/raw/SDK/network reads."""
from pathlib import Path
import argparse
import hashlib
import json
import time
from qualified227 import metadata, qualified, SHA, SOURCE_BYTES, ITER, ADAM, LR, SOURCE_MODEL, SOURCE_JOB

B = Path(__file__).resolve().parent
WORKER = 'evaluate227_CLOSED_W35_FULL_RM70_LOSSLESS_UNUSED_once.py'


def put(p, v):
    with p.open('x', encoding='utf8') as f:
        json.dump(v, f, indent=2, allow_nan=False)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--closing', type=Path, required=True)
    p.add_argument('--new-cpu', type=Path, required=True)
    p.add_argument('--GPU-UUID', required=True)
    p.add_argument('--out-new', type=Path, required=True)
    a = p.parse_args()
    closing, cr = metadata(a.closing)
    cpu, qr = metadata(a.new_cpu)
    qualified(closing, cpu, qr['SHA'])
    assert a.GPU_UUID in ('GPU-16828f91-2b45-b646-8dc0-9481138e2842','GPU-c27eecbd-6838-7290-1cd2-37e34522213d')
    a.out_new.mkdir(exist_ok=False)
    rows = []
    for name in (WORKER,'rm70_intervals227.py','positional_rows227.py','decode227_positional.py'):
        raw = (B/name).read_bytes()
        with (a.out_new/name).open('xb') as f:
            f.write(raw)
        rows.append(dict(relative=name,bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest()))
    shas = {r['relative']:r['SHA'] for r in rows}
    producer = dict(format='mod4.227.lossless_fieldset_positional_jsonl.v1',
        worker_SHA=shas[WORKER],observer_SHA=shas['rm70_intervals227.py'],
        writer_SHA=shas['positional_rows227.py'],decoder_SHA=shas['decode227_positional.py'],
        original_observer222_SHA='000e14607137c9d0221211da9ac6b86bc08deb6c3f4fdd380366fb4c9e8c5e12',
        unchanged_semantics='All original fields,values,UID/episode/parameter segment,pre-reset masks and union/counters retained',
        actual_byte_coverage='UNKNOWN_UNTIL_NEW_ACTUAL_CASE',retained_byte_limit=192*1024**2)
    task = dict(kind='NEW227_W35_CLOSED_FULL_RM70_SKILL_ONLY',epoch=time.time(),
        model_SHA=SHA,model_bytes=SOURCE_BYTES,model_path=SOURCE_MODEL,qualified219_job_root=SOURCE_JOB,
        model_iteration=ITER,Adam17=ADAM,model_new_PPO_updates=68,actual_saved_LR=LR,
        num_envs=20000,controls_max=1600,seconds_max=32.,physics_max=12800,feedback_max=3200,
        GPU_UUID=a.GPU_UUID,no_new_learning_or_GO=True,worker_seconds=3600,parent_seconds=3780,
        actual_current_CNone_private_shared_resources_admitted=False,worker_SHA=shas[WORKER],
        telemetry_producer=producer,model_physical_byte_reads=1,model_decodes=1,model_copies=0,
        old_5039_or_other_raw_reads=0,source_CPU_old_model_reads=0,default_JSONL_or_NPZ_transfer=False,
        current_authority='ROOT fresh canonicalCNone/exact LOCAL CIM/private+shared/resource checks required;all219 bindings historical',
        threshold_source='189 original max(.03,.1V) along/cross,.2signedyaw;original rough BODYvx absV',
        sampler='Original20%stand/BODYvx[-.3,.3]/vy=yaw0/12..16s;no directed command or reward change',
        full_expert_skill='UNKNOWN;old flat/world spin and other expert profiles unexposed',
        formal_qualification_refs=[cr,qr])
    put(a.out_new/'TASK227_PENDING_CURRENT_ADMISSION.json', task)
    put(a.out_new/'SOURCE227B_INSTALL.json', dict(files=rows, original_runtime_reused=SOURCE_JOB+'/runtime',
        model_metadata_only=True,source_model_copy_or_rehash=False,worker_wall_seconds=3600,parent_wall_seconds=3780))
    print(json.dumps(dict(source_task_created=True,current_target_admission=False,model_asset_raw_reads=0,GO=False)))


if __name__ == '__main__':
    main()
