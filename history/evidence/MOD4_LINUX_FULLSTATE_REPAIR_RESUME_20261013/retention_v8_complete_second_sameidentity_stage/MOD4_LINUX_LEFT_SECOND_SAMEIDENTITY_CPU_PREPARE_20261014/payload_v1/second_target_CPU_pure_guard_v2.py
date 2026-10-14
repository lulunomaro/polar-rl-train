"""Pure target guard functions. No oldonce/SDK import, no budget writer."""
from pathlib import Path
import hashlib,json,copy
SOURCE_SHA='2b9c3c36eaa47120e5c86753bc5b24684a9c8106d07c560d8403f26a7d372971'
BASE=Path('/mnt/mod4_linux_durable_20261013/MOD4_LINUX_FULLSTATE_REPAIR_RESUME_20261013')
FIRST=BASE/'left_exploration20k_first_formal_v1'
ROOT=BASE/'left_exploration20k_second_formal_sameidentity_v1'
SOURCE=FIRST/'left_formal3600_v1/learning_logs/2026-10-14_08-41-55_E1_WAVE50_left_exploration_formal3600/model_32635.pt'
B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json')
LOCKS=[B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')]
KEY='LINUX20K_LEFT_JOINT_EXPLORATION_INITIALIZATION'
DECISION_TRUE_FIELDS=('whole20k2b_source_actual_CPU_verified','first_formal_fulltrace_actual_reviewed','four_frozen_cases_actual_complete','physical_source_query_contact_COMhardware_all_raw_admitted','sameidentity_second3600_reasonable','no_new_policy_axis','center_near_candidates_rejected_not_source','second_and_last_block_before_full_audit')
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()
def record(p):return dict(path=str(p),bytes=Path(p).stat().st_size,sha256=sha(p))
def validate_decision(d):
    assert d.get('selected_source_SHA')==SOURCE_SHA
    for k in DECISION_TRUE_FIELDS:assert d.get(k) is True,('Missingactualscopegate',k)
    assert d['scope_learning_block_index']==2 and d['max_blocks_same_axis']==2
    assert d['first_seconds']==d['second_seconds']==3600 and d['total_planned_seconds']==7200
    evidence=d.get('evidence');assert isinstance(evidence,dict)
    for key in ('own_CPU','own_closeout','own_fulltrace','wave_complete','wave_direct','three_pairs','rejected_factors'):
        row=evidence[key];assert isinstance(row['path'],str) and row['bytes']>0
        assert isinstance(row['sha256'],str) and len(row['sha256'])==64
    assert d['qualified50'] is False and d['qualified70'] is False and d['all_skills_accepted'] is False
    assert d['no_mechanical_graduation_score'] is True
    return d
def validate_evidence_packet(d,files):
    """Actual saved evidence bytes, not a synthesized four-case success flag."""
    validate_decision(d);loaded={}
    for key,row in d['evidence'].items():
        p=Path(files[key]);assert p.stat().st_size==row['bytes'] and sha(p)==row['sha256'],key
        loaded[key]=json.loads(p.read_bytes())
    cpu=loaded['own_CPU'];assert cpu['passed'] is True and cpu['whole107finite'] is True
    assert cpu['own_final_source']['sha256']==SOURCE_SHA and cpu['updates']==189 and cpu['actual_exit_idle'] is True
    assert loaded['own_closeout']['passed'] is True
    trace=loaded['own_fulltrace'];assert trace['code']==0
    trace=json.loads(trace['stdout']);assert trace['passed'] is True and trace['own_final_SHA']==SOURCE_SHA
    assert trace['all_complete_indices_and_control_continuity_exact'] is True and trace['reset_teleport_excluded'] is True
    wave=loaded['wave_complete'];assert wave['passed'] is True and wave['source_SHA']==SOURCE_SHA
    assert wave['all_valid_unfinished_and_preordinary_prefixes_preserved'] is True and wave['no_sameepisode_reset_teleport_credit'] is True
    direct=loaded['wave_direct'];assert direct['passed'] is True and direct['new_source_SHA']==SOURCE_SHA
    three=loaded['three_pairs']['result'];assert three['all_three_pairs_actual_complete'] is True and three['actual_pending']==[]
    assert set(three['full_pairs'])=={'flat','spin','world'}
    assert set(three['actual_complete_full_cases'])=={'baseline_flat','candidate_flat','baseline_spin','candidate_spin','baseline_world','candidate_world'}
    for skill,pair in three['full_pairs'].items():
        assert pair['source_Dll_actor_root_q30_parameters_recipes_RNG_queues_exact'] is True,skill
        assert isinstance(pair['legacy_false_preserved'],dict),skill
        assert pair['legacy_false_preserved']==d['original_flags_preserved'][skill],skill
        assert set(pair['legacy_false_preserved'])=={'baseline','candidate'},skill
    rejected=loaded['rejected_factors'];assert rejected['original_best_source_sha256']==SOURCE_SHA
    assert rejected['original_best_source_retained'] is True and rejected['all_false_raw_and_cost_retained'] is True
    return dict(whole_source_CPU_and_trace_verified=True,Wave_complete_direct_and_three_complete_skill_pairs_verified=True,all_actual_evidence_bytes_SHA_exact=True,old_false_and_regressions_preserved=True)
def budget_guard(d):
    assert d['active_segment'] is None and d['authorized_training_seconds']==1188000
    x=d['budget_extensions'];assert len(x)==7 and all(v['state']=='applied' for v in x)
    assert 36000+sum(v['additional_training_seconds'] for v in x)==1188000
    assert x[-1]['extension_id']=='USER_ADD100H_20261011_7TH'
    assert x[-1]['authorized_seconds_before']==828000 and x[-1]['authorized_seconds_after']==1188000
    assert d['remaining_training_seconds']>68400
    assert abs(d['charged_training_seconds']+d['remaining_training_seconds']-1188000)<1e-5
def same(a,b):
    import torch,numpy as np
    if torch.is_tensor(a):return torch.is_tensor(b) and a.dtype==b.dtype and a.shape==b.shape and torch.equal(a.cpu(),b.cpu())
    if isinstance(a,np.ndarray):return isinstance(b,np.ndarray) and a.dtype==b.dtype and a.shape==b.shape and np.array_equal(a,b)
    if isinstance(a,dict):return isinstance(b,dict) and set(a)==set(b) and all(same(a[k],b[k]) for k in a)
    if isinstance(a,(tuple,list)):return type(a)is type(b) and len(a)==len(b) and all(same(x,y) for x,y in zip(a,b))
    return type(a)is type(b) and a==b
def walk(v,k=''):
    import torch
    if torch.is_tensor(v):yield k,v
    elif isinstance(v,dict):
        for n,x in v.items():yield from walk(x,k+'/'+str(n))
    elif isinstance(v,(tuple,list)):
        for n,x in enumerate(v):yield from walk(x,k+'/'+str(n))
def tree_sha(v):
    import torch,numpy as np
    h=hashlib.sha256()
    def add(x):
        h.update(type(x).__name__.encode());h.update(b'\0')
        if torch.is_tensor(x):h.update(str(x.dtype).encode());h.update(str(tuple(x.shape)).encode());h.update(x.detach().cpu().contiguous().numpy().tobytes())
        elif isinstance(x,np.ndarray):h.update(str(x.dtype).encode());h.update(str(x.shape).encode());h.update(x.tobytes())
        elif isinstance(x,dict):
            for k in sorted(x,key=str):add(k);add(x[k])
        elif isinstance(x,(tuple,list)):
            for y in x:add(y)
        else:h.update(repr(x).encode())
    add(v);return h.hexdigest()
def logical_fullsave(c):
    import torch
    rows=list(walk(c));floats=[v for k,v in rows if v.is_floating_point()];per=[v for k,v in rows if v.ndim and v.shape[0]==20000]
    assert len(rows)==195 and len(floats)==107 and len(per)==99
    assert all(v.device.type=='cpu' for k,v in rows) and all(bool(torch.isfinite(v).all()) for v in floats)
    assert c['independent_terrain_expert']=='E1_WAVE50'
    assert c['E1_WAVE50_initial_source_sha256']=='b026ade6c98f2f4e5d2cd4c9208cdbc9b0749a3f8df4e0b29f31f4495d3047bd'
    assert c['sensor_DR_state']['n']==20000 and c['sensor_DR_state']['profile']=='noise_bias_mild_v1'
    for k in ('feedback_delay_state','physical_action_delay_state','spring_pressure_state','gas_damping_state'):assert c[k]['n']==20000
    assert c['actor_state_dict']['mlp.0.weight'].shape==(256,35) and c['critic_state_dict']['mlp.0.weight'].shape==(256,38)
    assert c['actor_state_dict']['distribution.std_param'].shape==(6,)
    assert bool((c['actor_state_dict']['distribution.std_param']>0).all()) and len(c['optimizer_state_dict']['state'])==17
    t=c['E1_terrain_state'];assert t['num_envs']==20000 and t['seed']==20260928 and t['profile']=='mod4_G4_CAD_derived_50mm_entry_v1'
    assert t['G4_height_peak_to_trough_m']==.05 and t['partition_exact'] and t['no_ground_fallback']
    assert t['entry_reset_XY_only'] and t['entry_no_new_RNG'] and t['no_privileged_terrain_actor_input']
    entry=c['E1_WAVE50_entry_reset_identity'];assert entry['profile']==t['profile'] and entry['num_envs']==20000
    command=c['E1_retained_flat_command_state'];assert command['num_envs']==20000 and command['profile']=='E1_G3_verified_plane_signed_straight_world05_yaw12_v1'
    d=c['E1_WAVE50_episode_direction_state'];r=c['E1_WAVE50_route_lifecycle_state'];life=c['E1_WAVE50_episode_lifetime_state']
    assert d['profile']=='WAVE50_actual_legal_entry_episode_direction_v1'
    assert r['profile']=='WAVE50_legal_entry_inward4m_outward2m_lateral2m_v1' and r['Wave_inward_limit_m']==4 and r['outward_limit_m']==r['lateral_limit_m']==r['other_environment_limit_m']==2
    assert life['profile']=='WAVE50_birth_episode_timeout40s_nonWave20s_v1' and life['Wave_seconds']==40 and life['other_seconds']==20 and life['step_dt_s']==.01
    for obj in (d,r,life):
        assert obj['num_envs']==20000 and obj['no_new_rng'] is True
        assert obj['assignment_sha256']==command['assignment_sha256']
        assert obj['entry_map_sha256']==t['entry_map_sha256']==entry['entry_map_sha256']
        assert obj['entry_origin_sha256']==t['entry_origin_sha256']==entry['entry_origin_sha256']
        assert torch.equal(obj['bound_episode'],t['episode'])
    assert torch.equal(d['wave_mask'],r['wave_mask']) and torch.equal(d['wave_mask'],life['wave_mask'])
    assert c[KEY]['profile']=='left_initial_joint_margin014_std1_v1' and c[KEY]['source_envs']==20000
    assert c[KEY]['source_SHA']=='1aa77fa8e9d9813fcd3c722e249ebf3a755e1817e970f17955dd54fbcc1cff06'
    assert not any(k.startswith('LINUX20K_LEFT_JOINT_CENTER_') or k.startswith('LINUX20K_LEFT_JOINT_LOWER_') for k in c)
    return dict(floating_finite=107,perenv=99,tensors=195,saved_envs=20000,original_scope_identities_consistent=True,CPU_logical_only_not_GPU_fullrestore=True)
def negative_logical_checks(c):
    tests=[]
    edits=[('wrong_numenv',lambda x:x['sensor_DR_state'].update(n=512)),('wrong_expert',lambda x:x.update(independent_terrain_expert='E0')),('wrong_initialsource',lambda x:x.update(E1_WAVE50_initial_source_sha256='0'*64)),('wrong_terrain',lambda x:x['E1_terrain_state'].update(profile='wrong')),('wrong_entry',lambda x:x['E1_WAVE50_entry_reset_identity'].update(profile='wrong')),('wrong_direction',lambda x:x['E1_WAVE50_episode_direction_state'].update(profile='wrong')),('wrong_route',lambda x:x['E1_WAVE50_route_lifecycle_state'].update(profile='wrong')),('wrong_lifetime',lambda x:x['E1_WAVE50_episode_lifetime_state'].update(profile='wrong')),('wrong_leftprofile',lambda x:x[KEY].update(profile='wrong')),('wrong_assignment',lambda x:x['E1_WAVE50_route_lifecycle_state'].update(assignment_sha256='0'*64)),('wrong_origin',lambda x:x['E1_WAVE50_route_lifecycle_state'].update(entry_origin_sha256='0'*64))]
    for name,edit in edits:
        x=copy.deepcopy(c);edit(x)
        try:logical_fullsave(x)
        except AssertionError:tests.append(dict(case=name,strict_rejected=True))
        else:raise AssertionError('Wronglogicalsourceaccepted:'+name)
    return tests
def boundary_and_resources():
    import psutil,subprocess,shutil
    d=json.loads(B.read_bytes());budget_guard(d)
    identity=json.loads((FIRST/'PARENT_IDENTITY.json').read_bytes())
    exit=json.loads((FIRST/'left_formal3600_v1/EXIT_RECEIPT.json').read_bytes())
    assert exit['returncode']==0 and exit['canonical_cost_charged_once'] and exit['child_actually_absent']
    assert (FIRST/'GUARDIAN_EXIT.json').is_file()
    for old in [identity,exit['child']]:
        try:assert psutil.Process(old['pid']).create_time()!=old['created'],'Originalscopeprocessstillalive'
        except psutil.NoSuchProcess:pass
    completed=[x for x in d['completed_segments'] if x['kind']==exit['canonical_unique_segment']];assert len(completed)==1
    assert completed[0]['owner_parent_pid']==identity['pid'] and completed[0]['ended_epoch']>=exit['epoch']
    assert not subprocess.check_output(['nvidia-smi','--query-compute-apps=pid,process_name','--format=csv,noheader'],text=True).strip()
    available=psutil.virtual_memory().available;free=shutil.disk_usage(BASE).free
    gpu=int(subprocess.check_output(['nvidia-smi','--query-gpu=memory.free','--format=csv,noheader,nounits'],text=True).strip())*1024**2
    assert available>=55000000000 and free>=30000000000 and gpu>=22000000000
    assert SOURCE.stat().st_size==19044152 and sha(SOURCE)==SOURCE_SHA
    ready=json.loads((FIRST/'LEFT_FORMAL_SAVED_REVIEW_READY.json').read_bytes())
    assert ready['checkpoint_sha256']==SOURCE_SHA and ready['actual_saved_updates']==189 and ready['actor9_changed']
    return dict(original_scope_exit_verified=True,first_unique_segment=completed[0]['kind'],canonical_SHA=sha(B),available_RAM_bytes=available,durable_free_bytes=free,GPU_free_bytes=gpu,source=record(SOURCE))
