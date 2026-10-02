from pathlib import Path
r=Path(__file__).resolve().parent
previous=r.parent/'MOD4_CONTACT_SAMPLING_FIX_20260930'
t=(previous/'mod4_env.py').read_text(encoding='utf-8')
t=t.replace('        if self._contact_eager5ms_enabled:\n            self._install_contact_eager5ms()', '''        integrated = os.environ.get("RM_CONTACT_INTEGRATED", "0") == "1"
        if self._contact_eager5ms_enabled or integrated:
            self._install_contact_eager5ms()
        if integrated:
            from contact_capture import IntegratedWheelContact
            self._integrated_contact = IntegratedWheelContact(self)
            original_update = self.scene.update
            def integrated_update(dt):
                original_update(dt)
                self._integrated_contact.capture(dt)
            self.scene.update = integrated_update
            import json
            print("CONTACT_INTEGRATED_CONFIG " + json.dumps(self._contact_capture_metadata), flush=True)''')
t=t.replace('    def step(self, action):\n', '''    def _reset_idx(self, env_ids):
        super()._reset_idx(env_ids)
        if hasattr(self, "_integrated_contact"):
            self._integrated_contact.reset(env_ids)

    def step(self, action):
        if hasattr(self, "_integrated_contact"):
            self._integrated_contact.begin_control()
''')
compile(t,'mod4_env.py','exec');(r/'mod4_env.py').write_text(t,encoding='utf-8')
t=(r/'mod4_task_baseline.py').read_text(encoding='utf-8')
needle='    f = env.scene.sensors["wheel_contact_scut"].data.net_forces_w_history'
assert t.count(needle)==1
t=t.replace(needle,'''    capture = getattr(env, "_integrated_contact", None)
    f = capture.history if capture is not None else env.scene.sensors["wheel_contact_scut"].data.net_forces_w_history''')
compile(t,'mod4_task.py','exec');(r/'mod4_task.py').write_text(t,encoding='utf-8')
t=(previous/'sampling_pair_probe.py').read_text(encoding='utf-8')
t=t.replace('history_substep=[];height_credit=[];', 'history_substep=[];height_credit=[];bin_history=[];bin_peak=[];bin_impulse=[];bin_off=[];')
t=t.replace('        height_credit.append(task.height_track_both_wheels', '''        if hasattr(env,'_integrated_contact'):
            cap=env._integrated_contact
            bin_history.append(cap.history.clone());bin_peak.append(cap.peak_history.clone())
            bin_impulse.append(cap.impulse.clone());bin_off.append(cap.off_max.clone())
        height_credit.append(task.height_track_both_wheels''')
t=t.replace('columns=np.array(', '''bin_history=torch.stack(bin_history).cpu().numpy() if bin_history else np.empty(0),
        bin_peak=torch.stack(bin_peak).cpu().numpy() if bin_peak else np.empty(0),
        bin_impulse=torch.stack(bin_impulse).cpu().numpy() if bin_impulse else np.empty(0),
        bin_off=torch.stack(bin_off).cpu().numpy() if bin_off else np.empty(0),
        columns=np.array(''')
compile(t,'integrated_probe.py','exec');(r/'integrated_probe.py').write_text(t,encoding='utf-8')
t=(previous/'validate_speed.py').read_text(encoding='utf-8')
t=t.replace("'both_wheels_history_5ms','height_credit_active'", "'both_wheels_history_5ms','both_wheels_binned_mean','height_credit_active'")
t=t.replace('        height_soft=task.height_track(env,sigma=task.SCUT_H_SOFT_SIGMA)', '''        capture=getattr(env,'_integrated_contact',None)
        integrated_history=capture.history if capture is not None else history_active
        both_integrated=(integrated_history.norm(dim=-1).amax(dim=1)>1.).all(dim=1).float()
        height_soft=task.height_track(env,sigma=task.SCUT_H_SOFT_SIGMA)''')
t=t.replace("'height_credit_active':height_soft*both_active,", "'both_wheels_binned_mean':both_integrated,\n                'height_credit_active':height_soft*both_integrated,")
t=t.replace("    strict_5ms=common", "    strict_integrated=common & (per['both_wheels_binned_mean']>=.9)\n    strict_5ms=common")
t=t.replace("        d['strict_pass_window_5ms']=", "        d['strict_pass_integrated_mean']=float(strict_integrated[ids].float().mean())\n        d['strict_pass_window_5ms']=")
t=t.replace("    result['strict_pass_window_5ms']=", "    result['strict_pass_integrated_mean']=result['physics_pass'] and all(g['strict_pass_integrated_mean']>=.8 for g in groups)\n    result['strict_pass_window_5ms']=")
t=t.replace('legacy_gate_preserved_with_corrected_5ms_reporting_20260930','legacy_gate_preserved_with_integrated_and_endpoint_reporting_20260930')
compile(t,'validate_speed.py','exec');(r/'validate_speed.py').write_text(t,encoding='utf-8')
print('All candidate sources compile; integrationflag defaultoff')
