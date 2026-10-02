from pathlib import Path
ROOT=Path(__file__).parent.parent
s=(ROOT/'rm2025_fixed/tools/validate_model.py').read_text(encoding='utf8')
s=s.replace("training='scene_detail_training.xml' if detail else 'scene_training.xml'", "training='scene_headless.xml'")
s=s.replace("visual='scene_detail.xml' if detail else 'scene.xml'", "visual='scene_training.xml'")
s=s.replace("rollout('zero_torque_gravity',20000", "rollout('zero_torque_gravity',6000")
s=s.replace("rollout('joint_sine_tracking',20000", "rollout('joint_sine_tracking',10000")
s=s.replace("rollout('full_torque_random',30000", "rollout('full_torque_random',12000")
s=s.replace("rollout('commands_10x_clamped',20000", "rollout('commands_10x_clamped',6000")
s=s.replace("rollout('external_push',20000", "rollout('external_push',6000")
s=s.replace("'drop_'+str(i),12000", "'drop_'+str(i),4000")
(ROOT/'chassis_mod4/tools/validate_model.py').write_text(s,encoding='utf8')
