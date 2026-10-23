from pathlib import Path
import ast, hashlib, json, time

D=Path(__file__).resolve().parent;T=D.parent;R=D/'reports'
P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V43_20261023'
N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V44_20261023'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def put(p,v):
    with p.open('x',encoding='utf8') as f:json.dump(v,f,ensure_ascii=False,indent=2)

def main():
    proof=json.loads((P/'reports/H1_ONLY_COMPLETE_MODEL_ORIGINAL_COST_CPU_ACTUAL.json').read_bytes());assert proof['passed']
    correction=dict(epoch=time.time(),original_error_preserved=True,corrected_scope='The original manifest SHA/size and the later transferred complete log bytes/SHA are retained. The original manifest-time log byte content was not captured and cannot be reconstructed. The fresh one-read log SHA equals the first transferred log SHA.',original_manifest_SHA='e3e16e5d90a481d11082f39c74860232e3def181752cc23b5487164f189b368b',actual_transferred_and_fresh_SHA='67d9f568651a25a39323deeac16f609cad9b3033f66844c911b176bce964684a',original_manifest_time_bytes_unavailable=True,corrects_original_report_phrase='two byte versions retained',cause_unknown=True,no_training_failure_refund_or_recharge_inferred=True)
    put(R/'CLOSED43_LOG_TWO_SHA_VERSUS_AVAILABLE_BYTES_SCOPE_CORRECTION_ACTUAL.json',correction)
    target=N/'collect_selected_H1_final_unused_once.py'
    assert not (N/'reports/H1_ONLY_CLOSING_STARTED_ACTUAL.json').exists()
    old=target.read_text('utf8');backup=N/'UNUSED_OLD_TEXT_HASH_ONLY_COLLECTOR_SOURCE_BEFORE_CLOSED43_LOG_FIX.py';assert not backup.exists();backup.write_bytes(target.read_bytes())
    new=old.replace('import hashlib,importlib.util,json,os,sys,time,traceback','import base64,hashlib,importlib.util,json,os,sys,time,traceback')
    before="""            sf.get(row['path'],str(p));assert p.stat().st_size==row['bytes'] and H(p)==row['SHA']
            texts.append(dict(row,local_path=str(p)))"""
    after="""            sf.get(row['path'],str(p))
            if p.stat().st_size==row['bytes'] and H(p)==row['SHA']:
                texts.append(dict(row,local_path=str(p)))
            else:
                assert rel.as_posix()=='h1/job0/home/.nvidia-omniverse/logs/omni.processlifetime.log','Unexpected text mismatch; preserve original and stop'
                original=dict(row,local_path=str(p),transferred_bytes=p.stat().st_size,transferred_SHA=H(p),manifest_time_bytes_not_captured=True)
                code=\"from pathlib import Path;import base64,hashlib,json; p=Path(v['path']); a=p.stat(); raw=p.read_bytes(); b=p.stat(); assert (a.st_dev,a.st_ino,a.st_size,a.st_mtime_ns)==(b.st_dev,b.st_ino,b.st_size,b.st_mtime_ns); print(json.dumps(dict(path=str(p),bytes=len(raw),SHA=hashlib.sha256(raw).hexdigest(),mtime_ns=b.st_mtime_ns,base64=base64.b64encode(raw).decode())))\"
                fresh=d.code(c,d.t.PY,code,dict(path=row['path']),timeout=45);raw=base64.b64decode(fresh.pop('base64'));assert len(raw)==fresh['bytes'] and hashlib.sha256(raw).hexdigest()==fresh['SHA']
                fp=p.with_name('omni.processlifetime.fresh_after_manifest_mismatch.log')
                with fp.open('xb') as f:f.write(raw)
                put('H1_ONLY_PROCESSLIFETIME_LOG_MANIFEST_TRANSFER_AND_FRESH_SNAPSHOT_ACTUAL.json',dict(epoch=time.time(),original=original,fresh=dict(fresh,local_path=str(fp)),cause_unknown=True,original_manifest_time_bytes_unavailable=True,no_training_failure_or_refund_inferred=True))
                texts.append(dict(row,bytes=fresh['bytes'],SHA=fresh['SHA'],local_path=str(fp),original_manifest_and_transferred_log_preserved=original,one_fresh_snapshot_only=True))"""
    assert old.count(before)==1;new=new.replace(before,after)
    a=ast.parse(old);b=ast.parse(new)
    def untouched(tree):
        return [ast.dump(x) for x in tree.body if not isinstance(x,(ast.Import,ast.ImportFrom)) and not (isinstance(x,ast.FunctionDef) and x.name=='capture')]
    assert untouched(a)==untouched(b)
    assert 'nominal_end_epoch\']-time.time()<=900' in new
    target.write_text(new,encoding='utf8')
    put(R/'UNUSED44_COLLECTOR_BOUNDED_PROCESSLIFETIME_LOG_SNAPSHOT_SOURCE_AST_ACTUAL.json',dict(epoch=time.time(),passed=True,old_source_SHA=H(backup),new_source_SHA=H(target),old_unused_source_preserved=str(backup),only_import_and_capture_changed=True,all_other_top_level_AST_exact=True,original_900_local_gate_retained=True,one_known_text_log_snapshot_on_mismatch_only=True,no_model_raw_training_source_account_guard_or_remote_task_change=True,not_executed=True))
    print(json.dumps(dict(passed=True,scope_correction_saved=True,unused44_collector_fixed_without_training_change=True)))

if __name__=='__main__':main()
