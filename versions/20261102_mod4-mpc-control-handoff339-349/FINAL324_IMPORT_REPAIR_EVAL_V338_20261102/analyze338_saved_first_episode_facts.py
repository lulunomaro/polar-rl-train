"""Summarize saved independent328/308 first-episode facts without model/raw reads."""
from pathlib import Path
import hashlib, json, statistics, time

P = Path(__file__).resolve().parent
T = P.parent
E = T / 'FINAL324_IMPORT_REPAIR_EVAL_V338_20261102'
R = P / 'reports'
read = lambda p: json.loads(p.read_bytes())
H = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()

def summarize(result):
    rows = result['results']
    assert len(rows) == 80 and len({row['env'] for row in rows}) == 80
    seconds = [row['seconds'] for row in rows]
    assert all(0 < sec <= 8 for sec in seconds)
    components = sorted({key for row in rows for key in row.get('tracking_components', {})})
    return dict(
        model_SHA=result['model_SHA'], cases=80, strict=result['strict_successes'], crossed=result['crossed_cases'],
        terminations=result['terminations'], full8s=sum(bool(row['full_window']) for row in rows),
        mean_seconds=statistics.mean(seconds), median_seconds=statistics.median(seconds), min_seconds=min(seconds), max_seconds=max(seconds),
        airborne_cases=sum(bool(row.get('airborne_ever')) for row in rows),
        case_mean_tracking_cost=statistics.mean(row['tracking_cost_mean'] for row in rows),
        transition_mean_tracking_cost=sum(row['tracking_cost_mean']*row['controls'] for row in rows)/sum(row['controls'] for row in rows),
        case_mean_tracking_components={key:statistics.mean(row['tracking_components'][key] for row in rows) for key in components},
        transition_mean_tracking_components={key:sum(row['tracking_components'][key]*row['controls'] for row in rows)/sum(row['controls'] for row in rows) for key in components},
        action_overflow_counts=[sum(row['action_overflow'][channel] for row in rows) for channel in range(6)],
        completed_first_episode_controls=sum(row['controls'] for row in rows),
        depth_valid_first_episode_controls=sum(row['depth_valid_controls'] for row in rows),
        selected_replay_cases=[dict(env=row['env'], controls=row['controls'], seconds=row['seconds'], result=row['result'], path=row['path'], bytes=row['bytes'], SHA=row['SHA']) for row in result['replay']],
        scope='independent DR/episode seed9137, same fixededge.8/270 platform; no heldoutterrain claim')

current_path = E / 'reports/ROOT338_EVALUATION_FULL_RETURNED.json'
previous_path = T / 'RECOVERED305_TRACKING_REPLAY_EVAL_V308_20261102/reports/ROOT308_EVALUATION_FULL_RETURNED.json'
current = read(current_path)
assert not current['wrapper_error'] and current['result']['passed']
assert (E / 'reports/ROOT338_ALL_SSH_CLOSED_FREE.json').is_file()
new = summarize(current['result'])
old = summarize(read(previous_path)['result'])
out = dict(epoch=time.time(), kind='SAVED_FINAL324_INDEPENDENT338_COMPARISON_WITH305_308',
    current=new, previous=old,
    difference=dict(mean_seconds=new['mean_seconds']-old['mean_seconds'], full8s=new['full8s']-old['full8s'], orientation=new['terminations']['bad_orientation']-old['terminations']['bad_orientation'], crossed=new['crossed']-old['crossed'], strict=new['strict']-old['strict']),
    current_report=dict(path=str(current_path), SHA=H(current_path)), previous_report=dict(path=str(previous_path), SHA=H(previous_path)),
    model_reads=0, raw_or_replay_reads=0, SDK_or_physics=0, optimizer_steps=0, account_access=0,
    native_visual_review_required=True, no_causal_single_fix_claim=True,
    success_requires='firstflightcross/fullwheelfootprint/topcontact/stable.5s and actualmanifold')
path = R / 'ACTUAL338_FINAL324_EVAL338_COMPARISON_NO_MODEL_READS.json'
with path.open('x', encoding='utf8') as f:
    json.dump(out, f, indent=2, ensure_ascii=False, allow_nan=False)
print(json.dumps(out, ensure_ascii=False, indent=2))
