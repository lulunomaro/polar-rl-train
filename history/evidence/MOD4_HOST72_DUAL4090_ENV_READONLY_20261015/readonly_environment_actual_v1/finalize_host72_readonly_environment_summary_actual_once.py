"""Summarize only observed host facts. Does not grant deployment or training."""
from pathlib import Path
import hashlib
import json
import time

D = Path(__file__).resolve().parent
R = D / 'reports'


def main():
    names = ['HOST72_READONLY_DISCOVERY_ACTUAL.json', 'HOST72_PYTHON_SIM_STACK_READONLY_ACTUAL.json',
             'HOST72_AVAILABLE_TORCH_LEGACY_METADATA_V2_ACTUAL.json']
    a, b, c = [json.loads((R / name).read_bytes()) for name in names]
    gpu_rows = [x.split(', ') for x in a['discovery']['gpu']['stdout'].strip().splitlines()]
    assert len(gpu_rows) == 2 and all(row[1] == 'NVIDIA GeForce RTX 4090' for row in gpu_rows)
    torch = c['details']['actual_torch_CUDA_enumeration']
    assert len(torch) == 2 and all(x['returncode'] == 0 and x['actual']['cuda_available'] and
                                 x['actual']['device_count'] == 2 for x in torch)
    v = dict(epoch=time.time(), host=a['host'], user=a['user'], inspection_only=True,
        gpu=[dict(index=int(row[0]), name=row[1], uuid=row[2], driver=row[3], memory_total_MiB=int(row[4]),
                  memory_used_MiB=int(row[5]), memory_free_MiB=int(row[6]), utilization_percent=int(row[7])) for row in gpu_rows],
        no_compute_processes_at_snapshot=not a['discovery']['gpu_processes']['stdout'].strip(),
        system=dict(OS='Ubuntu20.04.4LTS', kernel=a['kernel'], CPU='2xIntelXeonPlatinum8358P',
            physical_cores=64, logical_threads=128, memory_total_bytes=540654702592,
            installed_nvcc_toolkit='11.8.89', nvidia_smi_reported_CUDA='12.2'),
        disks=a['discovery']['disks'],
        actual_torch_import_and_two_GPU_enumeration=[x['actual'] for x in torch],
        no_tensor_compute_benchmark_or_Isaac_simulation_proven=True,
        checked_python_environments_no_resolved_IsaacSim_IsaacLab_RSL_RL_TensorDict=True,
        bounded_source_path_search_no_Isaac_matches=b['details']['isaac_related_paths_at_bounded_depth'] == [],
        not_exhaustive_machine_or_container_inventory=True,
        docker_daemon_read_denied=a['discovery']['docker'],
        data_path_access=b['details']['data_path_access'],
        original_reader_findings_preserved=dict(
            named_pytorch_env_exists_but_no_torch=True,
            Python37_importlib_metadata_reader_errors_preserved=True,
            legacy_pkg_resources_reader_successes=c['details']['legacy_metadata'],
            neither_error_is_GPU_hardware_failure=True),
        deployment_readiness='GPU enumeration and existing Torch imports succeed. Existing MOD4 Isaac/physics/DR/source/fullstate stack has not been deployed or admitted on this host. No training/deployment authority inferred from inspection.',
        evidence=[dict(path=str(R / name), bytes=(R / name).stat().st_size,
                       sha256=hashlib.sha256((R / name).read_bytes()).hexdigest()) for name in names],
        credentials_not_saved=True, no_remote_source_install_training_signal_or_budget_mutation=True,
        existing210_249_transport_and_frozen_evaluation_scopes_untouched=True)
    with (R / 'HOST72_DUAL4090_ENVIRONMENT_SUMMARY_ACTUAL.json').open('x', encoding='utf8') as f:
        json.dump(v, f, indent=2, ensure_ascii=False)
    note = '''Human explicitly authorized a read-only inspection of account lc01 at10.24.0.72, described as a dual4090 host. Credentials were entered via hidden input and not saved or archived. Three bounded SSH sessions read hardware, software metadata and existing interpreter imports; no packages, drivers, remote source files, training/simulation, tensor kernels, process signals, GPU benchmark or canonical budget changes were performed.

Actual hostamax Ubuntu20.04.4LTS/kernel5.15.0-70 has2xRTX4090 each24564MiB, driver535.54.03, both0% at initial snapshot with13MiB desktop occupancy and no compute jobs. CPU2xXeonPlatinum8358P/64cores128threads, RAM540654702592B, /data3753239007232B free but lc01 write permission metadata isfalse. Docker daemon access is denied, so container contents remain unknown. Installed nvcc11.8.89 differs from nvidia-smi reportedCUDA12.2; installed Torch builds are separately recorded.

Existing /opt/anaconda3 Python3.10.9 Torch2.0.1+cu118 and an existing l2t Python3.10.18 Torch2.7.1+cu126 actually import and enumerate both4090s withCUDAavailableTrue andcapability8.9. This is enumeration, not kernel, performance or Isaac simulation admission. Inspected module/distribution scopes and bounded directories found no IsaacSim/IsaacLab/RSL-RL/TensorDict; this is not an exhaustive filesystem or Docker proof. The misleadingly named pytorch_env has noTorch. Original attempts with Python3.7 lackedstdlib importlib.metadata and were retained; independent read-only pkg_resources metadata confirmed their oldTorch packages. No installed package was changed to fix a reader.

All original successes/errors/denied permissions, scripts and reports remain exact. This host has not been admitted as a MOD4 training worker. Existing physical/source/SDK/fullstate/DR/reset/resource/lease/budget requirements remain; no new S8/secondgate/PPO budget or automatic launch is authorized by this inspection. Existing210/249 scopes and all completed once/Tasks remain untouched. Archive as one unique diagnostic annotatedtrial; push failure resumes existingobjects only, with actual remote main/tag/peeled and all1347 oldtagobjects+peels verified. Credentials excluded; original report provenance retained.
'''
    with (D / 'HOST72_READONLY_STAGE_NOTE.txt').open('x', encoding='utf8') as f:
        f.write(note)
    print(json.dumps(dict(complete=True, gpu_count=2, actual_torch_two_GPU_enumeration=True,
                          Isaac_MOD4_runtime_not_admitted=True, no_deployment_training_or_budget_action=True)))


if __name__ == '__main__':
    main()
