"""Review completed frozen cases only; no simulation or training authority."""
from pathlib import Path
import ast
import hashlib
import json
import math
import statistics
import time

D = Path(__file__).resolve().parent
R = D / 'reports'
OLD = D.parent / 'MOD4_E0_DT2500_ENV20K_CONTINUATION_20261007'
read = lambda p: json.loads(p.read_text(encoding='utf8'))
assert not (R / 'DIAGNOSTIC25525_MATCHED_REVIEW.json').exists()

# Reuse the already reviewed fact functions without executing its old one-shot body.
src = OLD / 'review_completed_clock2500.py'
nodes = []
for node in ast.parse(src.read_text(encoding='utf8')).body:
    if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef)):
        nodes.append(node)
    elif isinstance(node, ast.Assign) and isinstance(node.targets[0], ast.Name) and node.targets[0].id in ('D', 'read'):
        nodes.append(node)
    elif isinstance(node, ast.Expr) and ast.unparse(node).startswith('sys.path.insert'):
        nodes.append(node)
ns = {'__file__': str(src)}
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(src), 'exec'), ns)

transport = read(R / 'DIAGNOSTIC25525_RETURN_BYTES_VERIFIED.json')
assert len(transport['files']) == 9 and transport['all_bytes_exact']
remote_snapshot = read(OLD / 'reports/CLOCK2500_EVALUATOR_CURRENT_ACTUAL.json')
cases = {j['id']: j for j in remote_snapshot['jobs']}
sha = 'adf2ef02cf10e7a32efb34779f35252e8e7f4124494a88d11014c39c0ffb9e88'
report = dict(epoch=time.time(), source_sha256=sha, source_iteration_stored=25525,
              source_role='previously stopped policy, diagnostic frozen evaluation only',
              original_training_ordinary_bad_orientation_events=1,
              original_training_integrity_termination_events=0,
              original_training_max_closure_mm=1.982994842812419,
              scope='3060,2.5ms/TGS32-4/A0,seed20261002,white_v3,noise_bias_mild_v1,15s',
              current_training_source_unchanged=True, no_new_GPU_probe_or_PPO=True,
              no_budget_transaction=True, no_all_task_zero_claim=True,
              no_dualseed_threeprofile_or_full_DR_graduation_claim=True,
              pairing=[], candidate25211={}, diagnostic25525={}, returned_files=transport['files'])
for kind in ('flat', 'spin', 'world'):
    base_id = 'clk2500-solver32-20-candidate-' + kind
    job_id = 'clk2500-solver32-40-diagnostic25525-' + kind
    bdir = OLD / 'reports/windows' / base_id
    ndir = OLD / 'reports/windows' / job_id
    base, new = read(bdir / 'probe.json'), read(ndir / 'probe.json')
    result, manifest = read(ndir / 'result.json'), read(ndir / 'manifest.json')
    assert result['exit_code'] == 0 and result['errors'] == [] and result['result_present']
    assert result['checkpoint']['sha256'] == sha and result['steps'] == 1500
    assert result['runtime_archive_sha256'] == 'd1aa584bc05a6d09e4adf0dc50e609f2ba7e9deed1e57afa69ea7bb640a54c99'
    assert manifest['no_learning'] and not manifest['canonical_write_authority']
    assert cases[job_id]['probe'] == new and cases[job_id]['result'] == result
    pairing = dict(kind=kind, root_exact=base['reset_root_before_physics'] == new['reset_root_before_physics'],
                   q_exact=base['reset_joint_pos_before_physics'] == new['reset_joint_pos_before_physics'],
                   actual_parameters_exact=ns['params'](base) == ns['params'](new),
                   probe_exact=base['probe_sha256'] == new['probe_sha256'],
                   sensor_recipe_exact=base['sensor_recipe'] == new['sensor_recipe'],
                   solver_exact=base['clock2500_actual_solver'] == new['clock2500_actual_solver'],
                   seed_exact=base['seed'] == new['seed'] == 20261002)
    assert all(v for k, v in pairing.items() if k != 'kind'), pairing
    report['pairing'].append(pairing)
    report['candidate25211'][kind] = ns['facts'](base, kind)
    report['diagnostic25525'][kind] = ns['facts'](new, kind)

def summary(role):
    rows = report[role]
    return dict(world=rows['world']['target_count'], max_abs_cross=rows['world']['max_abs_cross'],
                along_range=rows['world']['along_range'], directions=rows['world']['directions'],
                straight=[g for g in rows['flat']['constant_speed'] if abs(g['command']) == 1.5],
                pure4pi=[{k: v for k, v in g.items() if k != 'values'} for g in rows['spin']['pure4pi']],
                closure_mm={k: rows[k]['closure_mm'] for k in ('flat', 'spin', 'world')})

report['summary'] = {role: summary(role) for role in ('candidate25211', 'diagnostic25525')}
jobs = [cases['clk2500-solver32-40-diagnostic25525-' + k]['result'] for k in ('flat', 'spin', 'world')]
report['cost'] = dict(process_wall_seconds=sum(j['physics_process_wall_seconds'] for j in jobs),
                      transfer_seconds=sum(j['transfer_seconds'] for j in jobs),
                      sampled_peak_MiB=max(j['observed_GPU_memory_mib'] for j in jobs), continuous_peak_claimed=False)
report['decision'] = 'Retain25525 as an observed skill-preserving candidate; current repaired25211-based training continues. No checkpoint switch or old supervisor resume.'
(R / 'DIAGNOSTIC25525_MATCHED_REVIEW.json').write_text(json.dumps(report, indent=2), encoding='utf8')
folder = D.parent / 'polar-rl-train/history/evidence/MOD4_DT2500_MODEL25525_DIAGNOSTIC_20261007'
folder.mkdir(exist_ok=False)
(folder / 'REVIEW.json').write_text(json.dumps(report, indent=2), encoding='utf8')
(folder / 'review_diagnostic25525_completed_once.py').write_bytes(Path(__file__).read_bytes())
note = '''# 已保存25525的独立回放完成，普通episode停训未导致既有技能丢失

旧4090候选25525此前因一次bad_orientation被旧监督器完整保存停训。原任务事件、1.982995mm训练闭链峰和所有权重继续保留，不改称原训练全task0。新的监督器已在另一隔离源218上运行20k PPO，本次只读取3060已完成的三个诊断回放。

同一3060、2.5ms/TGS32-4/A0、seed20261002、white_v3和noise_bias_mild_v1，flat80/spin88/world88各1500控制步15秒，均通过既有SCUTv4实际任务/模型/数据检查。与验证25211的完整初始root/q、实际参数、probe、sensor recipe和solver逐项exact；9份probe/result/manifest返回字节独立核验相同。

25525世界完整圈64/64，最坏净横向速度0.042556910m/s，along0.470474972–0.529082822m/s；25211对应64/64、0.041912537m/s。25525正/反4π各8/8满足原signedyaw±0.2rad/s，组均+12.491546/−12.552444rad/s。+1.5直线误差0.040279172→0.032540575m/s，−1.5误差0.022639973→0.024057917m/s。三诊断回放闭链峰0.575614/0.601763/0.681069mm，三进程wall634.197549s约10.57分钟，2秒采样显存峰3208MiB不是连续峰。

结论仅是这个已有平台协议下，停下保存的候选仍保留既有技能，没有证据支持把一次普通训练episode归因成整个策略或时钟失败。25525登记为可比较候选并保留，当前从25211恢复的新训练继续，不切换正在训练的源、不复活旧main、不放宽2mm/.01完整性合同。

这是单seed/单profile噪声协议的诊断结果，不是双seed三profile毕业、实车认证或隔离因果证明。完整圈、全窗口、有效前缀和原全部flags/raw保留。原大轨迹/权重只保存SHA索引。本次新GPU probe/PPO、预算操作、训练参数/暂停/重启均为0。
'''
(folder / 'REPORT.md').write_text(note, encoding='utf8')
(R / 'DIAGNOSTIC25525_MATCHED_REPORT.md').write_text(note, encoding='utf8')
print(json.dumps(dict(summary=report['summary'], cost=report['cost'], decision=report['decision']), indent=2))
