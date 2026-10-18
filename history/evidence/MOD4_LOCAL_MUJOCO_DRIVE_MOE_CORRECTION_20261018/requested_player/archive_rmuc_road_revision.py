"""Archive one local CAD terrain revision, without binary assets or credentials."""
from pathlib import Path
import hashlib,json,shutil,subprocess,time
D=Path(__file__).resolve().parent;repo=D.parent/'polar-rl-train'
dest=repo/'sources/local/MOD4_LOCAL_MUJOCO_DRIVE_20261008'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    marker=D/'RMUC_ROAD_GIT_RECORDED.json'
    if marker.exists():raise RuntimeError('This revision has already been recorded.')
    started=json.loads((D/'INTERACTIVE_STARTED.json').read_text(encoding='utf8'))
    current=json.loads((D/'INTERACTIVE_CURRENT.json').read_text(encoding='utf8'))
    assert started['viewer_running'] and current['finite'] and current['pid']==started['pid']
    query=f"Get-CimInstance Win32_Process -Filter 'ProcessId={started['pid']}' | Select-Object ProcessId,ParentProcessId,CreationDate,CommandLine | ConvertTo-Json"
    p=subprocess.run(['powershell','-NoProfile','-Command',query],check=True,capture_output=True,encoding='utf8')
    identity=json.loads(p.stdout);assert str(D/'drive_latest.py') in identity['CommandLine']
    opened=dict(epoch=time.time(),identity=identity,started=started,telemetry=current,terrain_npz_sha256=sha(D/'terrain.npz'))
    (D/'RMUC_GUI_OPENED_REVIEW.json').write_text(json.dumps(opened,ensure_ascii=False,indent=2),encoding='utf8')
    receipt=json.loads((D/'RMUC_ROAD_BUILD_RECEIPT.json').read_text(encoding='utf8'))
    if 'terrain_npy_sha256' in receipt:receipt['terrain_npz_sha256']=receipt.pop('terrain_npy_sha256')
    (D/'RMUC_ROAD_BUILD_RECEIPT.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2),encoding='utf8')
    index=dict(epoch=time.time(),local_only=True,remote_training_untouched=True,
               previous_local_trial='trial-20261009-latest30900-local-mujoco-wasd-and-mild-terrain-opened',
               binary_artifacts_only_sha={n:sha(D/n) for n in ['model_30900.pt','model_30900.onnx','terrain.npz','RMUC_ROAD_PREVIEW.png']},
               original_playground_sha=sha(D/'original_mild_playground/playground.xml'),
               original_heightfields_sha=sha(D/'original_mild_playground/terrain.npz'),
               source_CAD_collision_sha=receipt['source_collision_sha256'])
    (D/'RMUC_ROAD_REVISION_INDEX.json').write_text(json.dumps(index,indent=2),encoding='utf8')
    names=['add_rmuc_road.py','review_rmuc_road.py','drive_latest.py','playground.xml','README.md',
           'RMUC_ROAD_BUILD_RECEIPT.json','RMUC_ROAD_SMOKE_REVIEW.json','RMUC_GUI_OPENED_REVIEW.json','RMUC_ROAD_REVISION_INDEX.json']
    dest.mkdir(exist_ok=True,parents=True)
    for n in names:shutil.copyfile(D/n,dest/n)
    note='''User asked to match the local WASD playground's uneven road to RoboMaster. Rebuilt a standalone 10-bump lane from the user's RMUC2026_V2.0.0 CAD collision triangles, using vertical rays and a 5 mm x 10 mm heightfield, rather than a convex mesh hull or an enlarged sine wave. Nominal bumps are 70 mm high with 240 mm pitch, matching the official 2026 V1.2 rulebook figure 4-36. Actual sampled maximum is 71.023615 mm; centerline peaks are 69.409626-69.939863 mm, peak spacings 230-245 mm. No height rescaling to hide CAD/grid differences. This is the supplied V2.0 isolated road, not an asserted match to later V2.2 CAD. Rigidly leveled the original field's 1.5 degree base slope; full arena grading is not reproduced.

Retained the original 25 mm road as a purple practice lane, the original 80 mm blue ramp, and the exact downloaded model30900/ONNX actor. XML robot, solver, actuator and equality subtrees are unchanged; 31 robot bodies, 6 actuators and 10 equalities pass the existing parameter readback. 245 MuJoCo vertical rays match sampled terrain within 1e-6 m. A separate noncolliding floor visual at -0.2 mm removes coplanar display artifacts while the collision floor remains at zero.

Actual unchanged-policy MuJoCo observations do NOT show stable road completion: at 0.3 m/s requested speed, 18 simulated seconds advances 1.563517 m, still on the road; at 0.5 m/s it leaves the 2 m wide lane laterally after 7.19 seconds at x2.440579/y1.004121 m. Both remain finite and upright, without yaw or stabilization assistance. Preserved these incomplete traversals explicitly, not as an RM skills pass. Rendered and visually inspected the actual heightfield. Opened the updated local Tk/MuJoCo driver and verified fresh PID identity, live viewer and finite telemetry. Keys 2/4 select RM road and original mild road; WASD, stop, reset and speed controls remain available.

No remote training, evaluator, checkpoint selection, physics parameter or budget change. Checkpoint, ONNX, heightfields, preview and CAD binaries remain local, with SHA references only in Git. Original scene and previous observations are preserved in original_mild_playground. This is local sim-to-sim play and observed limitations, not Isaac graduation or hardware certification.
'''
    (D/'RMUC_ROAD_EXPERIMENT_NOTE.md').write_text(note,encoding='utf8')
    (D/'RMUC_ROAD_RECORD_INPUT.json').write_text(json.dumps(dict(files=[str((dest/n).relative_to(repo)).replace('\\','/') for n in names],note_file=str(D/'RMUC_ROAD_EXPERIMENT_NOTE.md')),indent=2),encoding='utf8')
    print(json.dumps(dict(file_count=len(names),gui_pid=started['pid'],archive_ready=True)))
if __name__=='__main__':main()
