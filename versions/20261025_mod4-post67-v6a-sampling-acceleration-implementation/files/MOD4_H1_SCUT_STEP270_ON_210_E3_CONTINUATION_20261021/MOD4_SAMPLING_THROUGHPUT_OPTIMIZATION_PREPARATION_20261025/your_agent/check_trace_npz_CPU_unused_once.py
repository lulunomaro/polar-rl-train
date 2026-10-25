"""Independent local CPU serialization experiment; no runtime or GPU imports."""
from __future__ import annotations
import gc, hashlib, io, json, platform, sys, time, traceback, zipfile, zlib
from pathlib import Path
import numpy as np
from trace_npz_writer_unused_v1 import write_arrays_npz, write_trace_rows_npz, sha256_file

B = Path(__file__).resolve().parent
T = B.parents[1]
REPORT = B / 'reports' / 'NPZ_CPU_MICROBENCH_V1_ACTUAL.json'
SOURCE = T / 'H1_STEP270_CLOSED67_SAVED_REPLAY_AFTER_V5_20261025' / 'SELECTED_RECORDED_MOTION.npz'
KEYS = ('policy35','critic38','root13','q30','joint_velocity','applied_torque','executed6',
        'history5ms','impulse','closure','mimic','public_request','event_expected',
        'progress_expected','progress_peak','progress_paid','step_stable_ticks','step_success',
        'step_wheel_crossed','takeoff_count','landing_count','recovery_count','episode',
        'reward_term_contribution','raw_sampled6','total_reward','done')


def put(value):
    REPORT.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf8')


def same_bytes(actual, expected):
    return actual.shape == expected.shape and actual.dtype == expected.dtype and actual.tobytes(order='C') == expected.tobytes(order='C')


def digest_arrays(arrays):
    digest = hashlib.sha256()
    for key, value in arrays.items():
        digest.update(key.encode());digest.update(value.dtype.str.encode())
        digest.update(repr(value.shape).encode());digest.update(memoryview(np.ascontiguousarray(value)).cast('B'))
    return digest.hexdigest()


def micro_checks():
    # Check NaN payloads, +/-zero, infinities, endian preservation, empty arrays,
    # scalar fields, and non-contiguous/Fortran arrays as serialization cases.
    special = np.array([0x00000000,0x80000000,0x7fc00001,0xffc00002,0x7f800000,0xff800000], dtype=np.uint32).view(np.float32)
    arrays = dict(special=special, endian=np.arange(7,dtype='>i4'), empty=np.empty((0,3),dtype=np.float32),
                  scalar=np.array(3.25,dtype=np.float32), noncontiguous=np.arange(60,dtype=np.int64).reshape(10,6)[:,::2],
                  fortran=np.asfortranarray(np.arange(24,dtype=np.float32).reshape(4,6)))
    results=[]
    for level in (1,3,6):
        buf=io.BytesIO();write_arrays_npz(buf,arrays,compresslevel=level);buf.seek(0)
        with np.load(buf,allow_pickle=False) as loaded:
            assert loaded.files==list(arrays)
            assert all(same_bytes(loaded[key],value) for key,value in arrays.items())
        results.append(dict(level=level,all_dtype_shape_array_bytes_exact=True,bytes=buf.getbuffer().nbytes))
        buf.close()
    rows=[dict(v=special[::2]),dict(v=special[1::2])]
    buf=io.BytesIO();write_trace_rows_npz(buf,rows,compresslevel=1);buf.seek(0)
    with np.load(buf,allow_pickle=False) as loaded:assert same_bytes(loaded['v'],np.stack([r['v'] for r in rows]))
    for bad in ({'object':np.array([object()],dtype=object)}, {'../bad':np.zeros(1)}):
        try:write_arrays_npz(io.BytesIO(),bad,compresslevel=1)
        except ValueError:pass
        else:raise AssertionError('Invalid schema must be rejected')
    fixture=B/'trace_npz_writer_unused_v1.py'
    assert sha256_file(fixture)==hashlib.sha256(fixture.read_bytes()).hexdigest()
    return dict(serialization_edge_cases=results,row_stacking_special_values_exact=True,
                invalid_schema_rejected=True,chunked_file_SHA_matches_read_bytes=True)


def synthetic_like_schema(selected):
    rng=np.random.Generator(np.random.PCG64(20261025))
    arrays={};parameters={}
    for key,sample in selected.items():
        shape=(24,20000,*sample.shape[2:]);zero_fraction=float(np.mean(sample==0))
        if sample.dtype.kind=='f':
            mean=float(np.mean(sample));std=max(float(np.std(sample)),1e-4)
            value=rng.standard_normal(shape,dtype=np.float32)
            value*=np.float32(std);value+=np.float32(mean)
            value[rng.random(shape,dtype=np.float32)<zero_fraction]=0
        elif sample.dtype.kind=='b':
            value=rng.random(shape,dtype=np.float32)<float(np.mean(sample))
        else:
            low=int(np.min(sample));high=int(np.max(sample))+1
            value=rng.integers(low,high,size=shape,dtype=sample.dtype)
        arrays[key]=value.astype(sample.dtype,copy=False)
        parameters[key]=dict(shape=list(shape),dtype=str(sample.dtype),selected_zero_fraction=zero_fraction,
                             synthetic_iid_distribution_not_actual_20k_trajectory=True)
    return arrays,parameters


def benchmark(name,arrays,repeats,report):
    rows=[{key:value[i] for key,value in arrays.items()} for i in range(24)]
    before=digest_arrays(arrays)
    variants=('numpy_original_allfield_stack_level6','helper_allfield_stack_level6',
              'helper_fieldwise_stack_level6','helper_fieldwise_stack_level3','helper_fieldwise_stack_level1')
    output=dict(dataset=name,raw_array_bytes=sum(v.nbytes for v in arrays.values()),
                max_field_stack_bytes=max(v.nbytes for v in arrays.values()),array_digest=before,
                fields=[dict(name=k,shape=list(v.shape),dtype=str(v.dtype),bytes=v.nbytes) for k,v in arrays.items()],samples=[])
    report['benchmarks'].append(output);put(report)
    for repeat in range(repeats):
        # Reverse order in repeat 1, preserving each actual timing record.
        order=variants if repeat%2==0 else tuple(reversed(variants))
        for variant in order:
            gc.collect();buf=io.BytesIO();start=time.perf_counter();cpu=time.process_time()
            if variant=='numpy_original_allfield_stack_level6':
                np.savez_compressed(buf,**{key:np.stack([row[key] for row in rows]) for key in arrays})
            elif variant=='helper_allfield_stack_level6':
                write_arrays_npz(buf,{key:np.stack([row[key] for row in rows]) for key in arrays},compresslevel=6)
            else:
                write_trace_rows_npz(buf,rows,compresslevel=int(variant[-1]))
            elapsed=time.perf_counter()-start;cpu_elapsed=time.process_time()-cpu
            view=buf.getbuffer();digest=hashlib.sha256(view).hexdigest();size=view.nbytes;view.release()
            verify_start=time.perf_counter();buf.seek(0)
            with np.load(buf,allow_pickle=False) as loaded:
                assert loaded.files==list(arrays)
                assert all(same_bytes(loaded[key],value) for key,value in arrays.items())
            verification_s=time.perf_counter()-verify_start
            output['samples'].append(dict(repeat=repeat,variant=variant,wall_s=elapsed,cpu_s=cpu_elapsed,
                                          compressed_bytes=size,archive_SHA=digest,exact_all_field_dtype_shape_and_array_bytes=True,
                                          verification_excluded_s=verification_s))
            buf.close();put(report)
            print(json.dumps(dict(dataset=name,repeat=repeat,variant=variant,wall_s=elapsed,compressed_bytes=size)),flush=True)
    assert digest_arrays(arrays)==before
    output['input_arrays_unchanged']=True
    output['medians']={variant:dict(wall_s=float(np.median([x['wall_s'] for x in output['samples'] if x['variant']==variant])),
                                    compressed_bytes=float(np.median([x['compressed_bytes'] for x in output['samples'] if x['variant']==variant]))) for variant in variants}
    baseline=output['medians'][variants[0]]
    for value in output['medians'].values():
        value['CPU_serialization_speed_factor_vs_original']=baseline['wall_s']/value['wall_s']
        value['compressed_size_ratio_vs_original']=value['compressed_bytes']/baseline['compressed_bytes']
    put(report)


def main():
    assert not REPORT.exists(),'Once-only report already exists; do not overwrite a completed experiment'
    report=dict(trial_id='MOD4_SAMPLING_CPU_NPZ_V1_20261025',epoch=time.time(),status='running',
                scope='Local isolated CPU serialization, memory BytesIO; no disk throughput, policy, physics, GPU or training.',
                Python=sys.version,numpy=np.__version__,zlib=zlib.ZLIB_RUNTIME_VERSION,platform=platform.platform(),
                helper_SHA=sha256_file(B/'trace_npz_writer_unused_v1.py'),script_SHA=sha256_file(__file__),
                source=dict(path=str(SOURCE),bytes=SOURCE.stat().st_size,SHA=sha256_file(SOURCE)),
                checkpoints_loaded=[],global_numpy_RNG_untouched=True,synthetic_generator='private PCG64 seed20261025',
                archive_bytes_change_by_compression_expected=True,old_producer_SHA_and_old_files_unchanged=True,
                no_retention_or_disk_guard_change=True,benchmarks=[])
    put(report)
    try:
        report['micro_checks']=micro_checks()
        with np.load(SOURCE,allow_pickle=False) as loaded:selected={key:loaded[key][:24] for key in KEYS}
        benchmark('saved_selected_24controls_x91envs_27originalfields_not_full20k',selected,3,report)
        synthetic,parameters=synthetic_like_schema(selected);report['synthetic_parameters']=parameters
        benchmark('synthetic_iid_same_24x20000_original27field_shapes_not_training',synthetic,2,report)
        report['status']='CPU_checks_passed_not_deployed';report['completed_epoch']=time.time();put(report)
    except BaseException:
        report['status']='original_error_retained';report['original_error']=traceback.format_exc();put(report);raise


if __name__=='__main__':main()
