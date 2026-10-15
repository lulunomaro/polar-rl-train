"""Consume every durable first-gate buffer and physical prefix on CPU only.

This is an independent saved-data review. Probability reconstruction samples
1024 deterministic rows in every update; it is not a new physical replay.
"""
from pathlib import Path
import hashlib, json, math, os, re, time
os.environ['CUDA_VISIBLE_DEVICES'] = ''
import numpy as np
import torch
from torch.nn import functional as F

ROOT = '/mnt/mod4_linux_durable_20261013/MOD4_S4_E0_WAVE35_FIRST_SUPPORTED_GATE45M_V1_20261015'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def main():
    import fcntl, psutil
    r = Path(ROOT); a = r / 'learning_logs'
    final = json.loads((a / 'S4_FORMAL_FINAL_ACTUAL.json').read_bytes())
    assert final['passed'] is True
    assert json.loads((r / 'PARENT_EXIT_ACTUAL.json').read_bytes())['passed'] is True
    assert (r / 'GUARDIAN_EXIT_ACTUAL.json').is_file()
    assert not (r / 'PARENT_ORIGINAL_ERROR.json').exists()
    assert not (a / 'S4_FORMAL_ORIGINAL_ERROR.json').exists()
    for who in ('parent', 'child'):
        row = json.loads((r / 'DISPATCH_ACTUAL.json').read_bytes())[who]
        try: assert psutil.Process(row['pid']).create_time() != row['created']
        except psutil.NoSuchProcess: pass
    b = Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
    assert json.loads(b.read_bytes())['active_segment'] is None
    for lock in (b.parent / 'native_floor_supervisor.lock',
                 Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
        with lock.open('r+b') as f:
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB); fcntl.flock(f, fcntl.LOCK_UN)
    torch.set_num_threads(4)
    cpu_rng = torch.get_rng_state().clone()
    p = Path(final['own_checkpoint']); assert sha(p) == final['own_checkpoint_SHA']
    ck = torch.load(p, map_location='cpu', weights_only=False)
    manifest = json.loads((r / 'S4_FIRST_FORMAL_ACTUAL_MANIFEST.json').read_bytes())
    source = torch.load(manifest['source_path'], map_location='cpu', weights_only=False)
    health = json.loads((a / 'CLOCK_TRAINING_HEALTH.json').read_bytes())
    controls = final['complete_controls']; updates = final['updates']; n = 20000
    assert controls == updates * 24 == health['control_steps']
    assert final['callbacks'] == health['actual_physics_callbacks'] == controls * 4
    assert health['integrity_task_reset_events'] == health['unknown_task_reset_events'] == 0
    assert health['nonfinite_observed'] is False and health['stop_reason'] is None
    index = json.loads((a / 'S4_GATE_FULL_ROLLOUT_INDEX_ACTUAL.json').read_bytes())
    assert index['source_SHA'] == final['source_SHA'] and len(index['rows']) == updates
    assert sha(a / 'S4_GATE_FULL_ROLLOUT_INDEX_ACTUAL.json') == ck['S4_full_rollout_audit_index_SHA']
    state = ck['actor_state_dict']
    assert all(torch.equal(v, source['actor_state_dict'][k]) for k, v in state.items() if not k.startswith('gate.'))
    std = state['frozen_std']
    def mean(x, expert):
        for i in (1, 3, 5, 7):
            x = F.linear(x, state[f'experts.{expert}.frozen_{i}'], state[f'experts.{expert}.frozen_{i+1}'])
            if i != 7: x = F.elu(x)
        return x
    previous = np.zeros((n, 6), np.float32)
    last_z = np.full(n, -1, np.int64)
    episode_ends = np.zeros(n, np.int64)
    switches = eligible_total = rollout_bytes = sample_count = 0
    selected_counts = np.zeros(2, np.int64)
    sample_logp_max = 0.; clip_elements = action_elements = 0
    rollouts = []
    expected_keys = {'policy35','critic38','sampled_z','supported_training_metadata','raw_actions',
        'old_gate_logits','old_joint_logp','rewards','dones','values','returns','bootstrap_supported'}
    for i, row in enumerate(index['rows']):
        q = Path(row['path'])
        assert row['index'] == i and row['optimizer_update_complete'] is True
        assert q.stat().st_size == row['bytes'] and sha(q) == row['sha256']
        with np.load(q, allow_pickle=False) as z:
            assert set(z.files) == expected_keys
            data = {k:z[k] for k in z.files}
        assert all(np.isfinite(v).all() for v in data.values())
        x = data['policy35']; raw = data['raw_actions']; done = data['dones'][:,:,0].astype(bool)
        choice = data['sampled_z'][:,:,0]
        labels = data['supported_training_metadata'][:,:,0]; bootstrap = data['bootstrap_supported']
        assert x.shape == (24,n,35) and data['critic38'].shape == (24,n,38) and raw.shape == (24,n,6)
        assert data['old_gate_logits'].shape == (24,n,2) and data['old_joint_logp'].shape == (24,n,1)
        assert np.isin(choice,[0,1]).all() and np.isin(labels,[0,1]).all() and bootstrap.shape == (n,)
        assert np.isin(bootstrap,[0,1]).all() and np.isin(data['dones'],[0,1]).all()
        normal = np.zeros_like(x[:,:,28:35]); normal[:,:,0] = 1
        assert np.array_equal(x[:,:,28:35],normal)
        keep = labels.astype(bool).all(0) & bootstrap.astype(bool)
        selection = row['selection']; eligible = int(keep.sum()) * 24
        assert selection['complete_supported_envs'] == int(keep.sum())
        assert selection['eligible_samples'] == eligible and selection['actual_samples_per_epoch'] == eligible
        assert selection['selected_whole_rollout_and_bootstrap'] is True and selection['domain_is_actor_input'] is False
        for t in range(24):
            assert np.array_equal(x[t,:,22:28],previous), (i,t,'actual previous action')
            selected_counts += np.bincount(choice[t].astype(int),minlength=2)
            switches += int(((last_z >= 0) & (last_z != choice[t])).sum())
            last_z = choice[t].astype(np.int64).copy(); last_z[done[t]] = -1
            previous = np.clip(raw[t],-6,6); previous[done[t]] = 0
            episode_ends += done[t]
        # Same historical x and recorded z, frozen means, stored old gate logits.
        # CPU-vs-GPU float rounding is reported separately from physical tolerances.
        ix = np.linspace(0,24*n-1,1024,dtype=np.int64)
        xx = torch.from_numpy(x.reshape(-1,35)[ix].copy())
        zz = torch.from_numpy(choice.reshape(-1)[ix].astype(np.int64))
        rr = torch.from_numpy(raw.reshape(-1,6)[ix].copy())
        logits = torch.from_numpy(data['old_gate_logits'].reshape(-1,2)[ix].copy())
        with torch.inference_mode():
            means = torch.stack([mean(xx,j) for j in range(2)],1)[torch.arange(len(ix)),zz]
            scales = std[zz]
            expected = (-.5*((rr-means)/scales).square()-scales.log()-.5*math.log(2*math.pi)).sum(-1)
            expected += logits.log_softmax(-1).gather(-1,zz[:,None])[:,0]
        actual = data['old_joint_logp'].reshape(-1)[ix]
        difference = float(np.max(abs(expected.numpy()-actual)))
        assert np.allclose(expected.numpy(),actual,rtol=2e-4,atol=2e-3), (i,difference)
        sample_logp_max = max(sample_logp_max,difference); sample_count += len(ix)
        eligible_total += eligible; rollout_bytes += row['bytes']
        clip_elements += int((abs(raw)>6).sum()); action_elements += raw.size
        rollouts.append(dict(index=i,path=str(q),bytes=row['bytes'],sha256=row['sha256'],eligible_samples=eligible))
        if (i+1)%25 == 0: print('CPU_RAW_PROGRESS '+str(i+1),flush=True)
    shared = ck['S4_shared_control_state']
    assert np.array_equal(previous,shared['previous'].numpy())
    assert np.array_equal(last_z,shared['last_selected'].numpy())
    assert np.array_equal(episode_ends,ck['E1_terrain_state']['episode'].numpy()-source['E1_terrain_state']['episode'].numpy()-1)
    # Physical prefixes retain every background and every valid/failed frame.
    meta = json.loads((a / 'RETENTION_COMMAND_ACTUAL.json').read_bytes())
    assert meta['actual_controls'] == controls and meta['pre_reset_roots_no_teleport'] is True
    columns = ['before_x','before_y','before_z','pre_reset_x','pre_reset_y','pre_reset_z','heading_before',
        'BODY_vx','BODY_vy','signed_yaw','family','eligible','linear','moving','terminated','truncated']
    total = ordinary = truncated = overlap = dynamic = longest = 0
    duration = np.zeros(n,np.int64); counts = np.zeros(n,np.int64); first_family = last = last_done = None
    wave_hist = np.zeros(3,np.int64); prefix_files = []
    for name in meta['trace_files']:
        q = a / name; m = re.fullmatch(r'retention_prefix_(\d+)_(\d+)\.npz',name)
        assert m and int(m[1]) == total and q.parent == a
        with np.load(q,allow_pickle=False) as z:
            x = z['rows']; assert z['columns'].tolist() == columns
        assert x.shape[1:] == (n,16) and len(x) == int(m[2])-int(m[1]) and np.isfinite(x).all()
        done = (x[:,:,14]!=0)|(x[:,:,15]!=0)
        assert all(np.isin(x[:,:,j],[0,1]).all() for j in (11,12,13,14,15))
        assert np.isin(x[:,:,10],np.arange(-1,5)).all()
        if first_family is None: first_family = x[0,:,10].copy()
        if last is not None: assert np.array_equal(x[0,~last_done,:3],last[~last_done,3:6])
        assert np.array_equal(x[1:,:,:3][~done[:-1]],x[:-1,:,3:6][~done[:-1]])
        wave = x[:,:,10] == 4; vx = x[:,:,7][wave]
        assert np.max(abs(x[:,:,8:10][wave])) <= 1e-6 and np.max(abs(vx)) <= .300001
        wave_hist += [(vx<0).sum(),(vx>0).sum(),(vx==0).sum()]
        for row in x:
            failing = row[:,14]!=0; ending = failing|(row[:,15]!=0)
            duration[~failing] += 1; longest = max(longest,int(duration.max())); duration[ending] = 0
        counts += done.sum(0)
        ordinary += int((x[:,:,14]!=0).sum()); truncated += int((x[:,:,15]!=0).sum())
        overlap += int(((x[:,:,14]!=0)&(x[:,:,15]!=0)).sum())
        dynamic += int((x[:,:,10]!=first_family[None,:]).sum())
        last = x[-1].copy(); last_done = done[-1].copy(); total += len(x)
        prefix_files.append(dict(path=str(q),bytes=q.stat().st_size,sha256=sha(q),controls=len(x)))
    assert total == controls and np.array_equal(counts,episode_ends)
    assert ordinary == health['actual_task_reset_events'] and truncated == health['actual_truncation_reset_events']
    assert longest*.01 <= 40.001 and (wave_hist>0).all()
    assert not torch.cuda.is_initialized() and torch.equal(cpu_rng,torch.get_rng_state())
    result = dict(epoch=time.time(),passed=True,own_final_SHA=final['own_checkpoint_SHA'],updates=updates,
        controls=controls,physical_vector_envsteps=controls*n,callbacks=controls*4,
        full_gate_rollouts=rollouts,total_gate_rollout_bytes=rollout_bytes,
        all_buffers_finite_source_SHA_creation_SHA_and_complete_update_verified=True,
        all_supported24_bootstrap_selections_recomputed=True,qualified_gradient_samples=eligible_total,
        physical_steps_not_all_qualified_gradient_samples=True,
        selected_E0_W35_envcontrols=selected_counts.tolist(),sampled_expert_switches=switches,
        raw_action_clip_element_fraction=clip_elements/action_elements,
        all_previous_actual_clipped_action_selectedreset_continuity_exact=True,
        all_episode_counts_source_plus_one_reset_union_exact=True,
        probability_reconstruction_samples=sample_count,CPU_GPU_sample_joint_logp_max_abs_error=sample_logp_max,
        probability_sampling_is_not_full_physical_replay_or_allrow_probability_test=True,
        CPU_GPU_numerical_check=dict(rtol=2e-4,atol=2e-3,original_physical_tolerances_unchanged=True),
        full_physical_prefixes=prefix_files,total_prefix_bytes=sum(v['bytes'] for v in prefix_files),
        ordinary_events=ordinary,unique_truncation_events=truncated,ordinary_truncation_overlap=overlap,
        currentrootfamily_vs_initial_assignment_changed_control_count=dynamic,
        currentroot_Wave_negative_positive_standing_control_count=wave_hist.tolist(),
        beforephysics_commands_not_forced_equal_afterhistory_phase=True,
        longest_valid_recorded_physical_prefix_seconds=longest*.01,
        root_command_proxy_not_contact_or_fullroute_or_causal_certificate=True,
        frozen_rule_vs_new_learned_gate_physical_evaluation_still_required=True,
        no_GPU_RNG_budget_write_signal_or_learning=True,qualification_claimed=False)
    print('S4_FINAL_CPU_RESULT '+json.dumps(result),flush=True)


if __name__ == '__main__': main()
