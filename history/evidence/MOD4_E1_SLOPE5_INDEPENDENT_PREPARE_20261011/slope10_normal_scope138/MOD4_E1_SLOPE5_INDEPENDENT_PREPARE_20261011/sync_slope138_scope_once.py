"""Only new138 frozen scope annotations; never writes budget or running source."""
from slope_io import *
import traceback

def main():
    pub=json.loads((R/'SLOPE138_PUBLISHED.json').read_bytes());assert pub['actual_complete_review_pending'] and pub['canonical_bytes_preserved']
    work=R/'NEXT_E1_SLOPE10_ANALYTICNORMAL138_ACTUAL_REVIEW_WORK_ORDER.md';assert not work.exists()
    work.write_text('''# 已批准10°单角度冻结138完整审查

完整135与137的own40424b权重已观测5°和8°完整镜像上下各27/27。138为新的10°派生连续2m高.352653961m/9m镜像/.4m前接近/两轮全坡200mm后支撑/80env1500controls15s/20260928white3，仅冻结推理，无PPO、fulllearningstate迁移或预算扣账；原5°存储terraincommand状态不冒same8或same10。different10°不声称与8°初始化geometry相同。

新法向/actualqueryCPU合同已独立2800三角射线和四个接缝审查。坡段法向按[-orientation*sin10,0,cos10]，平支撑按[0,0,1]；原8°sample-normal>.99仅原scope初始化几何检查，不适用于cos10=.984807753。本次explicit新合同normal component<=1e-6与unit<=1e-6/正z，实际35point查询避免接缝，接缝flat/slope多三角法向披露。actualworldfloat32射线位置绑定height解析期望、原ground1e-6保持；两端平支撑原normalz>.99保持，productionordinary/integrity/真实contact积分/COMlink/hardware容差与控制循环ASTexact，不静默放宽物理安全线。

积极collect_slope138_actual.py仅读actualcomplete/errorfree结果；两hostprobe/result JSON逐字SHAexact及完整NPZ SHA以后review_slope138_actual.py完整全root30q/parameters/recipes/assignments/6000callbacks/actualnormal-ground/groundcontactintegralCOMlinkhardware原容差、镜像实际ground符号方向、sameepisode prereset-before进度排除resetteleport、上下行两轮全坡与200mm后支撑。位置完成和原1N接触支撑分列，stand26不要求跨坡，ordinary/声明truncationunion两reasoncoverageexact、所有失败或有效未完成prefix保持，不缩接近/延窗改原结果。未生成future文件合法pending；真实error原样保留，健康E1_SLOPE8_QUERY_REVIEW工作器不重启。

完整138决定前不自动PPO/升11或15度/qualifiedSLOPE/RM/MoE。冻结能力已足够不每档机械PPO，接受观测范围后按004其它专家实际未完成问题继续独立诊断/修复，保护E0/Wave/CURB/5°8°权重。超出原10°分支须先实际CAD路线核验，不把世界约12°与当地10.5°/1.5°混为已训10°。需要10°学习时才新isolatedroot，完整source24b旧5°actorcriticstdoptimizer/allD0D7/globalnamed/dictprivateCPUCUDA/terraincommand身份exact后显式5→10geometry/actualassignment迁移、CUDA磁盘roundtrip/savedsourceepisode+1，必要真正新scopeCPU/SDK/native/small-bigPPO弃权重各一次同canonical，原clock/DR/同scopeexactreuse，无重复45minclock。全部PASSED后首300sload-learn-save-exit/15s本机guardian/ownfullsave/PASSED/unique结清再四case完整审查。gate未训、硬件未标定、S8后续具体批准，WASD播放器不干预。

旧136failed与137修复/402404成本原false保持；138/137/135/134/133/132/131/129/旧complete不重发，任何once/main/resume/native/SDK/PPO/record/sync/budgettail已执行不可重跑。828000s六扩展各一次新增0，canonical仅原parent管理，CPU/frozen无PPO不扣；新权actualownfullsave/PASSED/旧三进程exit/两真实fcntlOS锁free/noactive/unique结清，不hotpatch/kill/dual20k/复制clear账/其它AI干预。所有保存的reader/schema/失败/源代码/完整raw索引/同步/monitor/workorder/Gitreceipt必须Git，大weights/rawNPZ/USD/ZIP仅actualpath-size-SHA，凭据不输出不Git。
''',encoding='utf8')
    names={'E1_SLOPE10_138_NORMAL_QUERY_CPU_CONTRACT_REVIEW.json':R/'SLOPE10_NORMAL_QUERY_CPU_CONTRACT_REVIEW.json',
           'E1_SLOPE10_138_FROZEN_PREPARED.json':R/'SLOPE138_PREPARED.json',
           'E1_SLOPE10_138_FROZEN_PUBLISHED.json':R/'SLOPE138_PUBLISHED.json',
           'NEXT_E1_SLOPE10_ANALYTICNORMAL138_ACTUAL_REVIEW_WORK_ORDER.md':work}
    current=sorted(R.glob('SLOPE138_COLLECTED_[0-9]*.json'))
    if current:names['E1_SLOPE10_138_CURRENT_ACTUAL_COLLECTION.json']=current[-1]
    save('SLOPE138_SCOPE_SYNC_STARTED.json',dict(epoch=time.time(),metadata_only=True))
    n,w=connect_both()
    try:
        with n.open_sftp() as f:
            assert all(name not in f.listdir(E+'/reports') for name in names)
            for name,path in names.items():put(f,E+'/reports/'+name,path.read_bytes())
        row=linux_json(n,r'''from pathlib import Path
import json,time,hashlib,os
R=Path(__CENTRAL__)/'reports';B=Path(__BUDGET__);budget=B.read_bytes();protected={n:(R/n).read_bytes() for n in ('PLAN_APPROVAL.json','EXECUTION_TRACKS.json','MOD4_MOE_MASTER_PLAN.md','MOD4_RM_TERRAIN_TRAINING_REVISION.json')}
p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();v=json.loads(before);rev=v['terrain_subexpert_revision004'];assert rev['approved'] and rev['active_next_expert']=='E1_SLOPE' and 'slope10_138_analyticnormal_scope' not in rev
assert not rev['slope8_137_actualray_scope']['actual_complete_review_pending'] and rev['slope10_next_CPU_scope']['new_frozen_job_not_published']
pub=json.loads((R/'E1_SLOPE10_138_FROZEN_PUBLISHED.json').read_bytes());assert pub['canonical_bytes_preserved'] and pub['actual_complete_review_pending'] and pub['new_budget_seconds']==0
assert json.loads(budget)['authorized_training_seconds']==828000 and json.loads(budget)['active_segment'] is None
rev['slope10_next_CPU_scope'].update(new_frozen_job_not_published=False,normal_query_CPU_contract_reviewed=True,new_frozen_scope_reference='slope10_138_analyticnormal_scope',normal_query_GPU_actual_review_pending=True)
rev.update(slope10_138_analyticnormal_scope=dict(prepared=str(R/'E1_SLOPE10_138_FROZEN_PREPARED.json'),published=str(R/'E1_SLOPE10_138_FROZEN_PUBLISHED.json'),normal_query_CPU_contract=str(R/'E1_SLOPE10_138_NORMAL_QUERY_CPU_CONTRACT_REVIEW.json'),current_actual_collection=str(R/'E1_SLOPE10_138_CURRENT_ACTUAL_COLLECTION.json') if (R/'E1_SLOPE10_138_CURRENT_ACTUAL_COLLECTION.json').exists() else None,actual_complete_review_pending=True,frozen_only=True,learning_executor_deployed=False,source5deg_terraincommand_not8deg=True,new_budget_seconds=0),next_independent_work_order=str(R/'NEXT_E1_SLOPE10_ANALYTICNORMAL138_ACTUAL_REVIEW_WORK_ORDER.md'))
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.SLOPE138-'+str(time.time_ns()));tmp.write_bytes(json.dumps(v,ensure_ascii=False,indent=2).encode());os.replace(tmp,p)
h=R/'LATEST_HANDOFF.md';hb=h.read_bytes();append='\n\nActual138 new10degree frozen scope published from complete135and137 own40424b. Explicitnew analyticnormal atactualfloat32rayinputs CPU2800triangle rays passed,normalcomponent/unit1e-6 and ground1e-6,join ambiguity disclosed,flatnormal>.99 and productionhealthhardwarecontact thresholds unchanged. Actual complete138 fullraw review pending; no10PPO or state migration,healthynewworker no restart. Read NEXT_E1_SLOPE10_ANALYTICNORMAL138_ACTUAL_REVIEW_WORK_ORDER. Prior404savedexit/budgetidle/twoOSlocksfree verified,masterapprovaltracksRMcanonical unchanged; allsavedreports/source/Git aftercare must be recorded.\n'.encode()
assert h.read_bytes()==hb;tmp=h.with_name(h.name+'.SLOPE138-'+str(time.time_ns()));tmp.write_bytes(hb+append);os.replace(tmp,h)
assert B.read_bytes()==budget and all((R/n).read_bytes()==raw for n,raw in protected.items())
print(json.dumps(dict(epoch=time.time(),metadata_synced=True,new138_scope_synced=True,master_approval_tracks_RM_canonical_bytes_preserved=True,no_GPU_PPO_or_budget_write=True,canonical_SHA=hashlib.sha256(budget).hexdigest())))
'''.replace('__CENTRAL__',repr(E)).replace('__BUDGET__',repr(B)))
        p=save('SLOPE138_SCOPE_METADATA_SYNCED.json',row)
        with n.open_sftp() as f:put(f,E+'/reports/E1_SLOPE10_138_SCOPE_METADATA_SYNCED.json',p.read_bytes())
        print(json.dumps(row))
    finally:cleanup(n,w)

if __name__=='__main__':
    try:main()
    except BaseException:save('SLOPE138_SCOPE_SYNC_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_old_sync_replay=True));raise
