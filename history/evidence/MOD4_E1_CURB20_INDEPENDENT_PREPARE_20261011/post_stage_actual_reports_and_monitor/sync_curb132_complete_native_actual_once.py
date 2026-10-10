"""New completed132 and genuine CURB native admission; annotation CAS only."""
from curb_io import *
from stage_curb_native_contract_once import NEW
import traceback

def main():
    review_path=R/'CURB132_REVIEW_1791651751.json'
    review=json.loads(review_path.read_bytes());assert review['review_complete'] and not review['pending']
    job,summary=next(iter(review['summary'].items()))
    assert summary['ordinary']==0 and summary['groups']['ascending']['complete_envs']==26 and summary['groups']['descending']['complete_envs']==27
    rows=review['review'][job]['full_route_rows']
    incomplete=[x for x in rows if x['group']!='stand' and not x['complete_episodes']]
    assert len(incomplete)==1 and incomplete[0]['env']==15 and incomplete[0]['first_ordinary_failure_control']==1500
    actual_path=sorted(R.glob('CURB_NATIVE_ACTUAL_*.json'))[-1]
    actual=json.loads(actual_path.read_bytes())
    passed=actual['receipts']['CURB_NATIVE_SCOPE_PASSED.json']
    assert actual['receipts']['CURB_NATIVE_SCOPE_STATE.json']['phase']=='CURB_new_native_contract_complete_review_ready'
    assert not actual['receipts'].get('CURB_NATIVE_SCOPE_ATTENTION.json') and actual['active_segment'] is None
    assert actual['actual_parent']['actual'] is None or actual['actual_parent']['actual']['state']=='Z'
    assert all(x['OS_lock_free'] for x in actual['two_actual_OS_locks'])
    native={}
    for label in ('CURB_SDK10','CURB_NATIVE20K'):
        v=actual['outputs'][label+'.json'];p=passed['results'][label]
        assert p['passed'] and p['no_PPO'] and v['PPO_update_count']==0
        hist=v['command_retention']['sample_histogram']
        assert all(sum(x[2:6])==0 for x in hist[:1]+hist[2:])
        native[label]=dict(own_PID=p['own_child_PID_receipt'],output=p['path'],output_SHA=p['sha256'],timed_callbacks=v['physical_callback_count'],
            total_callbacks=v['health']['actual_physics_callbacks'],ordinary=v['actual_task_failed_environments'],nonfinite=v['nonfinite'],
            closure_mm=v['max_closure_error_m']*1000,ground_error_m=v['E1_actual_ground_error_m'],reward_formula_error=v['E1_height_reward_formula_error'],
            sample_histogram=hist,projection_error=v['command_retention']['projection_error'],actual_terrain_identity=v['E1_terrain_identity'],no_PPO=True)
    decision=dict(epoch=time.time(),trial_id='E1-CURB20-132-COMPLETE-NATIVE-ADMISSION-01',review_complete=True,
        actual132_full_review=str(review_path.resolve()),full_review_SHA=H(review_path.read_bytes()),source_SHA=SHA,
        summary=summary,all_effective_incomplete_prefixes=incomplete,standing_not_required_to_cross=True,
        frozen_source_not_trained_CURB_expert=True,qualified_CURB_expert=False,all_moving_envs_full_route=False,
        gate_admission=False,actual_new_SDK_native_contracts=native,source_count=372,root=NEW,
        actual_native_parent_child_exited=True,two_original_OS_locks_free=True,canonical_bytes_preserved=True,
        complete_CURB_CPUCUDA_restore_and_assignment_migration_pending=True,full_PPO128x2_20kx4_pending=True,
        formal_learning_not_started=True,next_action='Prepare explicit G3-to-CURB complete state and command-assignment migration, ownership and own fullsave; only after genuine new CPUCUDA/PPO admission run bounded300s and paired fourcase review.',
        no_native_SDK_or_valid132_replay=True,new_budget_seconds=0)
    dp=save('CURB132_COMPLETE_NATIVE_SCOPE_DECISION.json',decision)
    save('CURB132_COMPLETE_NATIVE_SYNC_STARTED.json',dict(epoch=time.time(),once=True,metadata_only=True))
    work=R/'NEXT_CURB20_FULL_STATE_AND_PPO_WORK_ORDER_V2.md';assert not work.exists()
    work.write_text('''# 独立CURB20：实际132和新SDK/native后的完整状态准入

004已由人类批准。冻结132已完整审查：上行26/27、下行27/27，ordinary0；env15上行完整有效15s前缀尚未满足两轮200mm后支撑，原始未完成保持。站立26不要求跨坎。数据合同和SDK/native通过不代表CURB训练合格、全RM或gate部署完成。

新root MOD4_S3_E1_CURB20_INDEPENDENT_20261011/372source的唯一native parent已自然退出，两OS锁free、active-Sactive空。新SDK10实际CURB上下平台与两镜像/selectedreset和native20k实际五族已各一次通过。仅读read_curb_native_actual.py可复用；不重跑stage/dispatch/parent/native/SDK及任何旧once。实际132 complete及旧115/129/131不得重发。

下一从完整129已审source364/3c97暖启动独立CURB actor/critic/std/optimizer，不能把同编号source338/e912、source365/f5b、Wave366/2b4当来源。旧完整D0-D7/global/named/privateCPUCUDA和原terrain、command-state须先实际验证；独立新迁移接口显式G3→CURB，保存旧command assignment SHA和私有rng exact，再显式绑定新actual CURB assignment/eligibility，保持原严格load_state_retention不放宽，保存来源episode+1。实际新geometry/CUDA磁盘roundtrip、完整ownfullsave/同CURBfullresume和独立storage/output/sourcefreeze先准入。源G3不是sameCURB，terrain_state_restored_exact=false/newgeometrytrue是披露，不是PhysX exactresume。旧named集合仍严格，新增command私有rng由dict拥有。

仅真正新完整状态范围必要CPU合同和128x2/20kx4完整PPO弃权重各一次，同唯一canonical由各自原parent结清；已有本轮SDK/native和旧clock/D0D7/geometry精确SHA复用，不再GPU重播这些，不重复45minclock。全部实际PASSED后300s含load-learn-save-exit/save25/15s本地主机guardian，再完整自己的CPU/save/PID/PASSED/唯一账段核验和新CURB/flat/spin/world四case实际配对。未完整准入不启动PPO；完成后积极下一单轴或纠正，不无限hold/只留队列，不自动长训或升级坎高。

E0/Wave及其他专家不作为optimizer或save目标。新课程仅原random family替换20mm竖直坎/150mm条带连续上平台/两镜像，其他五族30/20/20/15/15背景、plane条件signedstraight/worldV.5yaw±1–2、standing.2/nonplanegentleyaw0和全部clock/DR/hardware/reward/LR1e-4adaptive/KEEPSTD1/35actor38critic6action保持。不是实际RM002坎高或台阶，不增加预算，不装pure/S7/S8/teacher，不用assignment真值喂actor/gate。gate未训、合格后冻结供hardtop1完整六维选择；冻结保护旧专家不保证活跃单专家内部不退化。

所有新源码、试错、拒绝、false/raw/cost、有效前缀、sync/monitor/最终保存与Gitreceipt必须Git补档，大NPZ/权重/ZIP只真实path-size-SHA。新GPU权仍需要自己的旧fullsave/PASSED、实际父guardian孩子退出、两OS锁free、唯一账段结清，不hotpatch/kill/双20k/clearactive/重tail/干预其他AI。
''',encoding='utf8')
    n,w=connect_both()
    try:
        authority=boundary(n)
        files={'E1_CURB20_132_COMPLETE_NATIVE_SCOPE_DECISION.json':dp,
            'E1_CURB20_NATIVE_FINAL_CURRENT_ACTUAL.json':actual_path,
            'E1_CURB20_NATIVE_TARGET_CPU_VERIFIED.json':R/'CURB_NATIVE_TARGET_CPU_VERIFIED.json',
            'E1_CURB20_NATIVE_DISPATCH_ACTUAL_RECEIPT.json':R/'CURB_NATIVE_DISPATCH_ACTUAL_RECEIPT.json',
            'NEXT_E1_CURB20_FULL_STATE_AND_PPO_WORK_ORDER_V2.md':work}
        with n.open_sftp() as f:
            assert f.open(E+'/reports/E1_CURB20_132_COMPLETE_ACTUAL_REVIEW.json').read()==review_path.read_bytes()
            for name,p in files.items():
                b=p.read_bytes()
                with f.open(E+'/reports/'+name,'wbx') as out:out.write(b)
                assert f.open(E+'/reports/'+name).read()==b
        receipt=linux_json(n,r'''from pathlib import Path
import json,hashlib,time,os
R=Path(CENTRAL)/'reports';B=Path(BUDGET);budget=B.read_bytes()
protected={x:(R/x).read_bytes() for x in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
assert hashlib.sha256(protected['MOD4_MOE_MASTER_PLAN.md']).hexdigest()=='812a4bedd04834a98a7c9391609d0056b47c47398e0ecdda9c61e61c6466d05b'
d=json.loads((R/'E1_CURB20_132_COMPLETE_NATIVE_SCOPE_DECISION.json').read_bytes())
assert d['review_complete'] and not d['qualified_CURB_expert'] and d['formal_learning_not_started']
cp=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=cp.read_bytes();v=json.loads(before);a=v['terrain_subexpert_revision004']
assert a['approved'] and a['curb132_frozen_scope']['actual_published'] and 'curb132_complete_native_admission' not in a
a['active_next_expert']='E1_CURB'
a['curb132_complete_native_admission']=dict(epoch=time.time(),actual_review=str(R/'E1_CURB20_132_COMPLETE_ACTUAL_REVIEW.json'),decision=str(R/'E1_CURB20_132_COMPLETE_NATIVE_SCOPE_DECISION.json'),native_current_actual=str(R/'E1_CURB20_NATIVE_FINAL_CURRENT_ACTUAL.json'),new_root=d['root'],source_count=d['source_count'],ascending_full_route=26,descending_full_route=27,each_group_envs=27,ordinary=0,qualified_CURB_expert=False,SDK_native_complete=True,new_complete_CPUCUDA_restore_and_PPO_pending=True,formal_learning_not_started=True,no_more_wave_PPO=True,next_work_order=str(R/'NEXT_E1_CURB20_FULL_STATE_AND_PPO_WORK_ORDER_V2.md'),new_budget_seconds=0)
a['curb132_frozen_scope']['actual_complete_pending']=False
a['curb132_frozen_scope']['complete_review_ref']=str(R/'E1_CURB20_132_COMPLETE_ACTUAL_REVIEW.json')
raw=json.dumps(v,ensure_ascii=False,indent=2).encode();assert cp.read_bytes()==before;tmp=cp.with_name(cp.name+'.CURBComplete-'+str(time.time_ns()));tmp.write_bytes(raw);os.replace(tmp,cp)
hp=R/'LATEST_HANDOFF.md';old=hp.read_bytes();marker='IndependentCURB132 complete and new372 native admitted:';assert marker.encode() not in old
msg='\n\n'+marker+' actualfullraw/twohostbyteexact/ascending26of27 descending27of27 ordinary0;env15 valid15s incompleteprefix retained,standnotcross. Genuine newSDK10CURBmirrors/selectedreset and20knative completeonce/noPPO;actualnewparentchildexited/twoOSlocksfree/canonical unchanged. NoCURBqualified/gateadmission. Next V2 fullstate+explicitoldassignment/privateRNG-to-newCURB migration/CPUCUDAepisode1/ownership/fullsave/128x2-20kx4discardonce thenbounded300s andfourcase. Reuseactualnative/SDK/oldclockD0D7 exactSHA; no replay132/131/129 or oldonce. Selectedsource3643c97, E0/Wave untouched; allsavedreportsGitsupplement required.\n'
assert hp.read_bytes()==old;tmp=hp.with_name(hp.name+'.CURBComplete-'+str(time.time_ns()));tmp.write_bytes(old+msg.encode());os.replace(tmp,hp)
assert B.read_bytes()==budget and all((R/x).read_bytes()==b for x,b in protected.items())
print(json.dumps(dict(epoch=time.time(),curb132_complete_native_metadata_synced=True,new_scope_SDK_native_admitted=True,formal_PPO_not_started=True,protected_master_approval_tracks_RM_canonical_bytes_preserved=True)))
'''.replace('CENTRAL',repr(E)).replace('BUDGET',repr(B)))
        receipt['old_actual_authority']=authority;receipt['files']=[dict(name=name,bytes=p.stat().st_size,sha256=H(p.read_bytes())) for name,p in files.items()]
        p=save('CURB132_COMPLETE_NATIVE_METADATA_SYNCED.json',receipt)
        with n.open_sftp() as f:
            with f.open(E+'/reports/E1_CURB20_132_COMPLETE_NATIVE_METADATA_SYNCED.json','wbx') as out:out.write(p.read_bytes())
            assert f.open(E+'/reports/E1_CURB20_132_COMPLETE_NATIVE_METADATA_SYNCED.json').read()==p.read_bytes()
        print(json.dumps(dict(synced=True,SDK_native_admitted=True,formal_learning_not_started=True)))
    finally:cleanup(n,w)
if __name__=='__main__':
    try:main()
    except Exception:
        save('CURB132_COMPLETE_NATIVE_SYNC_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),no_replay_executed_mutations=True));raise
