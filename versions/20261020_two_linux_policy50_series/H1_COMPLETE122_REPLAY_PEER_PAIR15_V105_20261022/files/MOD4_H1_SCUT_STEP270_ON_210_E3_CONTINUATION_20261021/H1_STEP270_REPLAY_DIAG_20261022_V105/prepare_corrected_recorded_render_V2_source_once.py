from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent;R=D/'reports';old=D/'render_recorded_step_attempts_CPU_once.py';s=old.read_text('utf8')
report=dict(epoch=time.time(),original_source=str(old),original_render_succeeded=True,original_outputs_preserved=True,caption_error='Case2 phrase 到边缘时 was overbroad: the observed wheels remained at least 50mm short; request display was constant .8 instead of per-row actual flag',correction='Case2 says the whole retained segment remains below clearance; show each recorded public_request flag',no_reextraction_kinematic_recompute_GPU_or_training_change=True)
with (R/'RENDER_V1_CAPTION_SCOPE_CORRECTION_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
s=s.replace('向前走得更多，但到边缘时高度不足','前进更远，但片段内轮底仍不够高').replace('请求前进0.8 m/s','请求前进{(.8 if bool(z["public_request"][frame,e]) else 0.):.1f} m/s').replace("D/f'case_", "D/f'case_V2_")
s=s.replace('STEP270_RECORDED_REPLAY.gif','STEP270_RECORDED_REPLAY_V2.gif').replace('STEP270_REPLAY_POSTER.png','STEP270_REPLAY_POSTER_V2.png').replace('STEP270_REPLAY_CASES.png','STEP270_REPLAY_CASES_V2.png').replace('RECORDED_REPLAY_RENDER_CPU_ACTUAL.json','RECORDED_REPLAY_RENDER_V2_CPU_ACTUAL.json').replace('RENDER_ORIGINAL_ERROR_','RENDER_V2_ORIGINAL_ERROR_')
ast.parse(s);(D/'render_recorded_step_attempts_CPU_V2_once.py').open('x',encoding='utf8').write(s)
print(json.dumps(dict(new_render_source_prepared=True,old_outputs_preserved=True)))
