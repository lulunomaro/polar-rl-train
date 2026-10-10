"""New completed131 behavior/Curb CPU metadata; no GPU, signal, or budget transaction."""
from pathlib import Path
import hashlib, json, os, shlex, sys, time, traceback

D = Path(__file__).resolve().parent
W = D.parent
R = D / 'reports'
E = '/home/egde/rl_candidates/MOD4_MOE_PLAN_EXECUTION_20261007/reports'
H = lambda b: hashlib.sha256(b).hexdigest()
sys.path.insert(0, str(W / 'RM2026_TERRAIN_AUDIT_20261009'))
from reuse_authorized_session_transport import recover
sys.path.insert(0, str(W / 'MOD4_AUTONOMY_SLEEP_20261003'))
from remote_io import connect


def save(name, value):
    p = R / name
    assert not p.exists(), name
    p.write_bytes(json.dumps(value, ensure_ascii=False, indent=2).encode())
    return p


def main():
    assert not (R / 'WAVE131_COMPLETE_FINALIZE_STARTED.json').exists()
    rp = sorted(R.glob('CANDIDATE_131_REVIEW_[0-9]*.json'))[-1]
    sp = sorted(R.glob('CANDIDATE_131_SELECTED_SOURCE_REVIEW_[0-9]*.json'))[-1]
    v, s = [json.loads(p.read_bytes()) for p in (rp, sp)]
    assert v['review_complete'] and s['review_complete'] and not v['pending']
    colp = Path(v['collection'])
    col = json.loads(colp.read_bytes())
    assert len(col['cases']) == 4 and col['current_attention'] is None
    cp = v['own']['checkpoint']
    assert cp['sha256'] == '2b4f5a575d3a4d97013b331e215c503ab86e528a63a92d719a3366a684b52284'
    t = v['terrain']
    assert t['base_review']['full_raw_reviewed'] and t['base_review']['ordinary'] == 0
    missing = [row for row in t['full_route_rows']
               if row['group'] in ('forward', 'reverse') and not row['complete_episodes']]
    save('WAVE131_COMPLETE_FINALIZE_STARTED.json', dict(epoch=time.time(),
        trial_id='E1-WAVE-G3-131-COMPLETE-BEHAVIOR-01', metadata_only=True))
    decision = save('WAVE131_COMPLETE_SCOPE_DECISION.json', dict(epoch=time.time(),
        trial_id='E1-WAVE-G3-131-COMPLETE-BEHAVIOR-01', actual_review=str(rp),
        selected_source_matched_review=str(sp), collection=str(colp),
        own_independent_checkpoint=cp, summary=s['summary'],
        full_raw_SHA=t['base_review']['raw_sha256'], actual_ground_contact_hardware_fullraw_contract_reviewed=True,
        all_valid_uncompleted_prefixes=missing, all_moving_envs_full_route=not missing,
        frozen_reviewed_candidate=True,
        freeze_meaning='Exited immutable own checkpoint retained; no further optimizer updates scheduled for this checkpoint',
        candidate366_selected_as_next_learning_source=False,
        selected_next_warmstart_source_SHA='3c97c14e91a5483d03cb979cd0de0858f7fd1f2a1758e8469c88b7546b02921e',
        selected_source_complete129_behavior_reused=True,
        in_scope_complete_route_counts_declined_vs_source364=True,
        qualified_wave_expert=False,
        candidate_route_limitations_preserved=True, gate_routing_admission=False,
        inherited_flat_skills_diagnostic_not_E0_ownership=True,
        no_automatic_second_wave_block_or_900s_or50mm=True,
        next_axis='Prepare independent derived20mm CURB; new-scope physical contracts required',
        next_Curb_CPU_review=str(R / 'CURB20_CPU_COMPONENT_REVIEW.json'),
        next_Curb_work_order=str(R / 'NEXT_E1_CURB20_INDEPENDENT_WORK_ORDER.md'),
        no_MoE_route_or_permanent_anti_forgetting_or_RM70mm_graduation_claim=True,
        original_false_raw_cost_prefixes_preserved=True, new_budget_seconds=0))
    note = R / 'WAVE131_COMPLETE_SCOPE_REPORT.md'
    assert not note.exists()
    note.write_text('独立E1_WAVE source366自己的完整检查点与131四case已actualcomplete/errorfree。'
        '两主机8份probe/result JSON字节一致、完整地形NPZ SHA及初始root30q/参数/recipes/assignments、'
        '6000回调、ground-contact积分/COMlink/硬件原容差和完整signedcircle独立审查完成。'
        '35mm全十波两轮200mm后支撑实际组计数为' + json.dumps(t['groups'], ensure_ascii=False) + '。'
        '所有有效未完成前缀仍保留；普通失败0不代表全部路线通过。自己的权重保存后停止更新，'
        '保留为有明确范围与未完成限制的冻结审查候选，不能称门控已可用或整机抗遗忘已证明。'
        '对完整129 source364，前进整路线24/27→22/27、倒退27/27→25/27，'
        '因此本新保存不是已合格起伏专家，也不选择它作为下一学习来源。'
        '下一独立新scope暖启动仍选完整129已审3c97来源；不是恢复旧364入口继续混训。'
        '平地诊断与完整129 source364匹配：' + json.dumps(s['summary']['retention'], ensure_ascii=False) + '。'
        '不追加Wave盲训、不升50mm；004已批准下一独立CURB20mm CPU组件与工作单已准备，'
        '新geometry必须先实际SDK/native/fullrestore/CUDA/PPO合同准入，再首300s及完整行为审查。'
        '原E0冻结、gate未训、reward/LR/hardware/DR/clock/canonical总828000s及全部旧false/raw/cost保持。\n',
        encoding='utf8')
    files = {
        'E1_WAVE_G3_131_COMPLETE_ACTUAL_REVIEW.json': rp,
        'E1_WAVE_G3_131_SELECTED_SOURCE_MATCHED_REVIEW.json': sp,
        'E1_WAVE_G3_131_COMPLETE_COLLECTION.json': colp,
        'E1_WAVE_G3_131_COMPLETE_SCOPE_DECISION.json': decision,
        'E1_WAVE_G3_131_COMPLETE_SCOPE_REPORT.md': note,
        'E1_CURB20_CPU_COMPONENT_REVIEW.json': R / 'CURB20_CPU_COMPONENT_REVIEW.json',
        'NEXT_E1_CURB20_INDEPENDENT_WORK_ORDER.md': R / 'NEXT_E1_CURB20_INDEPENDENT_WORK_ORDER.md',
    }
    secret, _ = recover('RM_SSH_PASSWORD')
    assert secret
    os.environ['RM_SSH_PASSWORD'] = secret
    conn = connect()
    try:
        with conn.open_sftp() as f:
            for name, p in files.items():
                raw = p.read_bytes()
                with f.open(E + '/' + name, 'wbx') as out:
                    out.write(raw)
                assert f.open(E + '/' + name).read() == raw
        code = r'''from pathlib import Path
import hashlib,json,fcntl,time,os
R=Path(REPORTS);B=Path('/home/egde/rl_candidates/MOD4_native_floor_continue10h_20260930/TRAINING_BUDGET_10H.json');H=lambda b:hashlib.sha256(b).hexdigest()
protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')};budget=B.read_bytes();ledger=json.loads(budget)
assert H(protected['MOD4_MOE_MASTER_PLAN.md'])=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b' and ledger['active_segment'] is None and ledger['authorized_training_seconds']==828000
D=Path('/home/egde/rl_candidates/MOD4_S3_E1_WAVE_G3_INDEPENDENT_20261010');state=json.loads((D/'reports/E1_STATE.json').read_bytes());p=json.loads((D/'reports/e1_wave_G3_isolated_observation_PASSED.json').read_bytes());assert state['phase']=='E1_WAVE_G3_isolated_saved_review_ready' and state['child'] is None
for loc in (state['owner'],json.loads((D/'reports/E1_GUARDIAN_STARTED.json').read_bytes()),dict(pid=p['own_PID_bound_receipt']['pid'],start_ticks=80211793)):
 q=Path('/proc')/str(loc['pid'])
 if q.exists():
  a=(q/'stat').read_text().split(') ',1)[1].split();assert a[0]=='Z' or int(a[19])!=loc['start_ticks']
for lp in (B.parent/'native_floor_supervisor.lock',Path('/home/egde/rl_candidates/MOD4_scut_spin_rate_20261002/autonomy_controller.lock')):
 with lp.open('r') as q:fcntl.flock(q,fcntl.LOCK_EX|fcntl.LOCK_NB);fcntl.flock(q,fcntl.LOCK_UN)
assert len([x for x in ledger['completed_segments'] if x['pid']==p['own_PID_bound_receipt']['pid']])==1
cp=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=cp.read_bytes();v=json.loads(before);a=v['terrain_subexpert_revision004'];assert a['approved'] and 'wave131_behavior_complete' not in a
decision=json.loads((R/'E1_WAVE_G3_131_COMPLETE_SCOPE_DECISION.json').read_bytes())
a['wave131_behavior_complete']=dict(epoch=time.time(),actual_review=str(R/'E1_WAVE_G3_131_COMPLETE_ACTUAL_REVIEW.json'),selected_source_match=str(R/'E1_WAVE_G3_131_SELECTED_SOURCE_MATCHED_REVIEW.json'),decision=str(R/'E1_WAVE_G3_131_COMPLETE_SCOPE_DECISION.json'),checkpoint_SHA=decision['own_independent_checkpoint']['sha256'],own_checkpoint_frozen_reviewed_candidate=True,qualified_wave_expert=False,candidate366_selected_as_next_learning_source=False,selected_next_warmstart_source_SHA=decision['selected_next_warmstart_source_SHA'],all_moving_envs_full_route=decision['all_moving_envs_full_route'],gate_admission=False,no_more_wave_PPO_automatic=True,next_expert='E1_CURB',next_Curb_CPU=str(R/'E1_CURB20_CPU_COMPONENT_REVIEW.json'),next_work_order=str(R/'NEXT_E1_CURB20_INDEPENDENT_WORK_ORDER.md'),new_Curb_scope_not_deployed=True,new_budget_seconds=0)
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert cp.read_bytes()==before;tmp=cp.with_name(cp.name+'.Wave131-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,cp)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='E1_WAVE source366 actual131 complete and independentCURB20 CPU prepared:';assert marker.encode() not in old
msg='\n\n'+marker+' All4casescomplete/errorfree/twohost8JSONbyteexact/fullNPZ SHA and fullsignedprefix/contact/parameters audited. Read actual131 complete review/selected129source match/scope decision. Forwardfullroute24to22of27/reverse27to25of27 ordinary0; retain7uncompleted15sprefixes and originalfalse. Own2b4f exited checkpoint retained for reviewed evidence only, not qualifiedWave or nextlearningdefault; nextindependentwarmstart remains complete1293c97, neverold364entryreplay. No automatic secondWave900s or50mm; gate not admitted. E0 frozen/oldskillsdiagnostic only, actual whole-system routing not proven. Newderived20mmcurb150mmstrip contiguousupperplatform235independentCPUray+mirror+verticalwall PASSED only, not SDKnativeCUDAfullstatePPO or physicaltraversalpass. Next separateCURB output under approved004/newscope contracts and first300s before completebehavior; nooverwriteWave/E0, no blindhold or oldonce. Master/canonical/DR/hardware/reward unchanged; allnewreportsmonitorsyncGitrequired.\n'
assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.Wave131-'+str(time.time_ns()));tmp.write_bytes(old+msg.encode());os.replace(tmp,hp)
assert B.read_bytes()==budget and all((R/n).read_bytes()==b for n,b in protected.items())
print(json.dumps(dict(epoch=time.time(),complete131_decision_CurbCPU_synced=True,two_real_OS_locks_free=True,all_actual_Wave_processes_exited=True,canonical_master_approval_tracks_RM_bytes_preserved=True,new_budget_seconds=0)))
'''.replace('Path(REPORTS)', 'Path(' + repr(E) + ')')
        compile(code, '<wave131metadata>', 'exec')
        _, out, err = conn.exec_command('/usr/bin/python3 -c ' + shlex.quote(code), timeout=60)
        raw, error = out.read(), err.read()
        assert out.channel.recv_exit_status() == 0, (raw + error).decode(errors='replace')
        receipt = json.loads(raw)
        receipt['files'] = [dict(name=n, bytes=p.stat().st_size, sha256=H(p.read_bytes()))
                            for n, p in files.items()]
        receiptp = save('WAVE131_COMPLETE_METADATA_SYNCED.json', receipt)
        with conn.open_sftp() as f:
            with f.open(E + '/E1_WAVE_G3_131_COMPLETE_METADATA_SYNCED.json', 'wbx') as out:
                out.write(receiptp.read_bytes())
            assert f.open(E + '/E1_WAVE_G3_131_COMPLETE_METADATA_SYNCED.json').read() == receiptp.read_bytes()
        print(json.dumps(receipt))
    finally:
        conn.close()
        os.environ.pop('RM_SSH_PASSWORD', None)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        save('WAVE131_COMPLETE_FINALIZE_ERROR.json', dict(epoch=time.time(),
            error=traceback.format_exc(), no_replay_executed_mutations=True,
            no_GPU_signal_or_budget_transaction=True))
        raise
