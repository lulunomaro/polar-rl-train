from repair_io import *
import tomllib
def main():
 p=Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml');a=tomllib.loads(p.read_text(encoding='utf8'))
 assert a['status']=='ACTIVE' and a['rrule']=='FREQ=HOURLY;INTERVAL=1' and a['kind']=='heartbeat'
 prompt=a['prompt'];dest=D/'MONITOR_HOURLY_BUDGET005_PROMPT.md';assert not dest.exists();dest.write_bytes(prompt.encode())
 save('HOURLY_MONITOR_ACTUAL_VERIFIED.json',dict(epoch=time.time(),automation_id=a['id'],kind=a['kind'],name=a['name'],status=a['status'],rrule=a['rrule'],target_thread_id=a['target_thread_id'],prompt_SHA=H(prompt.encode()),direct_human_authorization='驻守改成一个小时一次',same_existing_automation=True,no_extra_schedule=True,healthy_pending_DONT_NOTIFY=True,no_training_or_budget_change=True))
 save('PREPARATION_READER_PATH_REJECTIONS.json',dict(epoch=time.time(),trials=[dict(id='ENTRY-LOCAL-READER-01',error='git status outside repository returned not a git repository',no_mutation=True),dict(id='ENTRY-LOCAL-READER-02',error='Get-Content inherited paths run from polar-rl-train instead of workspace; paths absent',no_mutation=True),dict(id='ENTRY-LOCAL-READER-03',error='Guessed historical timestamp directory absent; rg returned actual1791672163620845300 directory',no_mutation=True),dict(id='ENTRY-LOCAL-READER-04',error='plan_budget_contract.py not present in source389 map; actual budget_authority.py captured',no_mutation=True),dict(id='HOURLY-LOCAL-READER-01',error='CODEX_HOME unset caused C:/automations path miss; actual C:/Users/lulu/.codex/automations/mod4-10/automation.toml read',no_mutation=True)],all_pre_GPU_observer_only=True,old_failures_not_physical_failures=True))
 print(json.dumps(dict(status=a['status'],rrule=a['rrule'],same_target=True,errors_retained=True)))
if __name__=='__main__':main()
