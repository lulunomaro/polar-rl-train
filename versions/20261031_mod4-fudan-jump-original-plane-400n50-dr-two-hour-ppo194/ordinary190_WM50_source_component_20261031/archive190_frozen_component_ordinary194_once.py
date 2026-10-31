from pathlib import Path
import hashlib,json,subprocess,sys,time,tomllib
N=Path(__file__).resolve().parent;T=N.parent;G=T.parent/'polar-rl-train';R=N/'reports'
phase=G/'versions/20261031_mod4-fudan-jump-original-plane-400n50-dr-two-hour-ppo194'
D=phase/'ordinary190_WM50_source_component_20261031'
def git(*args):return subprocess.run(['git','-C',str(G),*args],capture_output=True,text=True,encoding='utf8',check=True).stdout.strip()
def refs(s):return dict(line.split()[::-1] for line in s.splitlines() if line.strip())
assert not git('status','--porcelain') and not D.exists()
before=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert len([k for k in before if not k.endswith('^{}')])==1500 and all(remote.get(k)==v for k,v in before.items())
assert json.loads((R/'ROOT190_V2_SYNTHETIC_NATIVE_WM50_CPU_ACTUAL.json').read_bytes())['passed']
req=json.loads((R/'AUTOMATION190_FROZEN_COMPONENT_ORDINARY194_UPDATE_REQUEST.json').read_bytes())
actual=tomllib.loads(Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml').read_text('utf8'))
assert actual['prompt']==req['prompt'].rstrip('\n') and actual['target_thread_id']==req['targetThreadId'] and actual['rrule']==req['rrule'] and actual['status']=='ACTIVE'
with (R/'ARCHIVE190_ORDINARY194_ONCE_CONSUMED.json').open('x') as f:json.dump(dict(epoch=time.time(),ordinary_append_only=True,protected_tag_count=1500,no_new_tag_or_recorder=True,no_training_or_binary_reads=True),f,indent=2)
sys.path.insert(0,str(G/'archive_tools'));from capture_history import redact
D.mkdir();rows=[];selected=[]
sources=list(sorted(p for p in N.rglob('*') if p.is_file()))
sources.append(T/'FUDAN_JUMP_LITERAL_PLANE_400N50_DR_TWO_HOUR_V194_20261031/reports/CURRENT_BACKGROUND190_FROZEN_WM50_COMPONENT_ONLY_AFTER194_FIRST.json')
for p in sources:
 assert p.suffix in ('.py','.json'),p
 raw=p.read_bytes();text=raw.decode('utf8');assert redact(text)[0]==text,str(p)
 rel=p.relative_to(N) if p.is_relative_to(N) else Path('194_reports')/p.name
 dest=D/rel;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
 rows.append(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),Git_path=dest.relative_to(G).as_posix(),capture='full_UTF8_byte_exact'))
 selected.append(dest.relative_to(G).as_posix())
index=D/'CAPTURE_INDEX.json';index.write_text(json.dumps(dict(epoch=time.time(),ordinary194_supplement=True,files=rows,
 source_component_only=True,actual_expert_model_raw_reads=0,SDK_remote_GPU_calls=0,native_policy_conversion=False,
 selected_V3_only_diagnostic_label_delta=True,actual_complete_runtime_caller_explicit_pending=True,
 first194_healthy_training_untouched=True),indent=2),encoding='utf8');selected.append(index.relative_to(G).as_posix())
for i in range(0,len(selected),24):git('add','--',*selected[i:i+24])
git('commit','-m','Append frozen WM50 teacher component CPU evidence while literal JUMP194 window continues')
git('push','origin','HEAD')
after=refs(git('show-ref','--tags','-d'));remote=refs(git('ls-remote','--tags','origin'))
assert all(after.get(k)==v and remote.get(k)==v for k,v in before.items())
head=git('rev-parse','HEAD');assert git('ls-remote','origin','refs/heads/main').split()[0]==head and not git('status','--porcelain')
print(json.dumps(dict(passed=True,HEAD=head,ordinary_append=True,no_new_tags=True,protected1500_objects_peels=True,full_UTF8_files=len(rows),clean=True)))
