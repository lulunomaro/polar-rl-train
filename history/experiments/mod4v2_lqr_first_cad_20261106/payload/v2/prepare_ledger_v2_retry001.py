"""Recover only absent ledger, not the already-created runner/protocol/runtime.
Attempt001 counted 4 historical reuse-table rows in addition to 36 canonical rows.
"""
from pathlib import Path
import ast,re,json
ROOT=Path(__file__).resolve().parent;V1=ROOT.parent/'mod4v1_lqr_mpc_robust_20261102'
error=dict(status='PREP_LEDGER_SOFTWARE_ERROR_NO_PHYSICS',attempt='prepare_t01_v2.py',
 cause='Regex searched whole document: 36 canonical rows + 4 historical reuse rows, not a changed task list',
 existing_prefix_preserved=['T01_V2/run_t01_v2.py','T01_V2/T01_PROTOCOL_V1.json'],physics_steps=0,
 recovery='Only absent ledger generated from canonical section; original failed script retained, no runtime/protocol rerun')
with (ROOT/'PREP_T01_LEDGER_ATTEMPT001.json').open('x',encoding='utf-8')as f:json.dump(error,f,indent=2)
tree=ast.parse((ROOT/'prepare_t01_v2.py').read_text(encoding='utf-8'))
head=next(n.value.value for n in tree.body if isinstance(n,ast.Assign)and any(isinstance(t,ast.Name)and t.id=='head'for t in n.targets))
old=(V1/'TERRAIN_ADAPTATION_TASKS_V1.md').read_text(encoding='utf-8')
section=old.split('## 任务与验收行为',1)[1].split('\n## ',1)[0]
rows=re.findall(r'^\| (T\d{2}) \|([^|]+)\|([^|]+)\|',section,re.M)
assert len(rows)==36 and len({r[0]for r in rows})==36
head=head.replace('无，待原有静力子任务交付新版gain','无；新静力/DARE已收exit0、0物理步，首个物理case待启动')
for ident,name,behavior in rows:
 state='进行中：新模型名义基线'if ident=='T01'else'待处理：v2未验证'
 head+=f'| {ident} | {name.strip()} | {behavior.strip()} | {state} | [保留原记录](<../mod4v1_lqr_mpc_robust_20261102/TERRAIN_ADAPTATION_TASKS_V1.md>) |\n'
head+='''\n## 本轮case与软件记录\n\n- [新版增益](<nominal_gain_v2.json>)已由原代理一次实际生成exit0，0mj_step；delta=-.2，hip=.2503281103649727，tau6约[3.021463,-4.065098,0,3.001951,-4.049372,0]Nm。full投影静力残差1.66141e-9，DARE残差1.035e-15，闭环局部谱半径.992779681593；是线性化/静力证据，尚非闭环技能。\n- [生成源码](<v2_linearization.py>)真正调用P0绝对hip/crank set_configuration；558次新P0 setter/1716次forward/0积分，不读取或复跑旧case。\n- [首个冻结协议](<T01_V2/T01_PROTOCOL_V1.json>)原姿态/速度/2kHz承载gate不变；先只执行nominal_stand，其余case不自动启动。\n- [台账生成软件错误](<PREP_T01_LEDGER_ATTEMPT001.json>)保留：首次把4条历史复用行算进36主表，runner和protocol已创建/0物理；只限定主表区恢复台账，不重写已生成prefix。\n- 首个物理case尚未启动，模型实际计数/物理步/成败待回填；源码/数学通过不计36项能力通过。\n'''
with (ROOT/'TERRAIN_ADAPTATION_TASKS_V2.md').open('x',encoding='utf-8')as f:f.write(head)
print('V2_36_TASK_LEDGER_RECOVERED_ONLY canonical_rows=36 physics=0',flush=True)
