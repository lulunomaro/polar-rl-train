from pathlib import Path
import sys,json,time,hashlib,shutil,traceback,xml.etree.ElementTree as ET
import numpy as np

D=Path(__file__).resolve().parent;W=D.parent;R=D/'reports';R.mkdir(exist_ok=True)
OLD=W/'MOD4_LOCAL_WASD_SERIES_20261011'
sys.path.insert(0,str(W/'MOD4_E1_WAVE50_ROUTE_SECOND_BOUNDED_20261012'))
from route_second_io import io
SOURCE='/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_STARTUP_RESOURCE_REVIEWED_20261012/learning_logs/2026-10-12_16-39-25_e1_WAVE50_route_startup_resource_reviewed_observation_1791794169327149016'
SHA='7facab0a45ccc7589123488deb98c77e9980a8f9d124b1cea3843ccbe16a5de9'
def H(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def save(name,value):
 p=R/name;assert not p.exists();p.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf8');return p

def main():
 assert not (R/'BUILD_ACTUAL.json').exists() and not (D/'DOWNLOAD_RECEIPT.json').exists()
 save('HUMAN_WASD50_70_REQUEST.json',dict(epoch=time.time(),human_text='把最新检查点拉到wasd操控里让我试试50mm地形和70mm地形通过性',scope='local frozenactor manual WASD only',source_SHA=SHA,no_new_remote_PPO_or70mm_qualification_authority=True))
 (D/'models').mkdir();(D/'scenes').mkdir();(D/'src_snapshot').mkdir()
 n,w=io.connect_both()
 try:
  with n.open_sftp() as f:
   latest=json.loads(f.open(SOURCE+'/latest_complete.json','rb').read());assert latest['checkpoint']==SOURCE+'/model_32352.pt' and latest['pid']==3374665
   proof=json.loads(f.open('/home/egde/rl_candidates/MOD4_S3_E1_WAVE50_ROUTE_STARTUP_RESOURCE_REVIEWED_20261012/reports/INDEPENDENT_POSTEXIT_FULLSTATE_CPU_ACTUAL.json','rb').read());assert proof['passed'] and proof['closeout_ready'] and proof['own_checkpoint']['sha256']==SHA and proof['actual_source_count']==449 and proof['actual_finite_tensor_count']==107
   cp=D/'models/model_32352_7fac_wave50.pt';f.get(latest['checkpoint'],str(cp));assert cp.stat().st_size==18701417 and H(cp)==SHA
   manifest=json.loads(f.open(SOURCE+'/run_manifest.json','rb').read());profile=f.open(SOURCE+'/src_snapshot/g4_cad_profile.json','rb').read();assert hashlib.sha256(profile).hexdigest()==manifest['src_sha256']['g4_cad_profile.json']
   (D/'g4_cad_profile.json').write_bytes(profile)
  receipt=dict(epoch=time.time(),models=[dict(id='wave449',label='最新起伏模型 · 449 / 32352 / 7fac',status='50mm正式评测：正13/27、倒23/27；70mm未训练，手动仿真测试',sha256=SHA,path=latest['checkpoint'],local_path=str(cp),bytes=cp.stat().st_size,local_sha256=H(cp))],remote_mutations=0,canonical_mutations=0,local_frozen_CPU_actor_only=True,original_449_supervisor_failure_and_independent_closeout_disclosed=True)
  (D/'DOWNLOAD_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
  save('MODEL_DOWNLOAD_ACTUAL.json',dict(**receipt,profile_SHA=H(D/'g4_cad_profile.json'),source_actual_fullsave_proof=proof))
 finally:io.cleanup(n,w)
 inputs=[]
 for name in ('sim_runtime.py','series_sim.py','policy_runtime.py','io_runtime.py','runtime_config.json'):
  src=OLD/name;shutil.copy2(src,D/name);inputs.append(dict(source=str(src),bytes=src.stat().st_size,sha256=H(src)))
 for name in ('reset_bank.json','import_contract.json'):
  src=OLD/'src_snapshot'/name;shutil.copy2(src,D/'src_snapshot'/name);inputs.append(dict(source=str(src),bytes=src.stat().st_size,sha256=H(src)))
 series=(D/'series_sim.py').read_text();assert "if kind in ('wave','rm70'):x=-x;yaw=math.pi" in series
 series=series.replace("scene_id='flat',model_id='e0'", "scene_id='wave50',model_id='wave449'").replace("if kind in ('wave','rm70'):x=-x;yaw=math.pi", "if kind in ('wave','rm70'):x=-x # Keep heading; S tests actual backwards motion")
 (D/'series_sim.py').write_text(series,encoding='utf8')
 drive=(OLD/'drive_series.py').read_text()
 drive=drive.replace("self.root.title('MOD4 · WASD / 小陀螺 / 地形系列')", "self.root.title('MOD4 · 最新32352 · 50/70mm起伏 WASD')")
 drive=drive.replace("scene='flat';model='e0'", "scene=SERIES['scenes'][0]['id'];model=MODELS[0]['id']")
 drive=drive.replace('反向起点 / 下行（切换会复位）','另一端起点（保持朝向，用 S 倒退）')
 start=drive.index("        ttk.Label(f,text='起伏：10 / 20 / 35 mm")
 end=drive.index("        self.root.protocol",start)
 drive=drive[:start]+"        ttk.Label(f,text='默认 50mm，同源全十波；F 切换 70mm / 平地。\\nW 正向；选另一端起点后用 S 倒退。R 复位，空格停车。\\n50/70mm 是峰谷高差，70mm 为同源派生测试档，尚未训练。\\n本地名义 MuJoCo 适配与远端 PhysX 正式评测分开记录。',wraplength=660,font=('Microsoft YaHei UI',9)).pack(anchor='w',pady=10)\n"+drive[end:]
 (D/'drive_series.py').write_text(drive,encoding='utf8')
 for name in ('sim_runtime.py','series_sim.py','policy_runtime.py','io_runtime.py','drive_series.py'):compile((D/name).read_bytes(),str(D/name),'exec')
 profile=json.loads((D/'g4_cad_profile.json').read_bytes());px=np.asarray(profile['profile_x_m']);pz=np.asarray(profile['normalized_height']);span=profile['span_m']
 base=ET.parse(OLD/'scenes/wave35.xml').getroot();base.set('model','MOD4 local latest checkpoint waveform comparison');base.find('compiler').set('meshdir',(W/'chassis_mod4/assets').as_posix())
 fields={};scenes=[]
 for mm in (50,70):
  root=ET.fromstring(ET.tostring(base));hf=root.find('asset').find('hfield');hf.set('name','wave'+str(mm));hf.set('size',f'4.5 1 {mm/1000} .05')
  geom=root.find('worldbody').find("geom[@name='terrain']");geom.set('hfield','wave'+str(mm));geom.set('rgba','.24 .56 .48 1' if mm==50 else '.64 .48 .22 1')
  xs=np.linspace(-4.5,4.5,9001);normalized=np.interp(xs+span/2,px,pz,left=0,right=0);fields['wave'+str(mm)]=np.tile(normalized,(3,1)).astype(np.float32)
  dense=np.linspace(-span/2,span/2,20001);expected=np.interp(dense+span/2,px,pz)*(mm/1000);actual=np.interp(dense,xs,fields['wave'+str(mm)][0])*(mm/1000)
  path=D/'scenes'/('wave'+str(mm)+'.xml');ET.ElementTree(root).write(path,encoding='utf8',xml_declaration=True)
  scenes.append(dict(id='wave'+str(mm),label=f'起伏 {mm} mm · 同源全十波'+(' / 最新模型测试' if mm==50 else ' / 未训练试玩'),kind='wave',height=mm/1000,spawn=[-span/2-.4,0,0],span=span,period=profile['period_m'],scope='CAD-derived peak-to-trough comparison; not whole RM arena',xml=str(path),local_sampling_max_vertical_error_m=float(abs(expected-actual).max()),sampled_peak_to_trough_m=float(np.ptp(fields['wave'+str(mm)])*(mm/1000)),root_approach_m=.4))
 flat=ET.parse(OLD/'scenes/flat.xml').getroot();flat.find('compiler').set('meshdir',(W/'chassis_mod4/assets').as_posix());fp=D/'scenes/flat.xml';ET.ElementTree(flat).write(fp,encoding='utf8',xml_declaration=True)
 scenes.append(dict(id='flat',label='平地 · 本模型对照',kind='flat',height=0,spawn=[0,0,0],xml=str(fp)))
 np.savez_compressed(D/'terrain.npz',**fields)
 (D/'SERIES.json').write_text(json.dumps(dict(scenes=scenes,spin_rad_s=[1,2,4,6,8,10,4*np.pi],spin_labels=['1','2','4','6','8','10','4π'],learned_gate=False),ensure_ascii=False,indent=2),encoding='utf8')
 (D/'START_WASD.bat').write_text('@echo off\nchcp 65001 >nul\ncd /d "%~dp0"\nset PYTHONUTF8=1\n"%~dp0..\\.venv\\Scripts\\pythonw.exe" "%~dp0drive_series.py"\n',encoding='utf8')
 (D/'README.md').write_text('''# 最新检查点 WASD：50mm / 70mm 起伏

默认使用本轮449的最终model32352，SHA7facab0a…；50mm正式评测正13/27、倒23/27，仍未合格。70mm尚未训练。

W/S前后、A/D转向；空格停车，R复位，F换地形。默认50mm，地形下拉框可选70mm、平地。勾选“另一端起点”后保持车头朝向，用S测试倒退通过。失去播放器焦点立即归零。

50/70mm均是峰谷高差，使用本轮同源CAD全十波2.406422727m，前方根接近0.4m、两端平支撑。70mm是同源派生测试档，不能当作真实RM整场/CAD全路线验收。本地为名义MuJoCo0.5ms物理、100Hz冻结actor35→6直接CPU推理；原robot31体/6驱动/10约束和硬件包络保留，无optimizer、动作混合、教师或航向纠偏。未复刻PhysX和全部D0D7 DR，试玩结果与正式153评测分开记录。

双击START_WASD.bat重新打开。本目录独立于昨天播放器；不修改4090/3060训练、预算或旧源码。
''',encoding='utf8')
 save('BUILD_ACTUAL.json',dict(epoch=time.time(),passed=True,source_model_SHA=SHA,old_runtime_inputs=inputs,scenes=scenes,profile_SHA=H(D/'g4_cad_profile.json'),terrain_SHA=H(D/'terrain.npz'),only_local_actor_manual_player_no_training=True,old_player_source_not_modified=True,default_scene='wave50',default_model='wave449',backwards_start_keeps_heading_and_uses_S=True,teacher=False,yaw_assist=False,local_MuJoCo_not_PhysX_exact=True,no_original_RM70mm_fullcourse_qualification_claim=True))
 print(json.dumps(dict(passed=True,model=str(cp),SHA=SHA,scenes=[s['id'] for s in scenes])))

if __name__=='__main__':
 try:main()
 except BaseException:save('BUILD_ERROR_'+str(time.time_ns())+'.json',dict(error=traceback.format_exc(),no_blind_repull_overwrite_or_remote_training_mutation=True));raise
