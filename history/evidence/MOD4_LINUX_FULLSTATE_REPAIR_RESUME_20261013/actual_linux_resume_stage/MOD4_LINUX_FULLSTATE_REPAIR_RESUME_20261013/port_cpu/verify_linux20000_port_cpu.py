"""Fresh actual latest-source CPU port/schema/negative/disk proof, no CUDA."""
from pathlib import Path
import copy
import hashlib
import json
import os
import sys
import time

import numpy as np
import torch
import temporary_state_binding as b


def run(source_path, output_dir):
    source_path = Path(source_path)
    output_dir = Path(output_dir)
    assert not output_dir.exists()
    assert b.H(source_path) == b.SOURCE_SHA
    assert not torch.cuda.is_initialized()
    rng_before = torch.get_rng_state().clone()
    source = torch.load(source_path, map_location='cpu', weights_only=False)
    b.validate_source512(source, b.SOURCE_SHA)
    candidate, proof = b.expand_learned_source(source, b.SOURCE_SHA)
    mapping = torch.tensor(candidate[b.KEY]['source512_slot_ids'], dtype=torch.long)
    fields, _ = b.ex.schema()
    by_path = {tuple(r['tokens']) for r in fields}
    copied = []
    untouched = []
    no_storage_alias = []

    def compare(a, c, path=()):
        if torch.is_tensor(a):
            if path in by_path:
                assert b.same(c, a.index_select(0, mapping)), path
                copied.append(list(path))
            else:
                assert b.same(a, c), path
                untouched.append(list(path))
            if a.numel() and c.numel():
                assert a.data_ptr() != c.data_ptr(), path
                no_storage_alias.append(list(path))
        elif isinstance(a, dict):
            for key, value in a.items():
                compare(value, c[key], path + (key,))
        elif isinstance(a, (list, tuple)):
            assert type(a) is type(c) and len(a) == len(c), path
            for i, value in enumerate(a):
                compare(value, c[i], path + (i,))

    compare(source, candidate)
    assert len(copied) == 99
    assert b.floating_count(source) == b.floating_count(candidate) == 107
    rejected = []

    def rejects(name, tree, function=None):
        try:
            (function or (lambda x: b.validate(x, b.SOURCE_SHA)))(tree)
        except (AssertionError, KeyError, ValueError, IndexError) as error:
            rejected.append(dict(case=name, type=type(error).__name__, message=str(error)))
        else:
            raise AssertionError('Accepted invalid port: ' + name)

    rejects('wrong_initial_source_SHA', source, lambda x: b.expand_learned_source(x, '0' * 64))
    bad = copy.deepcopy(candidate); bad[b.KEY]['profile'] = 'wrong'; rejects('wrong_Linux_branch_profile', bad)
    bad = copy.deepcopy(candidate); bad[b.KEY]['num_envs'] = 512; rejects('wrong_target_N', bad)
    bad = copy.deepcopy(candidate); bad[b.KEY]['source_checkpoint_SHA'] = '0' * 64; rejects('wrong_learned_source_lineage', bad)
    bad = copy.deepcopy(candidate); bad[b.KEY]['child_slot_ids'][1] = 0; rejects('duplicate_child_slot', bad)
    bad = copy.deepcopy(candidate); bad[b.KEY]['source512_slot_ids'][0] = 1; rejects('wrong_family_cyclic_mapping', bad)
    bad = copy.deepcopy(candidate); bad[b.KEY]['source_birth_family'][0] = 4; rejects('wrong_birth_family', bad)
    bad = copy.deepcopy(candidate); bad[b.KEY]['static1600_assignment_sha256'] = '0' * 64; rejects('wrong_global_assignment', bad)
    bad = copy.deepcopy(candidate); bad[b.KEY]['source512_spawn_xy'][0][0] += 9; rejects('wrong_saved_source_origins', bad)
    bad = copy.deepcopy(candidate); bad['E1_terrain_state']['entry_map_sha256'] = '0' * 64; rejects('wrong_map_hash', bad)
    bad = copy.deepcopy(candidate); bad['E1_terrain_state']['entry_origin_sha256'] = '0' * 64; rejects('wrong_origin_hash', bad)
    bad = copy.deepcopy(candidate); bad['E1_terrain_state']['entry_input_sha256'] = '0' * 64; rejects('wrong_input_hash', bad)
    bad = copy.deepcopy(candidate); bad['E1_WAVE50_route_lifecycle_state']['bound_episode'][0] += 1; rejects('wrong_episode_binding', bad)
    bad = copy.deepcopy(candidate); bad['sensor_DR_state']['n'] = 512; rejects('wrong_scalar_count', bad)
    bad = copy.deepcopy(candidate); bad['WINDOWS4090_TEMPORARY_BRANCH']['num_envs'] = 20000; rejects('historical_Windows_scope_relabel', bad)
    bad = copy.deepcopy(candidate); bad['E1_retained_flat_command_state']['BODY_command'] = bad['E1_retained_flat_command_state']['BODY_command'][:512].clone(); rejects('wrong_fixed99_shape', bad)
    actual_states = {key: copy.deepcopy(candidate[key]) for key in b.STATES}
    code_plan = {key: {} for key in b.STATES}
    for key, field in [('E1_terrain_state', 'entry_runtime_sha256'),
                       ('E1_WAVE50_entry_reset_identity', 'entry_runtime_sha256'),
                       ('E1_terrain_state', 'entry_full_pose_sha256'),
                       ('E1_WAVE50_entry_reset_identity', 'entry_full_pose_sha256'),
                       ('E1_WAVE50_route_lifecycle_state', 'parent_boundary_source_sha256')]:
        old = candidate[key][field]
        new = hashlib.sha256(('CPU_synthetic_Linux_code_field_' + field).encode()).hexdigest()
        actual_states[key][field] = new
        code_plan[key][field] = dict(old=old, new=new, explicit_frozen_code_binding_only=True)
    bound, changes = b.bind_runtime_metadata_once(candidate, actual_states, code_plan)
    assert len(changes) == 5 and b.require_same_runtime_metadata(bound, actual_states)
    rejects('second_Linux_ABI_binding_forbidden', bound,
            lambda x: b.bind_runtime_metadata_once(x, actual_states, code_plan))
    bad_states = copy.deepcopy(actual_states); bad_states['E1_terrain_state']['command_vx_range'] = [-.31, .31]
    rejects('sameLinux_physical_metadata_change_forbidden', bound,
            lambda x: b.require_same_runtime_metadata(x, bad_states))
    bad_states = copy.deepcopy(actual_states); bad_states['E1_terrain_state']['entry_runtime_sha256'] = '0' * 64
    rejects('sameLinux_code_rebind_forbidden', bound,
            lambda x: b.require_same_runtime_metadata(x, bad_states))
    bad_states = {key: copy.deepcopy(candidate[key]) for key in b.STATES}
    bad_states['E1_terrain_state']['spawn_xy'][0, 0] += .01
    rejects('actual_birth_XY_mismatch', candidate,
            lambda x: b.bind_runtime_metadata_once(x, bad_states, {k: {} for k in b.STATES}))
    bad_states = {key: copy.deepcopy(candidate[key]) for key in b.STATES}
    bad_states['E1_terrain_state']['reset_expected_q'][0, 0] += .001
    rejects('actual_full_pose_q_mismatch', candidate,
            lambda x: b.bind_runtime_metadata_once(x, bad_states, {k: {} for k in b.STATES}))
    bad_states = {key: copy.deepcopy(candidate[key]) for key in b.STATES}
    key = 'E1_WAVE50_episode_lifetime_state'; field = 'parent_timeout_source_sha256'
    if field in bad_states[key]:
        old = bad_states[key][field]; bad_states[key][field] = 'a' * 64
        timeout_plan = {k: {} for k in b.STATES}; timeout_plan[key][field] = dict(old=old, new='a' * 64, explicit_frozen_code_binding_only=True)
        rejects('timeout_code_rebind_without_math_proof', candidate,
                lambda x: b.bind_runtime_metadata_once(x, bad_states, timeout_plan))
    output_dir.mkdir(parents=True)
    p = output_dir / 'LINUX20000_FULLSTATE_CPU_CANDIDATE.pt'
    torch.save(candidate, p)
    with p.open('r+b') as f:
        f.flush(); os.fsync(f.fileno())
    reread = torch.load(p, map_location='cpu', weights_only=False)
    assert b.same(candidate, reread)
    b.validate(reread, b.H(p))
    assert torch.equal(rng_before, torch.get_rng_state()) and not torch.cuda.is_initialized()
    assert b.H(source_path) == b.SOURCE_SHA
    report = dict(epoch=time.time(), passed_CPU_source_family_dimension_storage_and_disk_only=True,
                  source=dict(path=str(source_path.resolve()), bytes=source_path.stat().st_size, sha256=b.SOURCE_SHA,
                              iteration=source['iter'], actual_learned28_update_source=True),
                  candidate=dict(path=str(p.resolve()), bytes=p.stat().st_size, sha256=b.H(p)),
                  projected99_paths_exact=copied, unprojected_tensor_paths_exact=untouched,
                  no_storage_alias_paths=no_storage_alias,
                  thirteen_scalar_count_paths=proof['scalar_count_paths'],
                  family_counts=b.FAMILY_COUNTS, source_birth_family_review=proof['source_birth_family_review'],
                  code_binding_synthetic_CPU_fixture_only=changes, strict_rejected_cases=rejected,
                  CPU_no_new_RNG=True, no_CUDA=True, source_unmodified=True,
                  floating107=True, no_initializer_repeated=True,
                  historical_Windows512_metadata_preserved=True,
                  actual_Linux_backend_SHA_binding_and_full_GPU_restore_pending=True,
                  qualification_claimed=False,
                  source_files=[dict(path=str(q.resolve()), bytes=q.stat().st_size, sha256=b.H(q))
                                for q in Path(b.__file__).parent.iterdir() if q.is_file()])
    q = output_dir / 'LINUX20000_PORT_CPU_ACTUAL_REVIEW.json'
    with q.open('xb') as f:
        f.write(json.dumps(report, indent=2).encode()); f.flush(); os.fsync(f.fileno())
    print(json.dumps(dict(passed=True, report=str(q.resolve()), reportSHA=b.H(q), candidateSHA=b.H(p),
                          source_SHA=b.SOURCE_SHA, source_families=b.SOURCE_FAMILY_COUNTS,
                          target_families=b.FAMILY_COUNTS, paths99=len(copied), floating107=True,
                          negative_cases=len(rejected), GPU_pass_claimed=False)))
    return report


if __name__ == '__main__':
    run(sys.argv[1], sys.argv[2])
