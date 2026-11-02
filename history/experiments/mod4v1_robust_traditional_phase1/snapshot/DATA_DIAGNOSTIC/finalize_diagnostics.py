"""Final static integrity and yaw-bias human notes; no simulation imports."""
from pathlib import Path
import ast,hashlib,json
OUT=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def meta(p):p=Path(p);return {'path':str(p),'bytes':p.stat().st_size,'sha256':sha(p)}
def link(p,label=None):return '['+(label or Path(p).name)+'](<'+Path(p).as_posix()+'>)'
def vec(v):return '('+', '.join(f'{x:.10g}' for x in v)+')'
def main():
    r=json.loads((OUT/'YAW_NOMINAL_BIAS.json').read_text(encoding='utf-8'));ix=json.loads((OUT/'DATA_DIAGNOSTIC_INDEX.json').read_text(encoding='utf-8'));assert all(sha(x['path'])==x['sha256'] for x in r['source_files'])
    assert all(sha(x['path'])==x['sha256'] for x in ix['sources'])
    assert sha(ix['report']['path'])==ix['report']['sha256'] and all(sha(x['path'])==x['sha256'] for x in ix['artifacts'])
    note=OUT/'YAW_NOMINAL_BIAS_NOTES.md';assert not note.exists()
    L=['# 名义yaw bias：静态fixed-chart模板，不是稳态纯转解','',
       '数据：'+link(OUT/'YAW_NOMINAL_BIAS.json')+'；脚本：'+link(OUT/'compute_yaw_nominal_bias.py')+'。',
       '', '## 直接可用的数学系数', '',
       '执行顺序：'+', '.join(r['actuator_order'])+'。单位为输出关节Nm；XMLgear=1，勿再乘9或15.8。',
       '', '`tau(omega)=tau0 + c_even*omega**2 + c_odd*omega`，由0,+1,−1rad/s计算。',
       '', '- tau0='+vec(r['tau0_Nm'])+' Nm。',
       '- c_even='+vec(r['tau_even_per_yawrate_squared_Nm_s2'])+' Nm/(rad/s)²。',
       '- c_odd='+vec(r['tau_odd_per_yawrate_Nm_s'])+' Nm/(rad/s)。',
       '', '若父已有gas/gravity FF，只加delta项，避免重复叠加tau0。系数不是新controller/硬件binding。',
       '', '## 逐点残差与边界', '',
       '|omega rad/s|lstsq residual x force N|其余6维残差Nm最大绝对值|混合单位残差norm（仅数诊）|FF超当前DC边界个数|',
       '|---:|---:|---:|---:|---:|']
    for a in r['rows']:
        L.append('|'+f"{a['yaw_rate_rad_s']:.8g}"+'|'+f"{a['residual_x_force_N']:.6g}"+'|'+f"{max(abs(x) for x in a['residual_other_generalized_torques_Nm']):.6g}"+'|'+f"{a['mixed_unit_residual_l2_diagnostic_only']:.6g}"+'|'+str(sum(a['tau_outside_nominal_DC_bounds']))+'|')
    L += ['', '±0.5/±1/±2/±2.6808/±4/±4π范围内二次＋一次拟合最大误差 '+f"{r['max_fit_error_Nm']:.6g}"+'Nm。精确拟合的是这个固定chart，不证明真实spin等价。',
          '', '## 关键限制：pivot/侧向滑动', '',
          '继承full_reduced的q=[rootWorldX,yaw,pitch,Lhip,Ldelta,Rhip,Rdelta]固定名义q，v只在yaw列非零。chassis origin的worldXY固定，而wheelmid_B.x=−0.0342023945m。',
          '静态mj_jacBody表明omega=1时左右wheel center body速度分别约(−.2188,−.0342024,0)与(+.2188,−.0342024,0)m/s；4π时共同侧向速度约−.429800m/s。因此它不是围绕wheelmid/COM的精确无侧滑纯转chart。',
          '', '此外：使用0.0637圆轮支撑chart，不是姿态依赖的真实凸包接触；Gᵀ(passive−bias)不纳入实际接触constraint reaction，固定chart未展开完整moving-reference关系。每点7维Btau+f残差均已报告，未假定可精确平衡。',
          '', 'R01实际yaw约2.6808时，四腿even delta仅约(.105,.299,.105,.299)Nm；与R01腿间约数十Nm的观测差别相比，不支持“漏掉这个ω²项就充分导致劈叉”的强因果结论。固定零yaw gain/参考点/接触耦合失配仍是待对照假说。',
          '', '## 速度和轴证据', '',
          '双wheel joint轴为+bodyY；正wheel spin的底接触点相对轮心速度向−bodyX，无滑时轮心向+bodyX。正yaw需左轮负、右轮正，与R01符号一致。主惯性PCA轴不改变joint axis；这些是软件模型证据，未验证实际CAN极性。',
          'controller wheel no-load=55.3557rad/s，metadata缩放值55.3649085074rad/s，仅差−0.0166324%；输出转子总比15.8，metadata rotor no-load≈8353.396rpm。R01尾wheel速度峰值约53.710rad/s，对应rotor≈8103.73rpm（controller no-load的97.0273%），均值约−4818/+3518rpm。',
          'no-load为零正向电机转矩点，不是外力驱动/再生区的绝对硬限；工程转矩转速曲线、热/峰值持续时间、硬件最大rotor转速未实测。leg输出no-load160rpm×9=rotor1440rpm，XML输入仍输出关节Nm/rad/s。',
          '', '## 零步与来源', '',
          'RobustPlant实际构造一次，仅tmp参与403次forward；step/step1/step2均设fail guard且调用数0，tmp时间0，主plant.d与tick保持原样。没有物理rollout/DR重跑、父模块或模型改写。',
          '所有source SHA最终复核通过；缺失的source_snapshots/r01路径检索错误保留，不假称该快照存在，计算绑定实际读取的当前源码SHA。']
    note.write_text('\n'.join(L)+'\n',encoding='utf-8')
    errors={'preserved_errors':[{'operation':'glob','path':str(OUT.parent/'source_snapshots/r01'),'original_error':'Error: glob search failed (exit 2): rg: F:\\RMPOLAR-RL\\mod4v1_lqr_mpc_robust_20261102\\source_snapshots\\r01: IO error for operation on F:\\RMPOLAR-RL\\mod4v1_lqr_mpc_robust_20261102\\source_snapshots\\r01: 系统找不到指定的文件。 (os error 2)'},
                              {'error_file':meta(OUT/'STATIC_FRAME_FAILURE_001.txt'),'log':meta(OUT/'STATIC_FRAME_001.log'),'resolution':'nv0 all-fixed fixture unsuitable; stationary COM-anchored nv1 and free known-omega fixtures pass; not classified as actual model IMU-axis error'}]}
    (OUT/'READER_AND_ATTEMPT_ERRORS.json').write_text(json.dumps(errors,ensure_ascii=False,indent=2),encoding='utf-8')
    newnames=['YAW_NOMINAL_BIAS.json','compute_yaw_nominal_bias.py','YAW_BIAS_001.log','YAW_NOMINAL_BIAS_NOTES.md','extract_exact_report_numbers.py','EXACT_SOURCE_NUMBERS.json','READER_AND_ATTEMPT_ERRORS.json','finalize_diagnostics.py']
    for name in newnames:
        if name.endswith('.py'):ast.parse((OUT/name).read_text(encoding='utf-8'))
    final={'status':'PASS_FINAL_SOURCE_DATA_STATIC_INTEGRITY','R00_index':meta(OUT/'DATA_DIAGNOSTIC_INDEX.json'),'R00_report':meta(OUT/'R00_DATA_DIAGNOSTIC.md'),'yaw_bias':meta(OUT/'YAW_NOMINAL_BIAS.json'),'yaw_notes':meta(note),'all_original_and_bound_source_hashes_match':True,'all_R00_indexed_artifact_hashes_match':True,'physics_steps_total_this_diagnostic':0,'new_rollout_episodes':0,'time_advanced_s':0.,'static_forward_successful_calls':27+r['tmp_only_forward_calls'],'failed_nv0_fixture_forward_calls':6,'R00_offline_replay_exact':True,'no_parent_modifications':True,'additional_artifacts':[meta(OUT/name) for name in newnames]}
    path=OUT/'FINAL_DIAGNOSTIC_QA.json';assert not path.exists();path.write_text(json.dumps(final,ensure_ascii=False,indent=2,allow_nan=False),encoding='utf-8')
    print(json.dumps({'QA':meta(path),'yaw_notes':meta(note),'summary_rows':[{k:a[k] for k in ['yaw_rate_rad_s','residual_x_force_N','mixed_unit_residual_l2_diagnostic_only','tau_outside_nominal_DC_bounds']} for a in r['rows']],'status':final['status']},indent=2))
if __name__=='__main__':main()
