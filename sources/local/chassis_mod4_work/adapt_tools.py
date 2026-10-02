"""Reuse the audited integration machinery, with MOD4-specific contracts."""
from pathlib import Path
import shutil
ROOT=Path(__file__).parent.parent
SRC=ROOT/'rm2025_fixed';OUT=ROOT/'chassis_mod4'
files=['robomaster_env.py','train_ppo.py','view_model.py','isaac/robot_cfg.py','isaac/audit_import.py',
       'isaac/smoke_test.py','tools/export_usd.py','tools/audit_model_parity.py','tools/test_import_guard.py']
for name in files:
    content=(SRC/name).read_text(encoding='utf8').replace('rm2025_fixed','chassis_mod4').replace('rm2025:','mod4:').replace('robot_closed.usda','robot.usd')
    if name=='tools/export_usd.py':
        content=content.replace("'independent_velocity_dofs':12", "'independent_velocity_dofs':m.nv-int(np.linalg.matrix_rank(d.efc_J.reshape(-1,m.nv)[:d.ne],tol=1e-8))")
        content=content.replace('The two fixed-tendon difference limits are redundant on the selected branch: six closures plus CAD knee limits enforce the same bounds. No tendon is silently discarded.',
          'This MOD4 MJCF has no tendons. Identical knee, rocker and slide operating limits are authored in both formats.')
        start=content.index('    # PhysX mimic supports limited revolute joints;')
        end=content.index('    if limits is not None:',start)
        content=content[:start]+content[end:]
    if name=='tools/audit_model_parity.py':
        content=content.replace('-.64,.64','-.49,.49')
        content=content.replace("-manifest['extra_mass']['battery_kg']",'')
        content=content.replace("assert abs(b.mass[0]-0.2019402028967604)<1e-8,'Motor housing mass must not spin with tire'",
           "assert abs(b.mass[0]-manifest['body_masses_kg'][side+'_wheel'])<1e-8, 'Wheel output component mass differs from CAD partition'")
    if name=='tools/test_import_guard.py':content=content.replace('/Robot/links/left_wheel/cad_113','/Robot/links/left_wheel/visual_276')
    if name=='view_model.py':
        content=content.replace('pos3','pos3').replace('v.cam.lookat[:]=[0,0,.26]','v.cam.lookat[:]=[0,0,.28]')
    (OUT/name).write_text(content,encoding='utf8')
for name in ['requirements.txt','requirements-usd.txt','requirements-training.txt']:
    shutil.copyfile(SRC/name,OUT/name)
