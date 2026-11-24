"""Choose fully documented passing representative cases, then validate zero-speed W+V."""
import json
import numpy as np
from fsm_paths import HERE
from fsm_io import put
from fsm_evaluation import run_case


def main():
    folder=HERE/'evidence/stage2_final'
    read=lambda name:json.loads((folder/name).read_text(encoding='utf-8'))
    stairs=read('stair/RESULT.json')['rows'];early=read('premature/RESULT.json')['rows']
    jumps=read('jump/RESULT.json')['rows'];checkpoint=HERE/json.loads((HERE/'CANDIDATE.json').read_text())['checkpoint']
    def select(rows):
        return min(rows,key=lambda r:(not r['passed'],bool(r['failure']),r['max_rollback_m'],r['peak_abs_pitch_deg']))
    def case(row):
        keys=('id','course','speed','height','yaw_deg','offset','seconds','settle_s','wz','task','edge_sign',
              'armed','dr','seed','restart','force_at_s','front_gap','hold_ticks','press_s')
        return {k:row[k] for k in keys if k in row}
    one=select([r for r in early if r['course']=='step_20'])
    two=select([r for r in early+stairs if r['course'] in ('rm27_west_400','rm27_east_400') and not r['dr']])
    oblique=[select([r for r in stairs if not r['dr'] and r['course']=='step_20' and r['yaw_deg']==angle]) for angle in (-25.,25.)]
    restarts=sorted([r for r in stairs if r['course']=='step_20' and not r['dr'] and r.get('force_at_s') is not None],
        key=lambda r:(not r['passed'],r['max_rollback_m'],r['peak_abs_pitch_deg']))
    attempts=[];restart_job=None
    for index,row in enumerate(restarts):
        job=dict(case(row),force_at_s=0.,id=f'video_zero_wv_{index:02d}')
        result,trace=run_case(job,checkpoint=checkpoint)
        target=folder/'video_recipe_validation';target.mkdir(exist_ok=True)
        put(target/(job['id']+'.json'),result)
        np.savez_compressed(target/(job['id']+'.npz'),**trace)
        attempts.append(result)
        if restart_job is None:restart_job=job
        if result['passed']:
            restart_job=job;break
    jump=select([r for r in jumps if r['course']=='platform_380' and r['speed']==2.8])
    specs=[dict(number=1,title='提前 2.5m 开 C · 200mm 单阶',jobs=[case(one)]),
        dict(number=2,title='RMUC2027 A–A · 200 → 400 → 360mm',jobs=[case(two)]),
        dict(number=3,title='200mm ±25° 斜入 / W+V 零速贴阶强起',jobs=[case(r) for r in oblique]+[restart_job]),
        dict(number=4,title='实速 2.8m/s 大跳 · 380mm 实体高台',jobs=[case(jump)])]
    put(folder/'VIDEO_CASES.json',specs)
    put(folder/'VIDEO_RECIPE_SELECTION.json',dict(stair_case_ids=[one['id'],two['id']]+[r['id'] for r in oblique],
        all_stair_source_cases_passed=all(r['passed'] for r in [one,two,*oblique]),
        zero_speed_wv_validation=attempts,
        jump_case=jump['id'],jump_passed=jump['passed'],
        note='Full benchmark failures remain in the benchmark; representative videos are explicitly selected cases.'))


if __name__=='__main__':main()
