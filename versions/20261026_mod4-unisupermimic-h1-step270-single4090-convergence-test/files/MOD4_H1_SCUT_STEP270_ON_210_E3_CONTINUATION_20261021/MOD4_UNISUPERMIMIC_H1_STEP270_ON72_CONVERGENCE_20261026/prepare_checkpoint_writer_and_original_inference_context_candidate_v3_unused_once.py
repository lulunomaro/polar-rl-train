"""Fix observed pre-sampling save API; align sampler context, without touching live81O."""
from pathlib import Path
import ast
import hashlib
import json
import shutil
import time

H=Path(__file__).resolve().parent;T=H.parent
O=T/'H1_STEP270_MIXED_UNISUPERMIMIC_RESOURCE_V81O_20261026'
source=O/'payloads/e2/source'
D=H/'candidate_source_v3';assert not D.exists();shutil.copytree(source,D,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
p=D/'h1_supermimic_bridge_v1.py';old=p.read_bytes();s=old.decode('utf8')
needle='    B,J,out=Path(B),Path(J),Path(out)\n';assert s.count(needle)==1
s=s.replace(needle,needle+"    runner.logger.writer=None  # same bootstrap used by original H1 PPO save chain\n",1)
for name in ('pack','current','before_action','step'):
    needle='    def '+name+'(';assert s.count(needle)==1
    s=s.replace(needle,'    @torch.inference_mode()\n'+needle,1)
start=s.index('        save(str(path))\n',s.index('    finally:\n        trace.persist()'))
end=s.index("        put(out/'FAILED_PARTIAL_NATIVE_FULLSTATE_ACTUAL.json'",start)
line_end=s.index('\n',end)
original=s[start:line_end]
replacement="""        try:
            save(str(path))
        except BaseException:
            put(out/'NATIVE_FULLSAVE_ORIGINAL_ERROR.json',dict(epoch=time.time(),error=traceback.format_exc(),original_primary_learning_error_preserved=failed,partial_file_retained=True))
            if not failed:raise
        else:
            final=dict(path=str(path),bytes=path.stat().st_size,SHA=hashlib.sha256(path.read_bytes()).hexdigest(),updates=learner.iteration,world_updates=bridge.wm_updates,policy_updates=bridge.pi_updates,original_H1_events=trace.lifetime_goal_counter.snapshot(),not_production_H1_or_E2_source=True)
            put(out/'FAILED_PARTIAL_NATIVE_FULLSTATE_ACTUAL.json' if failed else 'FINAL.json',dict(epoch=time.time(),passed=not failed and bridge.pi_updates>0,final=final,not_frozen_skill_graduation=True))"""
s=s[:start]+replacement+s[line_end:]
ast.parse(s);p.write_text(s,'utf8')
with (H/'reports/81O_OBSERVED_SAVE_ERROR_AND_CANDIDATE_V3_SOURCE_ONLY_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),actual81O_native_controls=0,actual81O_native_optimizer_updates=0,observed_error='RSL Logger.writer missing in original checkpoint save before first policy/action sampling',actual81O_original_slot_fee=458.8101952075958,original_worker_rc0_is_not_success=True,whole_original_owner_still_manages_healthy_H1_E3=True,candidate=str(D),original_bridge_SHA=hashlib.sha256(old).hexdigest(),candidate_bridge_SHA=hashlib.sha256(p.read_bytes()).hexdigest(),changes=['initialize runner.logger.writer=None exactly as original H1 production bootstrap','physical sampling/current-state/audit hooks use original RSL inference_mode context','secondary failed-fullsave error preserved separately without hiding primary error'],inference_context_is_prospective_compatibility_not_observed81O_failure=True,no_existing_root_or_active_process_hotpatch=True,not_installed_or_GO=True),f,indent=2)
print(json.dumps(dict(candidate_v3_source_only=True,observed_writer_error_fixed_in_new_source=True)))
