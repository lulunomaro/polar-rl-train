"""Summarize the frozen H5 from small result receipts, never rehash robot raws.
No plant imports, parameter selection, episode reruns or controller modification.
"""
from pathlib import Path
import collections,hashlib,json,math,statistics
R=Path(__file__).resolve().parent;D=R/'MINIHOP_L20_H5_V1';B=R/'batches/h5_l20_minihop64'
def readj(p):return json.loads(p.read_bytes())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):
    with p.open('x',encoding='utf-8')as f:json.dump(x,f,indent=2,allow_nan=False)
def wilson(k,n):
    if not n:return None
    z=1.959963984540054;p=k/n;den=1+z*z/n
    mid=(p+z*z/(2*n))/den;half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return [max(0.,mid-half),min(1.,mid+half)]
def span(values):
    a=[float(x)for x in values if x is not None]
    assert all(math.isfinite(x)for x in a)
    return dict(count=len(a),minimum=min(a),median=statistics.median(a),maximum=max(a))if a else None

def main():
    p=readj(D/'PROTOCOL.json');base=readj(D/'FROZEN_BASE_CONFIG.json');batch=readj(B/'BATCH_RESULT.json')
    assert sha(D/'FROZEN_BASE_CONFIG.json')==p['base_config_SHA']and sha(D/'CONTROLLER_SOURCE_INDEX.json')==p['source_index_SHA']
    protocol=readj(B/'PROTOCOL.json');assert protocol['frozen_protocol_SHA']==sha(D/'PROTOCOL.json')
    expected=[f'h5_l20_minihop_{s}'for s in p['seeds']];assert protocol['case_names']==expected
    assert batch['scheduled']==len(expected)and batch['executed']==len(batch['rows'])
    executed={x['case']for x in batch['rows']};assert len(executed)==len(batch['rows'])and executed<=set(expected)
    assert set(batch['unstarted'])==set(expected)-executed
    rows=[];software=[];by_delay=collections.defaultdict(lambda:dict(executed=0,passed=0));raw=[]
    for item in batch['rows']:
        case=item['case'];seed=int(case.rsplit('_',1)[1]);path=R/'results'/case/'result.json'
        if item['returncode']!=0:
            er=item.get('software_error')
            if er is None:
                ep=path.parent/'ERROR.json'
                if ep.is_file():er=readj(ep)
            er=er if isinstance(er,dict)else None
            def known_count(name):
                x=er.get(name)if er is not None else None
                return x if type(x)is int and x>=0 else None
            software.append(dict(case=case,returncode=item['returncode'],result_exists=path.is_file(),error_receipt=er,
                                 recorded_prefix_controls=known_count('controls'),recorded_prefix_physics_steps=known_count('physics_steps')))
            continue
        assert path.is_file(),case
        v=readj(path);cfg=dict(v['config']);assert cfg.pop('case_id')==case and cfg.pop('seed')==seed and cfg==base,case
        assert v['model_SHA']=='0e9ca6854285dc73465a198656fdedd992ffbf205c4ea9ed9d3ce88b905bf324'
        assert v['audit_version']==2 and v['controller_truth_inputs']is False and v['root_assist_forces']==0 and v['root_state_overwrites_after_initialization']==0
        assert v['DR']['seed']==seed and v['DR']['nominal']is False and all(f'D{i}'in v['DR']for i in range(8))
        assert v['DR']['D1']['enabled']is True and v['DR']['D1']['sample_hz']==100
        assert v['physics_steps']==20*v['controls']and 0<v['controls']<=600
        assert not v['complete']or(v['controls']==600 and v['physics_steps']==12000 and v['stop']=='complete')
        clear=v['maximum_main_mesh_clearance_during_full_air_m'];end=v['end_stable_s']
        assert clear is None or math.isfinite(clear)
        assert math.isfinite(end)
        checks=dict(complete=v['complete']is True,clearance=clear is not None and clear>=.08,
                    no_guide=v['after_trigger_guide_contact_physics_ticks']==0,
                    no_hard=v['after_trigger_hard_contact_physics_ticks']==0,end_stable=end>=2.)
        passed=all(checks.values());assert passed is v['proposed_flat_clear80mm_recover2s_v2'],case
        delay=v['DR']['D3']['requested_delay_us'];assert delay in(0,10000)
        by_delay[delay]['executed']+=1;by_delay[delay]['passed']+=int(passed)
        row=dict(case=case,seed=seed,passed=passed,failed_gates=[k for k,b in checks.items()if not b],complete=v['complete'],stop=v['stop'],
                 controls=v['controls'],physics_steps=v['physics_steps'],feedback_delay_us=delay,
                 D0_only_nominal_branch=v['DR']['D0']['D0_only_nominal_episode'],clearance_m=clear,end_stable_s=end,
                 guide_ticks=v['after_trigger_guide_contact_physics_ticks'],hard_ticks=v['after_trigger_hard_contact_physics_ticks'],
                 max_pitch_rad=v['max_pitch_rad'],max_roll_rad=v['max_roll_rad'],peak_positive_mechanical_power_W=v['peak_positive_mechanical_power_W'],
                 first_air_s=v['first_all_world_air_s'],first_landing=v['first_landing'],result_path=str(path),result_SHA=sha(path))
        rows.append(row)
        for k in('trace_artifact','physical_artifact'):
            a=dict(v[k]);assert a['producer_streamed_once']is True
            raw.append(dict(case=case,role=k,**a,raw_rehashed_for_report=False))
    accepted=sum(x['passed']for x in rows)
    full=not software and not batch['unstarted']and len(rows)==len(expected)
    failures=collections.Counter(k for x in rows for k in x['failed_gates'])
    result=dict(kind='FROZEN_H5_INDEPENDENT_OPERATOR_TIMED_FLAT_MINIHOP_FACTS',status='COMPLETE_FROZEN_HOLDOUT'if full else'INTERRUPTED_SOFTWARE_OR_UNSTARTED',
                protocol_path=str(D/'PROTOCOL.json'),protocol_SHA=sha(D/'PROTOCOL.json'),planned=len(expected),executed=batch['executed'],
                physical_result_count=len(rows),complete_episodes=sum(x['complete']for x in rows),passed=accepted,robot_failed=len(rows)-accepted,
                software_errors=software,unstarted=batch['unstarted'],planned_denominator_qualified=full,
                success_fraction=accepted/len(expected)if full else None,wilson95=wilson(accepted,len(expected))if full else None,
                wilson_note='Two-sided score interval; descriptive over this declared DR distribution, not hardware or >=95% reliability proof.',
                gate_failure_counts=dict(failures),feedback_delay_groups=dict(by_delay),
                valid_physical_result_controls=sum(x['controls']for x in rows),valid_physical_result_physics_steps=sum(x['physics_steps']for x in rows),
                software_prefix_controls_known=sum(x['recorded_prefix_controls']for x in software if x['recorded_prefix_controls']is not None),
                software_prefix_controls_unknown_cases=[x['case']for x in software if x['recorded_prefix_controls']is None],
                software_prefix_physics_steps_known=sum(x['recorded_prefix_physics_steps']for x in software if x['recorded_prefix_physics_steps']is not None),
                software_prefix_physics_steps_unknown_cases=[x['case']for x in software if x['recorded_prefix_physics_steps']is None],
                D0_only_nominal_branches=sum(x['D0_only_nominal_branch']for x in rows),
                ranges={k:span(x[k]for x in rows)for k in('clearance_m','end_stable_s','max_pitch_rad','max_roll_rad','peak_positive_mechanical_power_W')},
                failed_cases=[x['case']for x in rows if not x['passed']],rows=rows,raw_artifact_metadata=raw,
                raw_files_read_or_rehashed=False,new_physics_steps=0,parameters_changed=False,old_H1_H2_H4_modified=False,
                scope='stationary flat operator-timed minihop; original100Hz+D1+D3; operational-air/100Hz-endstable grades only',
                not_qualified=p['not_qualified'],power_allocator_integrated=False,PH5_pending=True)
    dest=R/'reports/H5_MINIHOP_L20_INDEPENDENT_FACTS.json';dump(dest,result)
    rate_line=(f"原门槛通过 **{accepted}/{len(expected)}**（完整冻结holdout）。"if full else
               f"有效物理result通过 **{accepted}/{len(rows)}**；软件错误{len(software)}、未启动{len(batch['unstarted'])}；完整计划率不适用。")
    md=['# H5 独立平地小跳验证','',f"状态：{result['status']}。计划{len(expected)}，执行{batch['executed']}，完整结束{result['complete_episodes']}，软件错误{len(software)}，未启动{len(batch['unstarted'])}。",'',
        rate_line,f"Wilson 95%：{result['wilson95']}（声明DR范围内描述，不是硬件/95%可靠度证明）。",'',
        f"有效物理result耗量：{result['valid_physical_result_controls']}控制采样/{result['valid_physical_result_physics_steps']}物理步。软件prefix已知：{result['software_prefix_controls_known']}控制采样/{result['software_prefix_physics_steps_known']}物理步；未知分别{len(result['software_prefix_controls_unknown_cases'])}/{len(result['software_prefix_physics_steps_unknown_cases'])}例，未知不补配置步数。",'',
        '不按失败更改控制器、不补种、不重跑；原64种子/冻结配置保持。计数中的guide/hard是唯一0.5ms环境接触采样ticks。',
        'operational air为normal总和≤1N连续20ms；100Hz末段稳定不是2k连续支撑。机械正功率不是母线电功率，落地峰值力不是硬件额定证明。','',
        '| Seed | 通过 | D3 µs | clearance m | endstable s | guide/hard ticks | 未过门槛 |','|---:|:---:|---:|---:|---:|---:|---|']
    for x in rows:
        md.append(f"|{x['seed']}|{x['passed']}|{x['feedback_delay_us']}|{x['clearance_m']}|{x['end_stable_s']}|{x['guide_ticks']}/{x['hard_ticks']}|{','.join(x['failed_gates'])}|")
    md+=['','完整结果及producer原始SHA元数据见[JSON](<H5_MINIHOP_L20_INDEPENDENT_FACTS.json>)。本报告只读小result/配置，不重hash大raw。',
         '仍未资格：270mm、RM、移动跳、自动触地FSM、C闭环跳、母线功率、目标板/HIL/WCET/冲击额定。Stage1 V1与旧holdout不改。']
    with(R/'reports/H5_MINIHOP_L20_INDEPENDENT_FACTS.md').open('x',encoding='utf-8')as f:f.write('\n'.join(md)+'\n')
    print(json.dumps({k:v for k,v in result.items()if k not in('rows','raw_artifact_metadata')},indent=2,allow_nan=False))
if __name__=='__main__':main()
