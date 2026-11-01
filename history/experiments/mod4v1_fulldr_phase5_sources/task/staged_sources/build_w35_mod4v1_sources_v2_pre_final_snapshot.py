"""Build an EXCLUSIVE new reviewable source overlay; never install/launch/read PT.

Inputs are text source/JSON only. Original full worker/trainer semantics retained
except explicit new asset/closure, selected source and typed admission changes.
"""
from pathlib import Path
import argparse
import ast
import copy
import difflib
import hashlib
import json

HERE = Path(__file__).resolve().parent
PREFIX = 'runtime/isaac/mod4/'
OLD_CONTRACT_SHA = '517cd6a4cc469455af08da75dc4b7f7cb596b375bafb4c3e566c7df5bc51df49'
NEW_CONTRACT_SHA = 'bae3203a7c30f75e29c20c0b0d0e215af5edfc7dbeacb9ebc5310f7867c98755'
NEW_USD_SHA = '2c421a8ec66e425ee6e47341ed0803f2c7e84f1f50afcc726572027ef6566ef3'
NEW_KIND = 'MOD4V1_W35_LATEST32481_FULLD0D7_RM70_V2'
MODEL = dict(path='/home/lc01/Zonglin Li/zonglin2/tasks/MOD4_W35_QUALIFIED343E_CONTINUE227D_20261101_0712/w35_72/production/model_final_complete.pt',
             SHA='2d0bc7b87c30f2f1d7b9130de2afddd554aab1fd8fe398a7e597ec7354d5650b',
             bytes=17619333, iteration=32481, Adam17=651260, LR=.0002562890625000001,
             prior_new_PPO_updates=77, metadata_only_not_read_or_copied=True)


def require(value, message):
    if not value:
        raise ValueError(message)


def raw_text(path, expected=None):
    p = Path(path)
    require(p.suffix in ('.py', '.json', '.md'), 'Only source/metadata text reads')
    raw = p.read_bytes()
    h = hashlib.sha256(raw).hexdigest()
    require(expected is None or h == expected, 'Frozen source identity mismatch: ' + str(p))
    return raw.decode('utf-8-sig'), dict(path=str(p.resolve()), bytes=len(raw), SHA=h)


def J(value):
    return (json.dumps(value, indent=2, ensure_ascii=False, allow_nan=False) + '\n').encode('utf-8')


def replace(text, old, new, count=1):
    require(text.count(old) == count, 'Exact derivation anchor mismatch: ' + old[:160])
    return text.replace(old, new)


def replace_function(text, name, new_definition):
    tree = ast.parse(text)
    found = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == name]
    require(len(found) == 1, 'Exactly one original function expected: ' + name)
    node = found[0]
    lines = text.splitlines(keepends=True)
    lines[node.lineno-1:node.end_lineno] = [new_definition.rstrip() + '\n']
    return ''.join(lines)


def contract_diff(old, new):
    top = sorted(k for k in old.keys() | new.keys() if old.get(k) != new.get(k))
    require(set(top) <= {'bodies', 'enhancement', 'leg_motor', 'wheel_motor', 'physics_dt_s'},
            'Unexpected non-mass/metadata top-level model change')
    require(set(old['bodies']) == set(new['bodies']) and len(new['bodies']) == 31, '31-body ABI changed')
    names = sorted(k for k in old['bodies'] if old['bodies'][k] != new['bodies'][k])
    require(set(names) == {'chassis', 'left_shin', 'right_shin'}, 'Unexpected rigid-body change')
    changes = []
    for name in names:
        a, b = old['bodies'][name], new['bodies'][name]
        fields = sorted(k for k in a.keys() | b.keys() if a.get(k) != b.get(k))
        require(set(fields) <= {'mass_kg', 'com_m', 'diagonal_inertia_kg_m2', 'principal_axes_wxyz', 'enhancement_mass_basis'},
                'Geometry/kinematic body field changed: ' + name)
        target_delta = .132 if name == 'chassis' else -.029
        delta = b['mass_kg'] - a['mass_kg']
        require(abs(delta-target_delta) < 1.e-6, 'Wrong authorized motor delta: ' + name)
        changes.append(dict(body=name, mass_delta_kg=delta,
                            fields={k: {'old': a.get(k), 'new': b.get(k)} for k in fields}))
    all_changes = {k: {'old': old.get(k), 'new': new.get(k)} for k in top if k != 'bodies'}
    require(new['physics_dt_s'] == .0025, 'New contract must synchronize selected 2.5ms runtime metadata')
    return dict(kind='MOD4V1_EXACT_AUTHORIZED_ASSET_DIFF_V1',
        old_400N_contract_SHA=OLD_CONTRACT_SHA, new_contract_SHA=NEW_CONTRACT_SHA, new_USD_SHA=NEW_USD_SHA,
        changed_body_names=names, body_changes=changes, changed_top_level_keys=top,
        nonbody_contract_changes=all_changes,
        contract_geometry_unchanged=True,
        proof_scope='Computed exact JSON diff: all other top-level/unchanged-body geometry and kinematic fields equal; not an SDK/PhysX result',
        physics_dt_metadata_note='old JSON .0005 -> new .0025 matches already-selected 400N50 runtime dt; no new dt/solver experiment',
        actual_SDK_or_expert_adaptation_executed=False)


def required_schema(protocol):
    # Static extraction only: allow list(tuple_of_literals), no module execution.
    class Lists(ast.NodeTransformer):
        def visit_Call(self, node):
            require(isinstance(node.func, ast.Name) and node.func.id == 'list' and len(node.args) == 1
                    and isinstance(node.args[0], ast.Tuple), 'Unexpected executable schema expression')
            return ast.copy_location(ast.List(elts=node.args[0].elts, ctx=ast.Load()), node)
    assignment = next(n for n in ast.parse(protocol).body if isinstance(n, ast.Assign)
                      and any(isinstance(t, ast.Name) and t.id == 'REQUIRED_ROOT_INPUTS' for t in n.targets))
    return ast.literal_eval(Lists().visit(copy.deepcopy(assignment.value)))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--source-root', type=Path, required=True)
    p.add_argument('--adapter-dir', type=Path, required=True)
    p.add_argument('--asset-dir', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    a = p.parse_args()
    out = a.output.resolve()
    require(out.is_relative_to(HERE), 'Output must stay under authorized staged_sources')
    if out.exists():
        raise FileExistsError('REFUSE_OVERWRITE_NEW_OUTPUT: ' + str(out))
    root = a.source_root.resolve()
    base_manifest = root / 'W35_RM70_QUALIFIED_CONTINUATION_AND_LOSSLESS_EVAL_SOURCE_V227_20261101/A_PPO_SOURCE/reports/INSTALL227_SOURCE_ROWS_FROZEN.json'
    manifest_text, manifest_ref = raw_text(base_manifest)
    rows = {x['relative']: x for x in json.loads(manifest_text)['files']}
    inputs, output, patches = [manifest_ref], {}, []

    def source(relative):
        row = rows[relative]
        text, ref = raw_text(row['local_path'], row['SHA'])
        require(Path(row['local_path']).resolve().is_relative_to(root), 'Source outside declared project')
        inputs.append(dict(relative=relative, **ref))
        return text

    def emit(relative, text, original=None, original_name=None):
        require(relative not in output, 'Duplicate output path')
        output[relative] = text.encode('utf-8')
        if relative.endswith('.py'):
            ast.parse(text, filename=relative)
        if original is not None:
            patches.extend(difflib.unified_diff(original.splitlines(keepends=True), text.splitlines(keepends=True),
                fromfile=original_name or 'historical/'+relative, tofile='new/'+relative))

    worker0 = source('worker_full227.py')
    trainer0 = source(PREFIX+'train_full214.py')
    reset0 = source(PREFIX+'reset208_v3.py')
    config0 = source(PREFIX+'config214_training.py')
    cache = source(PREFIX+'source_cache208_v3.py')
    old_contract, old_ref = raw_text(rows['runtime/assets/import_contract.json']['local_path'], OLD_CONTRACT_SHA)
    new_contract, new_ref = raw_text(a.asset_dir/'import_contract.json', NEW_CONTRACT_SHA)
    inputs.extend([old_ref, new_ref])
    asset_diff = contract_diff(json.loads(old_contract), json.loads(new_contract))

    hook, hook_ref = raw_text(a.adapter_dir/'mod4v1_fresh_dr_guard.py',
                              '93a8ca97044a59bddbb83717c6e48cf04ef1696927d3d4eef37dec845fe4f4c6')
    inputs.append(hook_ref)
    protocol, protocol_ref = raw_text(HERE/'templates/mod4v1_w35_protocol.py')
    compat, compat_ref = raw_text(HERE/'templates/mod4v1_w35_asset_compat.py')
    inputs.extend([protocol_ref, compat_ref])

    # Only the obsolete asset identity check changes; bank/pose witness stays original.
    reset = replace(reset0, 'from W35_gas400_exact_selected_reset_compatibility_v2 import (\n            require_W35_exact_four_scalar_asset, verify_original_W35_selected_bank)',
        'from mod4v1_w35_asset_compat import (\n            require_mod4v1_asset_and_original_bank_geometry, verify_original_W35_selected_bank)')
    reset = replace(reset, 'env._w35_gas400_asset_compatibility = require_W35_exact_four_scalar_asset(',
                    'env._mod4v1_asset_compatibility = require_mod4v1_asset_and_original_bank_geometry(')
    emit(PREFIX+'reset208_v3.py', reset, reset0)
    emit(PREFIX+'config_mod4v1_w35.py', config0, config0, 'historical/config214_training.py')
    emit(PREFIX+'source_cache208_v3.py', cache)
    emit(PREFIX+'mod4v1_fresh_dr_guard.py', hook)
    emit(PREFIX+'mod4v1_w35_protocol.py', protocol)
    emit(PREFIX+'mod4v1_w35_asset_compat.py', compat)

    trainer = replace(trainer0, 'from learning208_v3 import RetentionLearningEnv as Mod4Env',
        "from mod4v1_fresh_dr_guard import (bind_before_task_import, verify_task_module, configure_new_task, FreshDRNominalGuard)\nMOD4V1_IDENTITY = bind_before_task_import(os.environ['MOD4V1_ASSET_DIR'])\nfrom learning208_v3 import RetentionLearningEnv as Mod4Env")
    trainer = replace(trainer, 'from config214_training import configure208 as configure_intro',
                      'from config_mod4v1_w35 import configure208 as configure_intro')
    trainer = replace(trainer, '    configure_intro(cfg)\n',
        '    configure_intro(cfg)\n    verify_task_module(mod4_task, MOD4V1_IDENTITY)\n    _mod4v1_original_thresholds=dict(closure=cfg.terminations.closure.params["threshold"],mimic=cfg.terminations.mimic.params["threshold"])\n    cfg.terminations.closure.params["threshold"]=.01  # explicit per-env episode reset in NEW task\n    cfg.terminations.mimic.params["threshold"]=.01  # explicit current task contract, old cfg is historical only\n    configure_new_task(cfg, MOD4V1_IDENTITY)\n    assert cfg.sim.physics is not None  # actual SDK6.1 field, not mock physx\n')
    trainer = replace(trainer, '    env = Mod4Env(cfg=cfg)\n', '    env = Mod4Env(cfg=cfg)\n    env._mod4v1_original_thresholds=_mod4v1_original_thresholds\n')
    start = trainer.index('    if args.init_checkpoint:\n', trainer.index('def main()'))
    end = trainer.index('    from checkpoint_cache208_v3 import install_e1_save_contract', start)
    old_restore = trainer[start:end]
    new_restore = (
        "    from mild_dr import tensor as nominal_tensor\n"
        "    nominal_guard = FreshDRNominalGuard(env, MOD4V1_IDENTITY, torch_module=torch, tensor_converter=nominal_tensor)\n"
        "    env._mod4v1_fresh_dr_guard = nominal_guard\n"
        "    with nominal_guard.around_original_fullstate_restore():\n" +
        ''.join('    '+line if line.strip() else line for line in old_restore.splitlines(keepends=True)) +
        "    Path(log_dir,'MOD4V1_FRESH_DR_NOMINAL_ACTUAL.json').write_text(json.dumps(nominal_guard.receipt(),indent=2))\n")
    trainer = trainer[:start] + new_restore + trainer[end:]
    trainer = replace(trainer, '    manifest["source_map"]=json.loads((Path(__file__).resolve().parents[2]/"reports/SOURCE_FREEZE.json").read_text())["sha256"]',
        '    manifest["historical_source_map"]=json.loads((Path(__file__).resolve().parents[2]/"reports/SOURCE_FREEZE.json").read_text())["sha256"]\n    manifest["mod4v1_derivation_index"]=json.loads((Path(os.environ["MOD4_NEW208_JOB_ROOT"])/"MOD4V1_DERIVATION_INDEX.json").read_text())')
    trainer = replace(trainer, 'manifest["active_expert"]="W35_RM70_FULL208"',
                      'manifest["active_expert"]="W35_MOD4V1_FULLD0D7_RM70"')
    trainer = replace(trainer, '    manifest["src_sha256"] = snapshot',
        '    for name in ("train_mod4v1_w35.py", "config_mod4v1_w35.py", "reset208_v3.py", "mod4v1_fresh_dr_guard.py", "mod4v1_w35_asset_compat.py", "mod4v1_w35_protocol.py"):\n        shutil.copy2(Path(__file__).parent/name,snapshot_dir/name);snapshot[name]=_sha256(Path(__file__).parent/name)\n    manifest["mod4v1_asset_identity"]=dict(USD_SHA=MOD4V1_IDENTITY.usd_sha256,contract_SHA=MOD4V1_IDENTITY.contract_sha256,closure_episode_m=.01,mimic_rad=.01)\n    manifest["D6_scope"]="original_gas_damping_not_all_joint_friction"\n    manifest["historical_termination_cfg"]=env._mod4v1_original_thresholds\n    manifest["src_sha256"] = snapshot')
    emit(PREFIX+'train_mod4v1_w35.py', trainer, trainer0)

    worker = replace(worker0, "SHA='343e0fd8f4950ffea2b09808a3bf88d9dd68e14b06f84c7bdaad462dbc8a51bd'",
                     "SHA='"+MODEL['SHA']+"'")
    worker = replace(worker, 'BYTES=17619269; ADAM=649720; ITER=32404; LR=.00017085937500000009',
                     'BYTES=17619333; ADAM=651260; ITER=32481; LR=.0002562890625000001')
    worker = replace(worker, "KIND='MOD4_W35_FULL_RM70_QUALIFIED343E_CONTINUE227'", "KIND='"+NEW_KIND+"'")
    worker = replace_function(worker, 'validate', '''def validate(task,go,args,job):
    sys.path.insert(0,str(job/'runtime/isaac/mod4'))
    from mod4v1_w35_protocol import validate_new_job
    return validate_new_job(task,go,args,job)''')
    worker = replace(worker, '    source=Path(task[\'model_path\'])',
        "    from mod4v1_fresh_dr_guard import bind_before_task_import\n    asset_identity=bind_before_task_import(task['asset_dir'])\n    os.environ['MOD4V1_ASSET_DIR']=task['asset_dir']\n    source=Path(task['model_path'])")
    worker = replace(worker, "cache.state['actual_new_PPO_updates']==68", "cache.state['actual_new_PPO_updates']==77")
    worker = replace(worker, "cache.state['typed_W35_RM70_task']['kind']=='MOD4_W35_FULL_RM70_MATERIAL_SHARED214'",
        "cache.state['typed_W35_RM70_task']['kind']=='MOD4_W35_FULL_RM70_QUALIFIED343E_CONTINUE227'")
    worker = replace(worker, 'source_prior_new_PPO_updates=68,',
        "source_prior_new_PPO_updates=77,\n        new_asset_USD_SHA=asset_identity.usd_sha256,new_asset_contract_SHA=asset_identity.contract_sha256,\n        closure_episode_m=.01,mimic_rad=.01,D6_scope='original_gas_damping_not_all_joint_friction',")
    worker = replace(worker, "entry=mod/'train_full214.py'", "entry=mod/'train_mod4v1_w35.py'")
    worker = replace(worker, "'W35_QUALIFIED343E_RM70_CONTINUE227'", "'W35_LATEST32481_MOD4V1_FULLDR_RM70'")
    worker = replace(worker, "run_name='owned_W35_RM70_qualified227_config'", "run_name='owned_W35_MOD4V1_config'")
    worker = replace(worker, "assert len(real._w35_gas400_asset_compatibility['authorized_four_scalar_changes'])==4",
        "assert real._mod4v1_asset_compatibility['new_contract_SHA']==asset_identity.contract_sha256\n                assert set(real._mod4v1_asset_compatibility['authorized_changed_bodies'])=={'chassis','left_shin','right_shin'}\n                assert real._mod4v1_fresh_dr_guard.restore_completed")
    worker = replace(worker, "                    state['PPO50_gas400_adaptation']=full['PPO50_gas400_adaptation']\n                    state['PPO50_gas400_new_updates']=completed\n                    state['PPO50_gas400_clock']=dict(policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_hz=100,gamma=.9801,lam=.9025)",
        "                    from mod4v1_w35_asset_compat import record_historical_source_metadata\n                    record_historical_source_metadata(state,full)\n                    state['mod4v1_clock']=dict(policy_hz=50,physics_dt_s=.0025,decimation=8,feedback_hz=100,gamma=.9801,lam=.9025)")
    worker = replace(worker, 'obs=vec.get_observations();physics0=int(real._integrated_contact.tick)',
        "obs=vec.get_observations();real._mod4v1_fresh_dr_guard.check_observations(obs)\n                put('MOD4V1_FRESH_DR_NOMINAL_ACTUAL.json',real._mod4v1_fresh_dr_guard.receipt())\n                physics0=int(real._integrated_contact.tick)")
    # Legacy report basenames are ABI only; active kind/asset/source identity is NEW.
    emit('worker_mod4v1_w35.py', worker, worker0)

    output['MOD4V1_ASSET_DIFF.json'] = J(asset_diff)
    schema = required_schema(protocol)
    schema['Task_identity_required_keys'] = ['kind','num_envs','source_SHA','source_bytes','source_iteration','source_Adam_step','source_LR','source_prior_new_PPO_updates','model_path','saved_source_CPU_proof_SHA','asset_USD_SHA','asset_contract_SHA','closure_episode_m','mimic_rad','original_canonical_generation','canonical_path','source_read_purpose']
    schema['pinned_metadata_not_a_Task_or_pass_receipt'] = dict(kind=NEW_KIND, source=MODEL, asset_USD_SHA=NEW_USD_SHA, asset_contract_SHA=NEW_CONTRACT_SHA, num_envs=20000, interface=[35,38,6], physics_dt=.0025, TGS=[32,4], policy_hz=50, feedback_hz=100, closure_episode_m=.01, mimic_rad=.01)
    output['REQUIRED_ROOT_INPUTS.json'] = J(schema)
    history, history_ref = raw_text(HERE/'LOCAL_ATTEMPT_HISTORY.json')
    previous_index, previous_index_ref = raw_text(HERE/'W35_MOD4V1_SOURCE_V1/MOD4V1_DERIVATION_INDEX.json')
    snapshot, snapshot_ref = raw_text(HERE/'build_w35_mod4v1_sources_v1_snapshot.py')
    require(snapshot_ref['SHA'] == json.loads(previous_index)['generator']['SHA'], 'Preserved V1 generator snapshot mismatch')
    inputs.extend([history_ref, previous_index_ref, snapshot_ref])
    output['LOCAL_ATTEMPT_HISTORY.json'] = history.encode('utf-8')
    output['SOURCE_DIFF.patch'] = ''.join(patches).encode('utf-8')
    output['README.md'] = ('''# W35 latest32481 -> mod4v1 source-only overlay

Worker: worker_mod4v1_w35.py --mode train --num-envs 20000 --run-id ACTUAL --out NEW_JOB/production
Trainer: runtime/isaac/mod4/train_mod4v1_w35.py (worker-owned; not a direct GO)

NOT LAUNCHED. No Task/GO/actual pass/budget writer is generated. ROOT must supply REQUIRED_ROOT_INPUTS.json's real owner/SDK/new-asset/lock/resource/canonical join and complete post-install manifest. Existing busy writers/cards are not adopted.

Install the unchanged base runtime referenced by INSTALL_OVERLAY_SOURCE_MAP.json first, into a NEW job only; overlay these NEW files. Carry original source banks/CAD/material/runtime dependencies without PT reread in the installer. Preserve the historical runtime/reports/SOURCE_FREEZE.json as provenance, not active v1 admission. No old job is modified.

Runtime source SHA2d0/bytes17619333/iter32481/Adam651260/LR.0002562890625000001 are pinned; source PT is metadata only here, exactly one runtime PinnedSource208 byte-open/decode. No slicing/repeating 20k DR state. Original 35/38/6, STD,17Adam, fixed SI, PPO/reward, original RM70 CAD/shared-material repair, D0-D7 RNG/queues/save/native24/finite worker remain.

New asset binding occurs after original RM_* restore and BEFORE first task import. New trainer verifies module USD_PATH/CONTRACT, explicitly assigns BOTH cfg closure .01m and mimic .01rad before constructor (old cfg thresholds become historical only), uses cfg.sim.physics, then guards the original ONE fresh-reset helper. Old code has no known PT absolute m/I overwrite bug; constructor-new nominal caches are protected, not guessed/repaired.

New reset asset admission explicitly replaces the obsolete four-scalar/517/bce identity test with pinned2c/bae and computed three-body m/COM/I DIFF. Original bank pose34/q/whole-footprint witness remains unchanged. No old authorized_four_scalar_changes pass is returned. D6 remains gas damping, not all-joint friction or hardware full coverage.

Old PPO50 gas400 fields become historical_source_400N50_and_RM70_provenance in NEW saves, with mod4v1_asset_identity/mod4v1_clock/current typed task separate. Existing report filenames retaining V3 are legacy reader ABI only, never old active asset admission. TargetSDK Native0PT/birth-check and real fullrestore/native24/training/independent replay-evaluation are still required. Parent handles post-save review and continuation, Git/trial, locks/canonical/dispatch.
''').encode('utf-8')
    # No arbitrary placeholders become actual Task/GO/pass facts.
    require(not any(Path(name).name in ('TASK.json','GO_PRODUCTION.json') for name in output), 'No generated GO')
    for name, raw in output.items():
        if name.endswith('.py'):
            ast.parse(raw.decode('utf-8'), filename=name)
    derived_rows = [dict(relative=k, bytes=len(v), SHA=hashlib.sha256(v).hexdigest()) for k,v in sorted(output.items())]
    generator_ref = dict(path=str(Path(__file__).resolve()), SHA=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    index = dict(kind='MOD4V1_W35_REVIEWABLE_SOURCE_ONLY_V2',
        source_model_metadata=MODEL, generator=generator_ref, inputs=inputs, outputs=derived_rows,
        base_install_manifest=manifest_ref, source_reads='Only declared .py/.json/.md; no PT/model decode/SDK/SSH/budget operations',
        original_reward_algorithm_CAD_RNG_queue_semantics_preserved=True,
        actual_target_SDK_or_training_executed=False, Task_GO_or_passed_receipts_generated=False)
    output['MOD4V1_DERIVATION_INDEX.json'] = J(index)
    output['INSTALL_OVERLAY_SOURCE_MAP.json'] = J(dict(kind='MOD4V1_W35_OVERLAY_SOURCE_MAP_NOT_INSTALL_RECEIPT',
        base_manifest=manifest_ref, base_source_model_remote_job=MODEL['path'].rsplit('/production/',1)[0],
        root_must_install_unchanged_base_runtime_and_original_CAD_without_old_workers=True,
        replaced_base_paths=['worker_full227.py', PREFIX+'train_full214.py', PREFIX+'config214_training.py', PREFIX+'reset208_v3.py'],
        files=[dict(relative=k, bytes=len(v), SHA=hashlib.sha256(v).hexdigest()) for k,v in sorted(output.items())],
        asset_install='ROOT complete v1 asset directory including USD relative dependencies; declared task.asset_dir before import',
        Task_GO_actual_pass_or_canonical_writer_not_created=True))
    out.mkdir(parents=True, exist_ok=False)
    for relative, raw in output.items():
        path = out / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('xb') as stream:
            stream.write(raw)
    print(json.dumps(dict(status='SOURCE_ONLY_GENERATED_NOT_EXECUTED', output=str(out),
                          files=len(output), derived_python=sum(k.endswith('.py') for k in output),
                          PT_opens=0, SDK_or_SSH_or_training=False, overwrite_permitted=False), indent=2))


if __name__ == '__main__':
    main()
