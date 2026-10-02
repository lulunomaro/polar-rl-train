from pathlib import Path
p=Path(__file__).parent
s=(p/'tui_before_speed.py').read_text(encoding='utf8')
s=s.replace("    if state.get('stage') in ('training', 'final_evaluation', 'finished', 'attention_required'):","    if state.get('stage') in ('training', 'checkpoint_handover', 'final_evaluation', 'finished', 'attention_required'):")
s=s.replace("    ck = state.get('latest_checkpoint')", "    if state.get('speed_limit_m_s'):\n        status.append(f\"\\n速度指令 ±{state['speed_limit_m_s']:g} m/s；10% 站立；DR 关闭；达标后逐级提速\", style='bold green')\n    ck = state.get('latest_checkpoint')")
s=s.replace("f\"{group.get('command_vx', 0):.1f}\",", "f\"{group.get('command_vx', 0):.1f}\" + ('↔' if group.get('profile')=='ramp_brake_reverse' else ''),")
s=s.replace("    return Panel(Group(table, Text(' '), summary)","    if report.get('ramp_suite'):\n        summary.append('\\n↔为加速/刹停/反向轨迹；该行实速是全轨迹有符号均值，不是峰值。',style='yellow')\n    return Panel(Group(table, Text(' '), summary)")
compile(s,'tui_rescue.py','exec')
(p/'tui_speed.py').write_text(s,encoding='utf8')
