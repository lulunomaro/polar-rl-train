"""Freeze future terminal collection; never contact a host or touch a model."""
from pathlib import Path
import ast,json,time,hashlib
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
S=T/'FUDAN_JUMP_PARALLEL_SINGLE_WRITER_HANDOFF_V197_20261031'
src=(S/'collect197_original_two_role_formals_cost_normal900_UNUSED_once.py').read_text('utf8')
for a,b in [('ROOT197','ROOT210'),('control197','control210v2'),('current_closed197_models','current_closed210_models'),('normal197_','normal210_'),('collect197_original_two_role_formals','collect210_original_two_role_formals')]:src=src.replace(a,b)
src=src.replace("read(N/'SCHEDULE_PUBLIC.json')","read(N/'SCHEDULE_V2_PUBLIC.json')")
src=src.replace("  client.close();client=None;client=route.connect()\n  result=d.code(client,route.PY,COLLECT_NODE,dict(spec=specs['h1_210']),timeout=210);results['h1_210']=result", "  result=d.code(client,d.PY72,COLLECT_NODE,dict(spec=specs['w35_72']),timeout=210);results['w35_72']=result")
src=src.replace('h1_210','w35_72').replace('PRIMARY210_FULL_UTF8','W35_72_FULL_UTF8')
src=src.replace("original_two_role_formals|launch197_unified_194_remaining|request197_original194_saved|install198_E0_72_source_CPU", "original_two_role_formals|launch210_|prepare212_|install211_|install209_|launch209_")
src=src.replace('old194_saved_input_or_E0_inputs_read=0','old_W35_and_E0_source_inputs_read=0')
src=src.replace("  if p.suffix not in ('.json','.log'):continue", "  if p.suffix in ('.npz','.npy','.jsonl','.usd','.usdc','.png','.mp4'):\n   models.append(dict(path=str(p),bytes=p.stat().st_size,SHA='existing producer or unknown; no binary/raw read'));continue\n  if p.suffix not in ('.json','.log'):continue")
src=src.replace("assert p.is_relative_to(B/'production')", "assert p.resolve().is_relative_to((B/'production').resolve())")
ast.parse(src)
out=N/'collect210_original_two_role_formals_cost_normal900_UNUSED_once.py'
with out.open('x',encoding='utf8',newline='\n') as f:f.write(src)
with (R/'FROZEN210_ORIGINAL_NORMAL900_COLLECTOR_SOURCE_INDEX.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),status='FROZEN_UNUSED',entry=out.name,SHA=hashlib.sha256(out.read_bytes()).hexdigest(),
  signed_local_AND_remote_nominal_minus_now_gate_seconds=900,original_owner_wait_seconds=850,original_node_wait_seconds=180,
  roles=['e0_72','w35_72'],one_NEW_formal_transfer_per_qualified_role=True,
  rawfees_sum_once_no_account_write=True,old_models_or_raw_read=0,source_only=True),f,indent=2)
print(json.dumps(dict(passed=True,future_collector_frozen_unused=True)))
