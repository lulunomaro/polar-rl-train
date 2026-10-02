from pathlib import Path
root=Path(__file__).parent
source=root.parent/'mod4_scut_continue10h_20260929/validate_rescue_remote_audited.py'
s=source.read_text(encoding='utf8')
start=s.index('    # 2026-09-29 门禁对齐')
end=s.index('    # 2026-09-29 追加',start)
s=s[:start]+'''    # Window semantics mirror the upstream reward, but our observed lazy-sensor
    # sampling cadence is 10 ms, not the configured 5 ms. Neither gate is a contest standard.
    common=alive & (counts>0) & (per['vel_error']<=torch.maximum(torch.full_like(targets,.12),targets*.25)) & (per['tilt']<=8) & (per['height_error']<=.03) & (per['delta']<=.18) & (per['d2']<=.25)
    strict=common & (per['both_wheels_scut_history']>=.9)
    strict_instant=common & (per['both_wheels']>=.9)
'''+s[end:]
s=s.replace("d['fail_counts']={k:int((~m & validrows).sum()) for k,m in crit.items()}","d['fail_counts']={k:int((~m & (ids if k in ['alive','sampled'] else validrows)).sum()) for k,m in crit.items()}\n        d['strict_pass_window']=d['strict_pass']\n        d['strict_pass_instant_legacy']=float(strict_instant[ids].float().mean())")
s=s.replace("'scut_contact_window':'per-wheel peak over 3 samples at 5ms; diagnostic only; strict gate unchanged',", "'gate_version':'window_contact_v2_dual_reporting_20260929',\n            'scut_contact_window':{'semantics':'per-wheel peak over 3 samples >1N; not simultaneous continuous loading','configured_update_period_s':.005,'actual_update_interval_s_prior_measured':.01,'prior_evidence':'contact_substep_diagnostic.json'},")
s=s.replace("    Path(args.output).write_text", "    result['strict_pass_window']=result['strict_pass']\n    result['strict_pass_instant_legacy']=result['physics_pass'] and all(g['strict_pass_instant_legacy']>=.8 for g in groups)\n    Path(args.output).write_text")
(root/'validate_rescue.py').write_text(s,encoding='utf8')
