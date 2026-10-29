"""Retain pre-control null-component rows as explicitly unmeasured, not zero reward."""
from pathlib import Path
import json,time,traceback
HERE=Path(__file__).resolve().parent
old=(HERE/'finalize_closed116_models_and_curves_text_only.py').read_text(encoding='utf8')
a="data=[json.loads(x) for x in raw.splitlines()];assert data"
b="all_data=[json.loads(x) for x in raw.splitlines()];assert all_data\n    unmeasured=[x['completed_control_rows'] for x in all_data if not x.get('fudan_real_reward_tracking',{}).get('components')]\n    assert all(x==0 for x in unmeasured),'noninitial missing reward components'\n    data=[x for x in all_data if x.get('fudan_real_reward_tracking',{}).get('components')];assert data"
assert old.count(a)==1
source=old.replace(a,b).replace('rows=len(data),first_control=', 'rows=len(data),initial_unmeasured_control_rows_retained=unmeasured,total_original_rows=len(all_data),first_control=')
try:exec(compile(source,str(Path(__file__).resolve()),'exec'),dict(__name__='selected_closed116_text_v2',__file__=str(HERE/'finalize_closed116_models_and_curves_text_only.py')))
except BaseException:
    with (HERE/'reports'/('CLOSED116_TEXT_V2_ORIGINAL_ERROR_'+str(time.time_ns())+'.json')).open('x') as f:json.dump(dict(error=traceback.format_exc(),no_model_raw_or_remote=True),f,indent=2)
    raise
