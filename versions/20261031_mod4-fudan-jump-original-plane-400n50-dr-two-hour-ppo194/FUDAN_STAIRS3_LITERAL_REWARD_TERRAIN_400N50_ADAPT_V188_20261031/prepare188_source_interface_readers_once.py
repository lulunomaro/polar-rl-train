from pathlib import Path
import ast
N=Path(__file__).resolve().parent;T=N.parent
old=T/'FORWARDED210_EXISTING_FUDAN_JUMP_MODEL_REUSE_V185_20261031/admit_delivered185_remote_model4999_CPU_state_once.py'
source=old.read_text(encoding='utf8');tree=ast.parse(source)
node=next(x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='REMOTE' for y in x.targets))
remote="""from pathlib import Path
import importlib.util,json,time,hashlib
root=Path(next(iter(importlib.util.find_spec('isaaclab').submodule_search_locations)))
paths=[root/'terrains/height_field/hf_terrains.py',root/'terrains/height_field/hf_terrains_cfg.py',root/'terrains/height_field/utils.py',Path('/mnt/mod4_linux_durable_20261013/rm2026_fudan_exact_20261031/repo/isaac/mod4/mod4_env.py'),Path('/mnt/mod4_linux_durable_20261013/rm2026_fudan_exact_20261031/repo/isaac/mod4/mild_dr.py')]
rows=[]
for p in paths:
 if not p.is_file():rows.append(dict(path=str(p),exists=False));continue
 b=p.read_bytes();rows.append(dict(path=str(p),exists=True,bytes=len(b),SHA=hashlib.sha256(b).hexdigest(),UTF8=b.decode('utf8'),byte_reads=1))
print(json.dumps(dict(epoch=time.time(),purpose='Bind unchanged original STAIRS3 general reward and terrain to existing400N50 Lab runtime; source-only installed API metadata',files=rows,source_files_read=sum(x['exists'] for x in rows),SDK_Torch_imports=0,model_reads=0,physics_GPU_or_learning_calls=0,no_remote_writes=True)))
"""
lines=source.splitlines(keepends=True);source=''.join(lines[:node.lineno-1])+('REMOTE='+repr(remote)+'\n')+''.join(lines[node.end_lineno:])
source=source.replace('ROOT185MODEL','ROOT188API').replace('admit_delivered185_remote_model4999_CPU_state_once','capture188_target_HF_and_original_step_sources_once')
source=source.replace('inspect_forward210_|','capture188_target_HF_and_original_step_sources_once|install_evaluate187_totalplan_frozen_once|inspect_forward210_|')
source=source.replace('checkpoint_content_reads=1,checkpoint_decode_limit=1','checkpoint_content_reads=0,checkpoint_decode_limit=0')
source=source.replace('Cancel two-arm comparison; find other AI\'s existing jumping model on original forwarded4090 and prefer reuse','Latest human selects original 上台阶3 general reward byte-literal and original Fudan stairs terrain, then continuation under400N50 total-plan DR')
start=source.index('  print(json.dumps(dict(source=result[');end=source.index('\n finally:',start)
source=source[:start]+"  print(json.dumps(dict(source_files=result['source_files_read'],model_reads=result['model_reads'],SDK_Torch_imports=result['SDK_Torch_imports'])),flush=True)"+source[end:]
ast.parse(source)
(N/'capture188_target_HF_and_original_step_sources_once.py').write_text(source,encoding='utf8')
