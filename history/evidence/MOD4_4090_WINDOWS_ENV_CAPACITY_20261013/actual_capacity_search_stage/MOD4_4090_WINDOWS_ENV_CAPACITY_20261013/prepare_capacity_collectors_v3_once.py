from pathlib import Path
import json,time
D=Path(__file__).resolve().parent
p=D/'collect_capacity_completed_paths_reviewed_actual.py';s=p.read_text(encoding='utf8')
for a,b in [('n in (256,512,1024)','n in (256,512,640,768,1024)'),("s=R+f'/capacity{n}_own128_expanded_benchmark_v2_20261013'","s=R+f'/capacity{n}_own128_expanded_benchmark_'+('v3' if n in (640,768) else 'v2')+'_20261013'"),("(s/'payload').glob('*.py')","[p for p in (s/'payload').iterdir() if p.suffix in ('.py','.json')]")]:
 assert a in s;s=s.replace(a,b)
q=D/'collect_capacity_completed_with_schema_v3_actual.py';assert not q.exists();compile(s,str(q),'exec');q.write_text(s,encoding='utf8')
s=(D.parent/'MOD4_4090_WINDOWS_TEMP20GB_20261013/collect_all_temporary_sizes_evidence_actual.py').read_text(encoding='utf8')
a="sorted(r.glob('temporary_scope*memory20GB*'))";assert a in s;s=s.replace(a,"sorted([p for p in r.iterdir() if p.is_dir() and p.name.startswith('capacity')])")
s=s.replace('TEMP20GB_SAVED_EVIDENCE_','CAPACITY_SAVED_EVIDENCE_').replace('ALL_TEMP20GB_SAVED_REMOTE_EVIDENCE_','ALL_CAPACITY_SAVED_REMOTE_EVIDENCE_')
q=D/'collect_all_capacity_saved_evidence_actual.py';assert not q.exists();compile(s,str(q),'exec');q.write_text(s,encoding='utf8')
(D/'reports/CAPACITY_COLLECTOR_NATIVE_COMMAND_PREEXEC_PARSE_ERROR.json').write_text(json.dumps(dict(epoch=time.time(),original_error='PowerShell ParserError nested Python -c quote if token, before collector generation/CPU/GPU. Independent saved generator prepared.',no_GPU_replay=True),indent=2),encoding='utf8')
