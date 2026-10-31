"""Ordinary append of human-requested primary completion evidence, no new tag."""
from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;R=N/'reports';G=N.parent.parent/'polar-rl-train'
D=G/'versions/20261031_mod4-literal-fudan-jump-e0-hour-and-194-remainder-parallel197/ordinary199_primary_status_20261031'
def read(p):return json.loads(Path(p).read_bytes())
def git(*a):return subprocess.run(['git','-C',str(G),*a],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return {x.split()[1]:x.split()[0] for x in s.splitlines() if x.strip()}
assert not git('status','--porcelain') and not D.exists()
summary=read(R/'CURRENT_ACTUAL199_PRIMARY197_COMPLETE_SAVED_STATUS_NO_JUMP_SKILL_CLAIM.json')
assert summary['primary_exit_code']==0 and summary['original7200_learning_window_deadline_met']
assert read(R/'ROOT199_PRIMARY_STATUS_ALL_SSH_CLOSED_SESSION_RESTORED_FREE.json')['global_serial_client_lease']=='FREE'
req=read(R/'AUTOMATION199_PRIMARY_COMPLETE_SAVED_STATUS_UPDATE_REQUEST.json')
a=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert a['prompt']==req['prompt'].rstrip('\n') and a['status']=='ACTIVE' and a['rrule']==req['rrule'] and a['target_thread_id']==req['targetThreadId']
assert not read(R/'AUTOMATION199_PRIMARY_COMPLETE_SAVED_STATUS_UPDATE_RECEIPT.json').get('isError')
old=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert len([k for k in old if not k.endswith('^{}')])==1501 and all(remote.get(k)==v for k,v in old.items())
for name,v in (
    ('AUTOMATION199_PERSISTED_EXACT_SAME_HOURLY_THREAD_VERIFIED.json',dict(epoch=time.time(),passed=True,same_automation_kind_name_schedule_target=True)),
    ('ARCHIVE199_ORDINARY197_ONCE_CONSUMED.json',dict(epoch=time.time(),ordinary_append=True,no_record_or_new_tag=True,protected1501_tags_objects_peels=True,model_raw_GPU_for_Git_reads=0))):
    with (R/name).open('x',encoding='utf8') as f:json.dump(v,f,indent=2)
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
sources=sorted(p for p in R.glob('*199*') if p.is_file())
sources += [N/'human199_main197_one_saved_status_once.py',N/'prepare199_primary_status_summary_and_automation_once.py',Path(__file__).resolve()]
D.mkdir();rows=[];selected=[]
for source in sources:
    raw=source.read_bytes();assert redact(raw.decode('utf8'))[0]==raw.decode('utf8')
    dest=D/source.relative_to(N);dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
    rows.append(dict(path=str(source),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),Git_path=dest.relative_to(G).as_posix(),capture='full_UTF8_byte_exact'))
    selected.append(dest.relative_to(G).as_posix())
index=D/'CAPTURE_INDEX.json'
index.write_text(json.dumps(dict(epoch=time.time(),phase='ordinary197-human-primary-saved-status199',files=rows,
    human='非分支训练的如何？跳了吗？',one_new_readonly_primary_status=True,source72_small_JSON_reads=3,source210_small_JSON_reads=4,
    primary_full_window_complete_saved_and_node_waited=True,original_combined_normal900_still_UNUSED=True,
    input_or_final_model_raw_NPZ_SDK_GPU_or_account_reads_for_this_status=0,
    flight_diagnostic_not_success=True,success_not_measured=True,no_new_learning_or_training_change=True),ensure_ascii=False,indent=2),encoding='utf8')
selected.append(index.relative_to(G).as_posix())
git('add','--',*selected)
git('commit','-m','Append primary JUMP197 complete-save status199 and preserve contact-flight scope')
git('push','origin','HEAD')
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(after.get(k)==v and remote.get(k)==v for k,v in old.items())
head=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==head and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,ordinary_append=True,protected1501_objects_peels=True,files=len(rows),primary_iteration=summary['saved_iteration'],stable_jump='NOT_MEASURED',clean=True)))
