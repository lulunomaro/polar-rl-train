"""CPU-only immutable capture of tested Windows ABI reference and dependency metadata.

This script never imports Isaac, initializes CUDA, installs packages, mutates source,
or writes outside its own directory. Original 20k runtime remains a separate prerequisite.
"""
from pathlib import Path
import ast, difflib, hashlib, json, time, zipfile, re
from importlib import metadata

D = Path(__file__).resolve().parent
W = D.parents[2]
L = W / 'MOD4_LOCAL_WAVE50_CONTINUE_20261013'
B = W / 'MOD4_E1_WAVE50_EPISODE_LIFETIME_REPAIR_20261012/shutdown_backup_1791808183793797400'
O = B / 'training/learning_logs/2026-10-12_19-47-02_e1_WAVE50_episode_lifetime_observation_1791805426881441339/e1_source_snapshot'
LAB = Path('F:/isaacsim/IsaacLab')
NAMES = ['chassis_pd_nominal_readback.py', 'e1_full_pose_reset.py',
         'e1_scene_query_resource.py', 'e1_terrain_runtime.py',
         'mod4_task.py', 'wave50_entry_full_pose_reset_v2.py']

def h(b):
    return hashlib.sha256(b).hexdigest()

def capture(p, arc, *, original=None, applied=True):
    b = p.read_bytes()
    assert not re.search(br'-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----', b)
    if p.suffix == '.py':
        compile(b, str(p), 'exec')
    row = {'path': str(p), 'archive': arc, 'bytes': len(b), 'sha256': h(b),
           'apply_to_20k_abi_overlay': applied}
    if original is not None:
        old = original.read_bytes()
        row['original_source459'] = {'path': str(original), 'bytes': len(old), 'sha256': h(old)}
        row['diff_utf8'] = ''.join(difflib.unified_diff(
            old.decode('utf8').splitlines(True), b.decode('utf8').splitlines(True),
            str(original), str(p)))
    return row, b

Z = D / 'TESTED_WINDOWS_ABI_REFERENCE_20K_NO_CAP_CHANGE_20261013.zip'
M = D / 'TESTED_WINDOWS_ABI_REFERENCE_20K_NO_CAP_CHANGE_20261013_MANIFEST.json'
assert not Z.exists() and not M.exists()
rows = []
with zipfile.ZipFile(Z, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as z:
    for n in NAMES:
        p = L / 'runtime/isaac/mod4' / n
        r, b = capture(p, 'windows_abi_reference/overlay/isaac/mod4/' + n,
                       original=O / 'isaac/mod4' / n)
        rows.append(r); z.writestr(r['archive'], b)
    p = L / 'local_physx_api.py'
    r, b = capture(p, 'windows_abi_reference/local_physx_api.py')
    rows.append(r); z.writestr(r['archive'], b)
    # Only preserve the local128-only extra branch as an explicitly unused reference.
    n = 'wave50_entry_runtime_v2.py'
    p = L / 'runtime/isaac/mod4' / n
    r, b = capture(p, 'windows_abi_reference/unused128projection_reference/' + n,
                   original=O / 'isaac/mod4' / n, applied=False)
    rows.append(r); z.writestr(r['archive'], b)
    manifest = {
        'epoch': time.time(), 'file_rows': rows,
        'prerequisite_source459_zip_sha256': '01b9180a42b2fda8df4f869f552a4c7e9dc0dc06ff017e0b78bfe503808eb382',
        'SDK_zip_sha256': 'bfd6eb54412091a119659b538e02f90279b822951fe593ae726e06a15caf1a44',
        'actual_original_20k_checkpoint_SHA': 'd05c2f3ce1acc7988137f94a8853be0a6ac686d53225ef000821031bd1ffe64a',
        'scope': 'Tested local Windows API and quaternion ABI reference. 20k worker is separately reviewed and owned by repair_payload agent.',
        'apply_only_overlay_six_and_local_API': True,
        'keep_original_source459_wave50_entry_runtime_v2_for20k': True,
        'excluded_local128_state_projection_and_worker_and_buffer_caps': True,
        'original20k_PhysX_capacities_not_lowered': True,
        'SDK_files_not_modified': True, 'no_GPU_no_training_no_OS_changes': True,
        'metadata_identity_must_disclose_changed_source_ABI_SHA': True,
        'checkpoint_fullrestore_must_keep_actual_DR_RNG_tensor_schema_strict': True,
        'Windows_backend_not_claimed_Linux_PhysX_equivalent': True,
        'TensorDict_before_any_Isaac_module_required': True,
        'Windows_save_handle_must_r_plus_b_flush_fsync': True,
        'original_default_encoding_reader_rejection': {
            'operation': 'readonly difflib first attempt with Path.read_text default GBK',
            'error': "UnicodeDecodeError: 'gbk' codec cannot decode byte 0xae in position 10519",
            'source_mod4_task_unchanged': True, 'repair': 'independent explicit UTF8 reader only',
            'GPU_or_write_had_occurred': False},
    }
    z.writestr('WINDOWS_ABI_REFERENCE_MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2).encode('utf8'))
with zipfile.ZipFile(Z) as z:
    for r in rows:
        assert h(z.read(r['archive'])) == r['sha256']
manifest['zip'] = {'path': str(Z), 'bytes': Z.stat().st_size, 'sha256': h(Z.read_bytes())}
M.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps({'ABI_zip': manifest['zip'], 'file_count': len(rows), 'manifest': str(M)}), flush=True)

DEP = D / 'TESTED_FOURPKG_DEPENDENCIES_AND_LOCAL_DIST_ACTUAL.json'
assert not DEP.exists()
pkgs = {}
for name in ('isaaclab', 'isaaclab_rl', 'isaaclab_assets', 'isaaclab_tasks'):
    dist = metadata.distribution(name)
    setup = LAB / 'source' / name / 'setup.py'
    tree = ast.parse(setup.read_text(encoding='utf8'))
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and
             ((isinstance(n.func, ast.Name) and n.func.id == 'setup') or
              (isinstance(n.func, ast.Attribute) and n.func.attr == 'setup'))]
    assert len(calls) == 1
    args = {kw.arg: ast.unparse(kw.value) for kw in calls[0].keywords
            if kw.arg in ('install_requires', 'extras_require', 'python_requires', 'version')}
    pkgs[name] = {
        'version': dist.version, 'source_setup_path': str(setup),
        'source_setup_sha256': h(setup.read_bytes()), 'actual_setup_dependency_AST': args,
        'installed_metadata_requires_dist': dist.metadata.get_all('Requires-Dist') or [],
        'metadata_is_tested_local_reference_not_remote_install_receipt': True}
all_versions = sorted([{'name': dist.metadata['Name'], 'version': dist.version}
                       for dist in metadata.distributions()], key=lambda x: x['name'].lower())
core = {name: metadata.version(name) for name in (
    'isaacsim', 'torch', 'torchvision', 'rsl-rl-lib', 'tensordict', 'numpy',
    'scipy', 'warp-lang', 'psutil', 'gymnasium', 'h5py', 'setuptools')}
deps = {'epoch': time.time(), 'four_packages': pkgs, 'tested_core_versions': core,
        'actual_local_distribution_versions_reference': all_versions,
        'do_not_upgrade_torch_or_numpy_when_satisfying_sdk_requires': True,
        'recommended_editable_arguments': '--no-deps --no-build-isolation',
        'requirement_installation_owned_by_io_dr_agent_not_this_CPU_script': True,
        'not_a_remote_runtime_install_success_receipt': True,
        'no_environment_installed_or_mutated': True}
DEP.write_text(json.dumps(deps, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps({'dependency_report': str(DEP), 'core_versions': core,
                  'distribution_count': len(all_versions)}), flush=True)
