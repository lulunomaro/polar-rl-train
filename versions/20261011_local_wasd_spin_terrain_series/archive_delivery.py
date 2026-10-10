"""Capture this local-only deployment and every saved report, with binary indexes."""
from pathlib import Path
import hashlib,json,shutil,time,xml.etree.ElementTree as ET

D=Path(__file__).resolve().parent;W=D.parent;R=W/'polar-rl-train'
V=R/'versions/20261011_local_wasd_spin_terrain_series'
E=R/'history/evidence/MOD4_LOCAL_WASD_SERIES_20261011'
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
    return h.hexdigest()
def main():
    if E.exists():raise RuntimeError('Already archived; supplement new reports without rerecording.')
    frame=json.loads((D/'CHASSIS_FRAME_SERIES_REVIEW.json').read_text(encoding='utf8'))
    ui=json.loads((D/'UI_SWITCH_REVIEW.json').read_text(encoding='utf8'))
    assert frame['all_signed_directions_correct'] and frame['all_trials_finite'] and not frame['local_falls']
    assert ui['all_passed']
    (D/'ATTEMPTS_AND_REPAIRS.json').write_text(json.dumps(dict(epoch=time.time(),attempts=[
        dict(id='local-inventory-access-denied',status='reader error',detail='Initial broad workspace rg --files met an unrelated unpack_verify directory permission error; targeted reads succeeded; no mutation.'),
        dict(id='local-player-old-entry-name',status='reader lookup missing',detail='Guessed play.py did not exist; existing drive_latest.py was read. No execution.'),
        dict(id='local-selected-source-glob-invalid',status='reader error',detail='Windows literal SELECT* argument to rg produced OS123; corrected target directory and exact D7_D9_RAW_SHA_INDEX selected31903.'),
        dict(id='local-profile-guessed-path-missing',status='reader lookup missing',detail='Guessed new35mm_cpu profile path missing; resolved payload/g3_cad_profile.json. No remote mutation.'),
        dict(id='local-build-syntax-rejected',status='pre-execution SyntaxError',source='build_local_series_syntax_rejected.py',detail='Missing space in else 4.5 conditional rejected before build; source preserved and corrected standalone builder completed once.'),
        dict(id='old-local-player-telemetry-winerror5',status='previous actual crash retained',source=str(W/'MOD4_LOCAL_MUJOCO_DRIVE_20261008/INTERACTIVE_ERROR.txt'),repair='New unique temporary file, three bounded atomic replacement attempts, nonfatal current telemetry. Actual Windows file sharing lock tested.'),
        dict(id='local-inertial-frame-telemetry-reader',status='original readings retained',source='LOCAL_SMOKE_REVIEW.json',source_code='drive_series_inertial_telemetry_original.py',detail='mjOBJ_BODY local velocities refer to principal inertial axes, not regular chassis frame. Incorrect low/opposite velocity readings were a reader error. Actual positions/physics unchanged.',repair='mjOBJ_XBODY matches base_gyro site angular values within1e-8; independent seven signed-spin cases and signed straight checks saved separately.'),
    ],production_GPU_PPO_changes=0,canonical_changes=0),ensure_ascii=False,indent=2),encoding='utf8')
    started=json.loads((D/'INTERACTIVE_STARTED.json').read_text(encoding='utf8'));current=json.loads((D/'INTERACTIVE_CURRENT.json').read_text(encoding='utf8'))
    assert current['finite'] and current['fault'] is None and started['pid']==current['pid']
    receipt=dict(epoch=time.time(),human_request='拉到本地wasd操控，记得加上小陀螺系列和地形系列',player_started=started,player_current_capture=current,UI_checks_passed=True,spin_series=frame['trials'],scene_count=12,learned_MoE_gate=False,nominal_MuJoCo_only=True,trained_CURB_SLOPE_STAIR_models_available=False,remote_mutations=0,training_changes=0,budget_changes=0,desktop_shortcut=str(W.parents[1]/'MOD4-WASD 小陀螺与地形.lnk'))
    (D/'DELIVERY_REVIEW.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
    V.mkdir(parents=True);E.mkdir(parents=True)
    entries=[];large=[]
    for src in sorted(D.rglob('*')):
        if not src.is_file() or '__pycache__' in src.parts or src.name=='driver.lock' or src.suffix=='.tmp':continue
        relative=src.relative_to(D)
        # Freeze dynamic status to a single exact captured byte sequence.
        raw=src.read_bytes();digest=hashlib.sha256(raw).hexdigest()
        info=dict(source_path=str(src),bytes=len(raw),source_sha256=digest)
        if src.suffix.lower() in ('.pt','.pth','.npz','.npy','.onnx','.png','.lnk'):
            large.append(dict(**info,archive_mode='external actual path-size-SHA; original retained'))
            continue
        parent=V if src.suffix.lower() in ('.py','.bat','.xml') or relative.parts[0]=='src_snapshot' or src.name in ('runtime_config.json','SERIES.json','g3_cad_profile.json','README.md') else E
        dest=parent/relative;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        assert sha(dest)==digest
        entries.append(dict(**info,archive_path=dest.relative_to(R).as_posix(),archive_sha256=digest,archive_mode='full exact bytes',captured_epoch=time.time()))
    # Index every existing mesh dependency referenced by the actual local XML.
    root=ET.parse(D/'scenes/flat.xml').getroot();meshdir=Path(root.find('compiler').get('meshdir'))
    for mesh in root.find('asset').findall('mesh'):
        src=meshdir/mesh.get('file');assert src.exists()
        large.append(dict(source_path=str(src),bytes=src.stat().st_size,source_sha256=sha(src),archive_mode='external reused CAD mesh; original retained'))
    old=W/'MOD4_LOCAL_MUJOCO_DRIVE_20261008/INTERACTIVE_ERROR.txt'
    dest=E/'PREVIOUS_LOCAL_PLAYER_INTERACTIVE_ERROR.txt';shutil.copyfile(old,dest)
    entries.append(dict(source_path=str(old),bytes=old.stat().st_size,source_sha256=sha(old),archive_path=dest.relative_to(R).as_posix(),archive_sha256=sha(dest),archive_mode='full old failure retained'))
    index=dict(epoch=time.time(),entries=entries,large_artifacts=large,all_saved_current_delivery_reports_captured=True,credentials_archived=False,remote_training_changes=0,canonical_changes=0)
    (E/'REPORT_CAPTURE_INDEX.json').write_text(json.dumps(index,ensure_ascii=False,indent=2),encoding='utf8')
    note='''Human requested local WASD playback with spin and terrain series. Downloaded exact frozen E0/D7 b109, reviewed terrain3c97 and unqualified independent Wave2b4 checkpoints, retaining full originals and SHA indexes. Built a separate nominal MuJoCo player, direct CPU deterministic saved actor, process-focused WASD, seven signed spin presets, twelve explicit terrain scenes, reverse entry, reset/pause/camera and manual model choice. No learned gate or qualified CURB/SLOPE/STAIR weights are claimed. Full robot import contract/31 bodies/6 actuators/10 constraints/100Hz nominal PD and hardware envelope retained; local0.5ms solver is not PhysX or full DR reproduction.

All scenes loaded finite. Local spin1/2/4/6/8/10/4pi both directions and signed straight checks passed finite/direction checks; tracking residuals retained (4pi tail+12.8297/-12.7529, straight+1.6601/-1.691 for target±1.5). Local wave35 both directions and curb20 up/down completed requested test windows without falls; no remote terrain graduation inferred. Actual Tk/MuJoCo viewer model switch/scene rebuild/reverse/pause checks passed and human player launched.

Preserved initial builder SyntaxError and reader inventory/path/glob failures. Previous local telemetry WinError5 crash retained; actual Windows sharing-lock test confirms bounded nonfatal replacement and recovery. Preserved original principal-inertia-frame telemetry and original runtime source; corrected XBODY chassis telemetry independently matched site gyro within1e-8. This corrected a reader, not physics or policy. Every saved report/source/config/preview and trajectory has a full-byte archive or true external path-size-SHA index. No remote training/evaluator, approved plan, monitor or canonical budget mutations.'''
    (E/'STAGE_NOTE.md').write_text(note,encoding='utf8')
    print(json.dumps(dict(full_files=len(entries),large_indices=len(large),evidence=str(E),version=str(V))))
if __name__=='__main__':main()
