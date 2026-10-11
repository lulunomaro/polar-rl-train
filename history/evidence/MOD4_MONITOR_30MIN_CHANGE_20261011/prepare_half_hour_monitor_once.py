from pathlib import Path
import tomllib, json, time, hashlib

D=Path(__file__).resolve().parent
R=D/'reports'
R.mkdir(exist_ok=True)
H=lambda b:hashlib.sha256(b).hexdigest()

def main():
    t=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text(encoding='utf8'))
    assert t['id']=='mod4-10' and t['status']=='ACTIVE'
    assert t['rrule']=='FREQ=HOURLY;INTERVAL=1'
    assert not (R/'REQUEST_PREPARED.json').exists()
    prev=D/'MONITOR_PREVIOUS_HOURLY_PROMPT.md'
    prev.write_text(t['prompt'],encoding='utf8')
    new=D/'MONITOR_CURRENT_30MIN_PROMPT.md'
    prefix='''最新人类2026-10-11明确要求：“半个小时一次吧”。本次仅将现有mod4-10驻守频率改为每30分钟一次/ACTIVE，同一heartbeat与同一目标任务；原每1h、每2h以及旧禁止小时巡检的文字只作历史，当前以每30分钟为准。沿用健康pending DONT_NOTIFY，只实质阶段/真实修复/重大退化/完成/需人类动作通知；不新增其他驻守、不加5minSSH/ping/Rich/自动预算、不重跑任何旧once/训练/物理评测/record/tag/预算事务，不触碰人类本地WASD播放器。新频率设置及实际核验回执必须Git普通补充；本次不是新的物理实验或新预算扩展。

以下此前已经核验的入口修复、005预算与专家工作单继续有效，后续actual/fullsave/PIDreceipt/实际stage优先。旧报告/旧提示保持追溯，不据旧频率复原设置：

'''
    new.write_text(prefix+t['prompt'],encoding='utf8')
    (R/'REQUEST_PREPARED.json').write_text(json.dumps(dict(epoch=time.time(),user_instruction='半个小时一次吧',id=t['id'],kind=t['kind'],name=t['name'],target_thread_id=t['target_thread_id'],prior_status=t['status'],prior_rrule=t['rrule'],requested_rrule='FREQ=MINUTELY;INTERVAL=30',same_existing_heartbeat=True,prior_prompt_SHA=H(prev.read_bytes()),new_prompt_SHA=H(new.read_bytes()),not_yet_claimed_applied=True),ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps(dict(prepared=True,prompt=str(new))))

if __name__=='__main__':main()
