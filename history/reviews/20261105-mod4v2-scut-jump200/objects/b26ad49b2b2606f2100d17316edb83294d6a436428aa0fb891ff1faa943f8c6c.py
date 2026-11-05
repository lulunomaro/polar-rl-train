"""Scoped text/evidence archival; binaries indexed, no PT decode or simulation."""
from pathlib import Path
import hashlib,json,sys,time

ROOT=Path(__file__).resolve().parent
G=Path('C:/Users/lulu/Desktop/claude/mjcf/polar-rl-train')
DEST=G/'history/reviews/20261105-mod4v2-scut-jump200'
OLD=ROOT.parent/'mod4v1_scut_step270_2h_20261103/env20000_jump200_tuck_retraction_1h_20261105'
sys.path.insert(0,str(G/'archive_tools'))
from capture_history import redact
H=lambda raw:hashlib.sha256(raw).hexdigest()

if __name__=='__main__':
    DEST.mkdir(exist_ok=True);(DEST/'objects').mkdir(exist_ok=True)
    paths=[p for base in [ROOT,OLD]for p in base.rglob('*')if p.is_file()and p.suffix.lower()in ['.py','.md','.json','.log','.txt']and '__pycache__'not in p.parts]
    paths += [ROOT.parents[1]/'admin/CURRENT_STATE.json',G.parent/'AGENTS.md',G/'AGENTS.md',
        Path('C:/Users/lulu/.codex/automations/mod4-10/automation.toml'),Path('C:/Users/lulu/.codex/automations/mod4-200-rl-bptt/automation.toml')]
    rows=[]
    for p in sorted(set(paths)):
        raw=p.read_bytes();text=raw.decode('utf8');transform=None
        if p.name in ('POSTROUND_FULL_RETURNED.json','FULL_RETURNED.json','RECOVERED_COMPLETE_RETURNED.json'):
            v=json.loads(raw)
            if 'evaluation/CONTROL_CURVES.json'in v.get('files',{}):
                v['files']['evaluation/CONTROL_CURVES.json']=dict(external_large_raw=True,path=str(p),
                    bytes=len(raw),SHA=H(raw),json_pointer='/files/evaluation~1CONTROL_CURVES.json')
                text=json.dumps(v,indent=2);transform='OnlyCONTROL_CURVESexternalized'
        if p == ROOT/'shared_control_access.py' and text.endswith('\n\n'):
            # Keep the running source frozen and its original SHA in the index.
            # Only omit its redundant final blank line from the Git text object.
            text=text.rstrip('\r\n')+'\n';transform='OnlyRedundantBlankAtEOFRemovedOriginalPreserved'
        text,count=redact(text);data=text.encode();target=DEST/'objects'/(H(data)+p.suffix.lower())
        if not target.exists():target.write_bytes(data)
        rows.append(dict(path=str(p),bytes=len(raw),SHA=H(raw),git_path=target.relative_to(G).as_posix(),
            archived_SHA=H(data),redactions=count,transform=transform))
    receipts = list(OLD.glob('reports/*TRANSFERS.json')) + list(ROOT.rglob('*TRANSFERS.json'))
    for receipt in receipts:
        for row in json.loads(receipt.read_bytes()).get('files',[]):
            if row.get('local_path'):
                rows.append(dict(path=row['local_path'],bytes=row['bytes'],SHA=row['SHA'],
                    external_artifact=True,source_receipt=str(receipt),archive_model_reads=0))
    render_reports = list(OLD.glob('evaluation/**/RENDER_REPORT.json')) + list(ROOT.rglob('RENDER_REPORT.json'))
    for report in render_reports:
        for name in json.loads(report.read_bytes()).get('media',[]):
            p=Path(name);rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA=H(p.read_bytes()),
                external_artifact=True,actual_saved_pose_render=True))
    hw=ROOT/'attempt02/hardware/assets/robot.usd'
    if hw.exists():rows.append(dict(path=str(hw),bytes=hw.stat().st_size,SHA=H(hw.read_bytes()),
                                  external_artifact=True,kind='USDcompositionlayer'))
    for p in ROOT.glob('*.usda'):
        rows.append(dict(path=str(p),bytes=p.stat().st_size,SHA=H(p.read_bytes()),
                         external_artifact=True,kind='USDcompositionlayer'))
    (DEST/'EVIDENCE_INDEX.json').write_text(json.dumps(dict(captured_epoch=time.time(),files=rows,
        model_deserializations=0,physics=0),indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(dict(files=len(rows),destination=str(DEST))))
