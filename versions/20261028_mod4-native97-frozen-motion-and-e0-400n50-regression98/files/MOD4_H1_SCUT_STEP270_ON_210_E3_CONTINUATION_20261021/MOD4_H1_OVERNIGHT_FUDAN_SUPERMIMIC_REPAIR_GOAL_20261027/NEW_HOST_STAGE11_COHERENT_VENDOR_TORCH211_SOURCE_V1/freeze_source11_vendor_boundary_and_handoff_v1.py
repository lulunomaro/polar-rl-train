"""Source AST/byte checks and handoff only; no installer/SSH/model execution."""
from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;L=B.parent;S=L/'NEW_HOST_STAGE10_TINY_PACKAGING_TLS_SHA_CACHE_CONTINUE_V1'
hp=B/'owned_stage11_coherent_vendor_Torch211_supervisor_v1.py';ep=B/'pinned86_launch_NEW_coherent_vendor_Torch211_stdin_once_v11.py'
old=(S/'owned_stage10_same_vendor_tiny_wheel_supervisor_v1.py').read_text();new=hp.read_text();entry=ep.read_text()
def functions(text):return {n.name:ast.get_source_segment(text,n) for n in ast.parse(text).body if isinstance(n,ast.FunctionDef)}
a=functions(old);b=functions(new)
for name in ['put','status','ident','own_out','emit','H','environment']:assert a[name]==b[name]
restored=b['supervise'].replace("lock=(OLDVENV/'MOD4_OWN_RUNTIME_INSTALLER.lock')","lock=(VENV/'MOD4_OWN_RUNTIME_INSTALLER.lock')").replace('STAGE11_PACKAGES_AND_SOURCE_REGISTRATION_PASSED_ACTUAL','STAGE10_PACKAGES_AND_SOURCE_REGISTRATION_PASSED_ACTUAL')
assert restored==a['supervise']
ast.parse(entry);assert 'R.mkdir(parents=True,exist_ok=True)' in entry and entry.index('R.mkdir(parents=True,exist_ok=True)')<entry.index("save('STAGE11_STDIN_ENTRY_ENTERED_ACTUAL.json'")
assert entry.count("secret=req.pop('password')")==1 and "PIN_MISMATCH_BEFORE_AUTH" in entry and entry.index("actual==PIN")<entry.index('t.auth_password')
assert '--no-deps' not in new and new.index("command('joint_all_runtime_metadata_resolution_before_large_Torch_download'")<new.index("command('install_all_joint_required_dependencies'")<new.index("command('pip_check_all_required_dependencies'")
assert 'before=runtime_rows();assert before==oldproof' in new and 'assert runtime_rows()==before' in new
for node in ast.walk(ast.parse(new)):
 if isinstance(node,ast.Import):assert not any(x.name.split('.')[0] in ('torch','isaaclab','isaacsim','pxr') for x in node.names)
 if isinstance(node,ast.ImportFrom):assert (node.module or '').split('.')[0] not in ('torch','isaaclab','isaacsim','pxr')
proof=dict(epoch=time.time(),passed_source_CPU_AST_only=True,old_lifecycle_exact_inverse_bytes_after_two_declared_binding_replacements=True,all_seven_shared_helpers_byte_identical=True,secret_STDIN_only_pin_before_auth=True,report_directory_before_marker=True,new_venv_and_all_writes_project_only=True,complete_runtime_resolution_before_install_then_pipcheck=True,unchanged_runtime_PY_checks_before_after=True,no_Torch_SDK_model_or_GPU_import_executed=True,actual_newhost_packages_CPU_CUDA_restore_physics_pending=True,source_only_no_training_claim=True)
with (B/'SOURCE_CPU_AST_EXACT_LIFECYCLE_AND_VENDOR_BOUNDARY_ACTUAL_V1.json').open('x',encoding='utf8') as f:json.dump(proof,f,indent=2)
handoff='''SELECTED unused entry pinned86_launch_NEW_coherent_vendor_Torch211_stdin_once_v11.py --max-seconds 1800 (2400 supported). Root alone supplies one noecho JSON host/username/password by stdin memory after fresh exactLOCAL CIM and global SSH lease. Source entry creates reports before marker; no secret argv/file/output, pin8adc87f3e75eb307a2429fa97b68761e09c0636b0eea684c71894438757c788b before auth. Startup connection only <=120s; owned supervisor/installer detached exact IDs returned and no other watcher. Never rerun old Stage10 or this consumed entry.

New owned run /data/robemo/polar-rl-train/setup_runs/W35_VENDOR_TORCH211_COHERENT_RUNTIME_20261028_V11; new isolated environment /data/robemo/polar-rl-train/runtime_envs/vendor_sim601_torch211_lab_test_packaging26_v3. Existing2.10 env and all previous failures unchanged. Same original installer lock in owned7B env acquired without deletion; original known-child bounded lifecycle exact except new pass marker/old-lock alias. No GPU/Torch/SDK/model/account operations; CUDA_VISIBLE_DEVICES empty.

Actual Stage10 full primary proves core6.0.1.0 requires Torch2.11.0; old2.10 constraint cannot be jointly satisfied. Official target cu128 cp312 torch2.11.0+cu128 SHA d252cf975fb18c94a85336323ad425f473df56dab35a44b00399bd70c7a3b997; matching vision0.26.0+cu128 ccf26b4b659cfce6f2208cb8326071d51c70219a34856dfdf468d1e19af52c0d. Official PEP658 metadata SHAs both passed; vision requires torch==2.11.0 and targetTorch uses cuda-toolkit12.8.1. Default PyPI Torch metadata is CUDA13 and is explicitly not the selected build. Existing small-selector format failure retained; offline existing-byte semantic finisherV2 passed, no refetch.

Only two old vendor constraints change Torch2.10/vision.25 to2.11/.26, exact inverse proof at target. Keep Sim6.0.1.0/RSL5/Lab6.1.14 original runtime.py, prior explicit test-coverage extra split and packaging26 metadata change, NumPy2.3.1 and every other pin. Reuse existing S9 builtSDKwheels/cache, verifiedS8 5.88GB Kit and S10 tiny packaging26 wheel. A project-local HTML points to only the two original published CUDA wheel URLs with their SHA/PEP658 attributes; full joint dry-run resolves ALL runtime requirements before install and pipcheck. No --no-deps for runtime. Pip may download/cache required wheels during resolution; completed/partial bytes remain. All logs and terminal proof will be collected by one later new-purpose readonly reader, not 5min polls.

This explicitly differs from72 Torch environment. Package/pipcheck pass would NOT prove SDKready: newhost headless SDK/source/fullstate CPU/CUDA private RNG/optimizer/physics40050/firstPPO admission remains mandatory before training. No second canonical writer/GO. Current source only; root approval/secure ingress and actual results pending. All source/primary full text/old false within this folder ordinaryGit; no new trial/tag merely for source.
'''
with (B/'HANDOFF_FROZEN_STAGE11_COHERENT_VENDOR_V1.md').open('x',encoding='utf8') as f:f.write(handoff)
rows=[]
for p in sorted(B.rglob('*')):
 if p.is_file():rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA=hashlib.sha256(p.read_bytes()).hexdigest()))
index=B/'FROZEN_STAGE11_COHERENT_VENDOR_SOURCE_INDEX_V1.json'
with index.open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),source_frozen=True,actual_86_install_not_yet_executed=True,source_proof=proof,files=rows),f,indent=2)
print(json.dumps(dict(passed=True,index=str(index),index_SHA=hashlib.sha256(index.read_bytes()).hexdigest(),entry_SHA=hashlib.sha256(ep.read_bytes()).hexdigest(),helper_SHA=hashlib.sha256(hp.read_bytes()).hexdigest())))
