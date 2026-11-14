"""Record this bounded replay task and its complete SCUT PT through the established helper."""
from pathlib import Path
import subprocess,sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
HELPER=ROOT.parent/'tmp/step7_archive_helper/record_experiment.py'
sys.path.insert(0,str(HELPER.parent))
source=HELPER.read_text(encoding='utf-8')
# User explicitly requires actual PT bodies in Git; allow only this task's weights.
old="if file.suffix.lower() in ('.pt','.pth','.onnx','.npz','.npy','.pem','.key'):"
new="if file.suffix.lower() in ('.pt','.pth','.onnx','.npz','.npy','.pem','.key') and not (file.suffix.lower()=='.pt' and file.is_relative_to(ROOT/'sources/local/SCUT_ORIGINAL_MUJOCO_ROUGH_20261115/weights')):"
assert old in source
source=source.replace(old,new)
source=source.replace("git('add','--',","git('add','-f','--sparse','--',")
source=source.replace("['git','-C',str(ROOT),*args]", "['git','-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true','-C',str(ROOT),*args]")
files=[HERE/'scut_backend.py',HERE/'scut_player.py',HERE/'open_best_mod4.py',HERE/'archive_result.py',HERE/'README.md',HERE/'.gitignore',HERE/'启动华南虎MuJoCo.cmd']
files+=list((HERE/'reference').glob('*'))+list((HERE/'weights').glob('*.pt'))
files+=[p for p in (HERE/'evidence').iterdir() if p.is_file() and p.name not in ('player_r2.stdout.log','player_r2.stderr.log','best_mod4.stdout.log','best_mod4.stderr.log','full_map.log')]
branch=subprocess.check_output(['git','-C',str(ROOT),'branch','--show-current'],text=True).strip()
def remote(*refs):
    return subprocess.check_output(['git','-c','http.proxy=http://127.0.0.1:7897','-c','http.sslVerify=true','-C',str(ROOT),'ls-remote','origin',*refs],text=True).strip()
main_before=remote('refs/heads/main')
sys.argv=[str(HELPER),'--id','scut-original-mujoco-wasd-best-comparison-01','--title','Original SCUT WASD MuJoCo terrain playback and frozen MOD4 comparison','--kind','evaluation','--note-file',str(HERE/'README.md'),'--validation','Original35/6 actor and published sim2sim plant; three8s runs no resets, max closure0.441mm; actual Space UI request observed; jump flight not demonstrated; two player/control window pairs present; SCUT preserved; no training changes.','--files',*[str(p.relative_to(ROOT)).replace('\\','/') for p in files],'--push']
exec(compile(source,str(HELPER),'exec'),{'__name__':'__main__','__file__':str(HELPER)})
head=subprocess.check_output(['git','-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()
tag='trial-20261115-scut-original-mujoco-wasd-best-comparison-01'
refs=remote('refs/heads/'+branch,'refs/heads/main','refs/tags/'+tag,'refs/tags/'+tag+'^{}')
assert remote('refs/heads/main')==main_before
assert head+'\trefs/heads/'+branch in refs
assert head+'\trefs/tags/'+tag+'^{}' in refs
print('ARCHIVE_REMOTE_VERIFIED',refs,sep='\n')
