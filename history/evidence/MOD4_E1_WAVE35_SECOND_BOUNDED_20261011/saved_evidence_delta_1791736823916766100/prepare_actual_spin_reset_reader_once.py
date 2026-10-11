"""Preserve legacy missing-total rejection; bind observed resets to recorded episodes and failed prefixes."""
from second_io import *
import ast
old=D/'review_second_candidate_actual.py'
new=D/'review_second_candidate_reset_schema_actual.py'
assert not new.exists()
src=old.read_text(encoding='utf8')
node=next(n for n in ast.parse(common_source:=(W/'MOD4_E1_G1_ACTUAL_REVIEW_20261010/review_actual_schema_checked.py').read_text(encoding='utf8')).body if isinstance(n,ast.FunctionDef) and n.name=='reset_audit')
original=ast.unparse(node)
oldcheck="assert sum(increments) == p['resets'] if 'resets' in p else sum(increments) == 0"
assert oldcheck in original
replacement="""if 'resets' in p:
        assert sum(increments) == p['resets']
    elif any(increments):
        assert 'alive' in p and 'first_failure_step' in p
        assert len(p['alive']) == len(p['first_failure_step']) == len(increments)
        assert all(v in (0, 1) for v in increments)
        assert [i for i,v in enumerate(increments) if v] == [i for i,v in enumerate(p['alive']) if not v]
        for i,v in enumerate(increments):
            if v: assert not p['alive'][i] and 0 <= p['first_failure_step'][i] < p['steps']
        assert all(p['first_failure_step'][i] == p['steps'] for i,v in enumerate(increments) if not v)
    else:
        assert sum(increments) == 0"""
body=original.replace(oldcheck,replacement,1).replace("original_task_flags_retained=True)","original_task_flags_retained=True, total_resets_field_present='resets' in p, episode_increment_sum=sum(increments), missing_total_not_assumed_zero=True)")
src=src.replace('def main():',body+'\n\ndef main():',1).replace('resets=common.reset_audit(p)','resets=reset_audit(p)').replace("if not age:assert p.get('resets',0)>0","if not age:assert resets['episode_increment_sum']>0")
src=src.replace("'WAVE143_REVIEW_ERROR_'","'WAVE143_RESET_SCHEMA_REVIEW_ERROR_'")
compile(src,str(new),'exec');new.write_bytes(src.encode())
save('WAVE143_LEGACY_SPIN_RESET_READER_SCHEMA_REVIEW.json',dict(epoch=time.time(),original_reader=str(old),original_SHA=H(old.read_bytes()),new_reader=str(new),new_SHA=H(new.read_bytes()),original_rejection_retained=True,original_common_reader_unchanged=True,scope='Missing legacy spin reset total is disclosed; exact episode increments across action/spring/gas/COM/PD bound to alive and original first_failure_step. No physical validator or result edited.',actual_spin_env8_first_failure_control=370,actual_spin_env8_episode_increment=1,original_physical_smoke_false_retained=True,no_GPU_replay_or_budget_write=True))
save('SECOND_LOCAL_DISCOVERY_READER_ERRORS.json',dict(epoch=time.time(),errors=[dict(action='rg paths MOD4_E1*',error='PowerShell literal wildcard path invalid OS123',preGPU=True),dict(action='inspect action assignment episode directly',error="KeyError: episode; actual dict owns legs/wheels subgroups",preGPU=True)],no_production_or_result_change=True))
print(json.dumps(dict(prepared=str(new))))
