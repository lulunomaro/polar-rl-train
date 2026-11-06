"""Pinned source reward requirements and complete readable semantic coverage."""
from pathlib import Path
import ast
import json

from build import write_json,sha


def inventory(repo,package):
    repo,package=Path(repo),Path(package)
    source=repo/'source/agent_tasks/agent_tasks/direct/wheelbipe/wheelbipe25_v3/env.py'
    code=source.read_text(encoding='utf8');tree=ast.parse(code)
    cls=next(n for n in tree.body if isinstance(n,ast.ClassDef)and n.name=='Wheelbipe25V3Env')
    fun=next(n for n in cls.body if isinstance(n,ast.FunctionDef)and n.name=='_get_rewards')
    terms=sorted({n.id[4:]for n in ast.walk(fun)if isinstance(n,ast.Name)and isinstance(n.ctx,ast.Store)and n.id.startswith('rew_')})
    fields=sorted({ast.unparse(n)for n in ast.walk(fun)if isinstance(n,ast.Attribute)and isinstance(n.value,ast.Name)and n.value.id=='self'})
    methods=sorted({n.func.attr for n in ast.walk(fun)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and isinstance(n.func.value,ast.Name)and n.func.value.id=='self'})
    report=dict(schema='mod4v3.SCUT_reward_source_inventory.v1',source=source.relative_to(repo).as_posix(),sha256=sha(source),
        function='_get_rewards',lines=[fun.lineno,fun.end_lineno],reward_terms=terms,self_requirements=fields,called_methods=methods,
        core_robot_state_boundary='ScutRobotView: names, q, qd, qdd, applied torque, body state, quaternion',
        separate_environment_requirements=['final terminated/truncated flags','pre-reset terminal observation',
            'current command and actual control dt','previous two actions and applied torques',
            'contact sensor with its own name order','terrain rays and state-machine cache/clock'],
        not_implemented_as_asset_metadata=['task state machines','commands','raycaster','critic/learner'],
        source_silent_zero_disabled_in_new_interface=True,
        source_formulas_not_reweighted=True)
    write_json(package/'SCUT_REWARD_REQUIREMENTS.json',report)
    spec=json.loads((package/'semantics.json').read_bytes())
    lines=['# MOD4v3 与华南虎 V14_2 语义对应','',
        '参考来自固定 Git revision 的华南虎 USD、关节顺序、观测和奖励代码。该参考仓库无 MJCF。',
        '下表的“对应”是机构功能与坐标定义对应，MOD4 的尺寸、惯量、硬件限位不会替换为华南虎参数。','',
        '| 华南虎关节/闭链轴 | 原 MOD4v2 | v3 接口 | 状态 |','|---|---|---|---|']
    for r in spec['reference_coverage']['joints']:
        lines.append('| '+r['scut']+' | '+str(r['mod4v2']or'—')+' | '+str(r['binding']or'明确不存在，读取报错')+' | '+r['status']+' |')
    lines+=['','| 华南虎刚体 | 原 MOD4v2 | v3 刚体 | 状态 |','|---|---|---|---|']
    for r in spec['reference_coverage']['bodies']:
        lines.append('| '+r['scut']+' | '+str(r['mod4v2']or'—')+' | '+str(r['mod4v3']or'—')+' | '+r['status']+' |')
    lines+=['','## 零位与正方向','',
        '所有 hinge 均采用实体 +Y 转轴。通过对应销轴连线推导 anatomical reference frame；',
        'v3 MJCF 使用 ref 偏移，USD 使用连杆局部帧，实体 mesh/collider/惯量反向变换抵消，原世界几何保持。',
        '原闭链树切口保留。front3 为 front1+front2 连杆到 rocker 的相对标量：',
        '`q_front3 = q_rear1 + q_f3r1 - q_front1 - q_front2`。位置、速度、加速度与力矩分别正确转换。',
        'rear2 是原 knee/shin，确有对应。此前“没有 rear2”判断错误，原错误记录不改写。','',
        '## 几何量和执行时序','',
        '华南虎腿长：base-to-wheel 向量的 heading XZ 投影范数。腿角 atan2(-x,-z)。',
        'MOD4 L0：真实 hip-to-wheel 三维范数；theta 为 atan2(x,-z)。两套量独立命名。',
        '终止奖励读取本步最终 terminated 后再 reset；timeout 的价值自举读取 terminal observation。',
        '非零权重项未计算必须报错。历史动作和力矩在本步计分完成后推进。','',
        '## 适用边界','',
        '37 个参考刚体、42 个参考关节/闭链轴均逐项说明；MOD4 少两个云台刚体和八个导轮刚体。',
        '不存在项不生成假质量/假接触或零奖励。MOD4 的四个传动 follower 保留为额外显式坐标。',
        '此包不声称原华南虎 checkpoint 可直接复用，也不声称 PPO/SuperMimic 已收敛。']
    (package/'SEMANTIC_ALIGNMENT.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
    return report


if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('reference_repo',type=Path);p.add_argument('package',type=Path);a=p.parse_args()
    print(json.dumps(dict(reward_terms=len(inventory(a.reference_repo,a.package)['reward_terms']))))
