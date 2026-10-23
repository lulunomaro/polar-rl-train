from pathlib import Path
import ast,hashlib,json,time
import capture_index_ordered_parts_v1 as fmt
D=Path(__file__).resolve().parent;R=D/'reports';W=D.parent.parent;C=W/'MOD4_WORKSPACE_CLEANUP_AUTHORIZED_20261021_V88';G=W/'polar-rl-train'
H=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    cpu=json.loads((R/'FORWARD_COMPLETE_CAPTURE_INDEX_ORDERED_UTF8_PARTS_MEMORY_CPU_ACTUAL.json').read_bytes());assert cpu['passed']
    algorithm=ast.parse(cpu['algorithm_source']);module=ast.parse(Path(fmt.__file__).read_text('utf8'))
    for name in ('index_parts','reassemble_index'):
        a=next(x for x in algorithm.body if isinstance(x,ast.FunctionDef) and x.name==name);b=next(x for x in module.body if isinstance(x,ast.FunctionDef) and x.name==name)
        assert ast.dump(a)==ast.dump(b)
    source=Path(cpu['source']);value=fmt.read_capture_index(source,G);assert len(value['entries'])==cpu['complete_entries']
    captured={};splits=[];fake=G/'versions/__MEMORY_ONLY_COMPLETE_INDEX_FORMAT_CPU__/COMPLETE_FILE_CAPTURE_INDEX.json'
    def add(p,raw):captured[p.relative_to(G).as_posix()]=raw
    used=fmt.write_capture_index(fake,value,add,splits,G);assert used==fmt.FORMAT and len(splits)==1
    descriptor=json.loads(captured[fake.relative_to(G).as_posix()]);rows=descriptor['ordered_UTF8_parts'];blocks=[captured[x['path']] for x in rows]
    assert fmt.reassemble_index(blocks,rows,descriptor['complete_json_bytes'],descriptor['complete_json_SHA'])==value
    assert descriptor['complete_json_SHA']==cpu['source_SHA'] and descriptor['complete_json_bytes']==cpu['source_bytes']
    assert not fake.parent.exists()
    target=C/'append_current_clearance_v4_closed47_pair48_ordinary_once.py'
    assert not (C/'reports/append_current_clearance_v4_closed47_pair48_ordinary_once_STARTED_ACTUAL.json').exists()
    old=target.read_text('utf8');assert 'read_capture_index' not in old
    insertion="sys.path.insert(0,str(T/'H1_STEP270_TUCK_V3_FIRST_CLOSED39_REPLAY_20261023'))\nfrom capture_index_ordered_parts_v1 import read_capture_index,write_capture_index\n\n"
    a='  v=json.loads(p.read_bytes())';b='  v=read_capture_index(p,G)';assert old.count(a)==1
    x="add(D/'COMPLETE_FILE_CAPTURE_INDEX.json',json.dumps(index,ensure_ascii=False,indent=2).encode('utf8'))";y="write_capture_index(D/'COMPLETE_FILE_CAPTURE_INDEX.json',index,add,splits,G)";assert old.count(x)==1
    fresh=old.replace('def main():',insertion+'def main():',1).replace(a,b).replace(x,y).replace('new_full_large_logs=len(splits)','new_full_large_texts=len(splits)')
    ast.parse(fresh)
    restored=fresh.replace(insertion,'',1).replace(b,a).replace(y,x).replace('new_full_large_texts=len(splits)','new_full_large_logs=len(splits)')
    assert restored==old
    backup=C/'UNUSED_CLOSED47_PAIR48_ORDINARY_BEFORE_FULL_INDEX_PARTS.py';assert not backup.exists();backup.write_bytes(target.read_bytes());target.write_text(fresh,encoding='utf8')
    report=dict(epoch=time.time(),passed=True,old_actual_text_index=str(source),input_bytes=cpu['source_bytes'],input_SHA=cpu['source_SHA'],complete_entries=cpu['complete_entries'],all_original_JSON_values_and_full_UTF8_bytes_exact=True,legacy_reader_actual_text_index_passed=True,partition_and_reassembly_functions_AST_exact_to_passed_memory_CPU=True,memory_writer_roundtrip_and_same_full_SHA=True,no_temporary_directory_or_binary_model_raw_GPU_host_or_ledger_read=True,unused_old_writer_preserved=str(backup),old_writer_SHA=H(backup),new_writer_SHA=H(target),format_module=str(Path(fmt.__file__)),format_module_SHA=H(fmt.__file__),only_new_writer_import_and_index_read_write_and_output_label_changed=True,all_other_source_bytes_exact=True,no_old_Git_object_or_tag_change=True,no_new_training_gate=True,not_executed_archive_yet=True,format=fmt.FORMAT)
    with (R/'UNUSED_CLOSED47_ORDINARY_FULL_INDEX_PARTS_SOURCE_AST_AND_CPU_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(report,f,ensure_ascii=False,indent=2)
    print(json.dumps(dict(passed=True,complete_entries=cpu['complete_entries'],old_text_bytes=cpu['source_bytes'],full_index_parts=len(rows),legacy_compatible=True,unused_writer_patched_only=True)))

if __name__=='__main__':main()
