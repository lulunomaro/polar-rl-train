"""Distinguish the exact successful305 WM diagnostic from error records."""
from pathlib import Path
import json, math
DIAGNOSTIC='ACTUAL305_H32_PAIRED_REAL_WM_ERROR_BEFORE_PI.json'
METRICS=('H32_position_RMSE_m','H32_Rzz_MAE','one_step_position_RMSE_m','one_step_Rzz_MAE','loss')
def classify_error_reports(directory):
    fatal=[];diagnostic=[]
    for path in sorted(Path(directory).glob('*ERROR*.json')):
        try:
            row=json.loads(path.read_bytes())
            admitted=(path.name==DIAGNOSTIC and row.get('passed') is True
                and 'error' not in row and 'traceback' not in row
                and row.get('source')=='actual own contiguous transitions, fixed startobservedanchor; mask before episode reset'
                and row.get('prediction_uses_no_future_real_depth') is True
                and isinstance(row.get('sample_count'),int) and row['sample_count']>0
                and all(isinstance(row.get(k),(int,float)) and math.isfinite(row[k]) and row[k]>=0 for k in METRICS))
        except (OSError,ValueError,TypeError):admitted=False
        (diagnostic if admitted else fatal).append(str(path))
    return fatal,diagnostic
