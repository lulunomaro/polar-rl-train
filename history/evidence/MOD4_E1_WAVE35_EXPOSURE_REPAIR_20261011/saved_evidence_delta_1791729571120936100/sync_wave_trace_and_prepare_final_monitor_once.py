"""Append actual full saved-trace review and prepare a corrected monitor request."""
from wave_io import *

def main():
    p=sorted(R.glob('WAVE368_FULL_TRAINING_TRACE_ACTUAL_[0-9]*.json'))[-1];trace=json.loads(p.read_bytes());assert trace['passed'] and trace['actual_controls']==2352
    n,w=io.connect_both()
    try:
        with n.open_sftp() as f:
            io.put(f,io.E+'/reports/E1_WAVE35_368_COMPLETE_TRAINING_TRACE_ACTUAL.json',p.read_bytes())
            io.put(f,io.E+'/reports/E1_WAVE35_368_DYNAMIC_FAMILY_READER_SCHEMA_REVIEW.json',(R/'WAVE368_DYNAMIC_FAMILY_READER_SCHEMA_REVIEW.json').read_bytes())
        v=run(n,r'''from pathlib import Path
import json,time,os
R=Path(CENTRAL_TOKEN)/'reports';B=Path(BUDGET_TOKEN);before_B=B.read_bytes();p=R/'MOE_PLAN_EXECUTION_CURRENT.json';before=p.read_bytes();c=json.loads(before)
s=c['terrain_subexpert_revision004']['wave35_exposure_repair_next_scope'];assert s['source_count']==368 and not s['formal_final_pending']
s.update(formal_full_trace_review_pending=False,formal_full_trace_review=str(R/'E1_WAVE35_368_COMPLETE_TRAINING_TRACE_ACTUAL.json'),actual_dynamic_family_reader_review=str(R/'E1_WAVE35_368_DYNAMIC_FAMILY_READER_SCHEMA_REVIEW.json'),full_candidate142_behavior_pending=True)
assert p.read_bytes()==before;tmp=p.with_name(p.name+'.WAVETRACE-'+str(time.time_ns()));tmp.write_text(json.dumps(c,ensure_ascii=False,indent=2));os.replace(tmp,p);assert B.read_bytes()==before_B
v=dict(epoch=time.time(),metadata_synced=True,formal_full_trace_review_pending=False,full142_behavior_pending=True,no_GPU_queue_or_budget_mutation=True)
p=R/'E1_WAVE35_368_TRACE_READER_METADATA_SYNCED.json';assert not p.exists();p.write_text(json.dumps(v,indent=2));print(json.dumps(v))
'''.replace('CENTRAL_TOKEN',repr(io.E)).replace('BUDGET_TOKEN',repr(io.B)))
        save('WAVE368_TRACE_READER_METADATA_SYNCED.json',v)
    finally:io.cleanup(n,w)
    request=json.loads((R/'WAVE_FINAL_MONITOR_UPDATE_REQUEST.json').read_bytes())
    prefix='''最新补充actual：Wave368完整5份训练NPZ/2352controls CPU仅读审查通过，actualSHA原件保留。动态actualfamily4正向2656397/负向2585623/standing1390620 controls；初始2820Wave cohort中最长有效physicalepisodeprefix20s，全部同controlprereset-before排除reset teleport。初始cohortcommand积分0–6.4463623m与净X累计-6.026154–5.687439m仅root/command代理，不是两轮接触或完整十波通行证明。全20k动态family标签相比初值有273control变化，旧读者错误把terrainassignment固定冒family每env永久固定，原AssertionError/source保留；新review_wave368_dynamic_family_full_trace_actual.py依据原retention_flat_runtime当前rootcell动态查询语义独立审，未改几何/命令/物理validator。旧review_wave368_full_training_trace_actual.py失败不要套pass或重GPU。

先读中央E1_WAVE35_368_COMPLETE_TRAINING_TRACE_ACTUAL、DYNAMIC_FAMILY_READER_SCHEMA_REVIEW、TRACE_READER_METADATA_SYNCED和本机对应最新actual；formal_full_trace_review_pending=false，142完整行为决定仍pending。今后按actualstage可复用已审schema仅读者；保存的新读者错误/trace/metadata/monitor与最新142collection继续Git ordinarysupplement。RM003官方起伏70mm是峰谷高差，不是±70mm，当前35mm派生档，出处仓库history/plans/MOD4_RM_TERRAIN_TRAINING_REVISION.md第21行。

以下ownformal final与固定合同继续有效，任何后来142complete完整决定优先：
'''
    request['prompt']=prefix+request['prompt']
    out=D/'MONITOR_CURRENT_WAVE368_FINAL_TRACE_142_PROMPT.md';assert not out.exists();out.write_text(request['prompt'],encoding='utf8')
    save('WAVE_FINAL_TRACE_MONITOR_UPDATE_REQUEST.json',request)
    print(json.dumps(dict(metadata_synced=True,request=str(R/'WAVE_FINAL_TRACE_MONITOR_UPDATE_REQUEST.json'),prompt_bytes=out.stat().st_size)))

if __name__=='__main__':
    try:main()
    except BaseException:save('WAVE_TRACE_SYNC_MONITOR_PREPARE_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_GPU_or_budget_write=True));raise
