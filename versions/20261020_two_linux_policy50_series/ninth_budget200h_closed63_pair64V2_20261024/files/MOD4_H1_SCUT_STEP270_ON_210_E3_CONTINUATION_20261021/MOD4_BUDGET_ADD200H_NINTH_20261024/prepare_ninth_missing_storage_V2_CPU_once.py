from pathlib import Path
import ast,hashlib,json,time
B=Path(__file__).resolve().parent;T=B.parent;R=B/'reports';N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V63_20261024';F=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V64_20261024';proto='forensic_tls_peer_transfer_V96_V5_NINTH.py';H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
src=N/'relocate_missing_closed62_26_after_closed63_NINTH_TLS_once.py';s=src.read_text('utf8')
s=s.replace('CLOSED63_NINTH_OLD62_26','CLOSED63_NINTH_V2_OLD62_26').replace("label='CLOSED63_NINTH_OLD'","label='CLOSED63_NINTH_V2_OLD'")
needle="spec.loader.exec_module(ops);d=ops.d";assert s.count(needle)==1;s=s.replace(needle,needle+"\nops.BOOT=ops.BOOT.replace('forensic_tls_peer_transfer_V96_V4.py','"+proto+"')")
tree=ast.parse(s);inv=next(ast.literal_eval(x.value) for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='INVENTORY' for t in x.targets));start=inv.index('for row in selected:');end=inv.index('assert C.read_bytes()==canonical',start)
replacement='''cache={r['path']:r for r in v['sha_cache']}
for row in selected:
 old=cache.get(row['path'])
 if old and all(old[k]==row[k] for k in ('bytes','SHA','mtime_ns','inode')):continue
 h=hashlib.sha256()
 with Path(row['path']).open('rb') as f:
  for block in iter(lambda:f.read(8*1024**2),b''):h.update(block)
 assert h.hexdigest()==row['SHA']
''';newinv=inv[:start]+replacement+inv[end:];ast.parse(newinv);a=s.index('INVENTORY=');b=s.index('\n\nREAD_SOURCE',a);s=s[:a]+'INVENTORY='+repr(newinv)+s[b:]
needle=" m=importlib.util.spec_from_file_location('memory'";idx=s.index(needle);s=s[:idx]+" cache=read(R/'CLOSED63_NINTH_OLD62_26_COMBINED_MINIMAL_FRESH_SOURCE_ACTUAL.json')\n"+s[idx:]
needle='dict(sources=sources,current_owner_root=';assert s.count(needle)==1;s=s.replace(needle,'dict(sha_cache=cache[\'files\'],sources=sources,current_owner_root=')
needle='c=d.connect72(secret);capacity=';assert s.count(needle)==1
failed="from pathlib import Path;import os,psutil,json,time;B=Path(v['root']);assert not any(p.pid!=os.getpid() and any(a.startswith(str(B)+'/') for a in p.info['cmdline'] or []) for p in psutil.process_iter(['pid','cmdline']));print(json.dumps(dict(epoch=time.time(),all_failed_storage_processes_actual_out=True,receiver_never_started_no_ready=True,files=[dict(name=p.name,bytes=p.stat().st_size) for p in B.iterdir() if p.is_file()],raw_target_files=[p.name for p in (B/'retained_control_npz').iterdir()])))"
insert="c=d.connect72(secret);put('CLOSED63_NINTH_V2_FAILED_V1_ACTUAL_OUT_EMPTY_TARGET_ACTUAL.json',d.code(c,d.PY72,"+repr(failed)+",dict(root='/home/lc01/Zonglin Li/zonglin2/forensic_originals/PEER_TLS_CLOSED63_NINTH_OLD62_MINIMAL_V4'),timeout=30));capacity="
s=s.replace(needle,insert);ast.parse(s);dest=N/'relocate_missing_closed62_26_after_closed63_NINTH_TLS_V2_once.py';assert not dest.exists();dest.write_text(s,'utf8')
for name in ('relocate_selected_pair_closed_forensics_unused_once.py','relocate_selected_H1_closed_forensics_unused_once.py'):
 p=F/name;x=p.read_text('utf8');needle='spec.loader.exec_module(ops);d=ops.d';assert x.count(needle)==1;x=x.replace(needle,needle+"\nops.BOOT=ops.BOOT.replace('forensic_tls_peer_transfer_V96_V4.py','"+proto+"')");ast.parse(x);p.write_text(x,'utf8')
w=T/'H1_STEP270_REWARD_PATH_V1_20261022/same_authorized_session_compressed_transport_v40.py';x=w.read_text('utf8');needle="        'collect_selected_pair_finals_unused_once.py',";x=x.replace(needle,needle+"\n        '"+dest.name+"',");wrapper=w.with_name('same_authorized_session_compressed_transport_v41.py');assert not wrapper.exists();ast.parse(x);wrapper.write_text(x,'utf8')
with (R/'NINTH_STORAGE_V1_BOOT_FILENAME_ORIGINAL_ERROR_V2_AST_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),original_source=str(src),original_source_SHA=H(src),original_failure='ops.BOOT attempted old V4 basename although V5 budget-bound source was installed; FileNotFoundError before receiver ready',V2=str(dest),V2_SHA=H(dest),new_namespace=True,original_failed_target_and_error_kept=True,reuse_previously_full_SHA_only_when_fresh_path_size_mtime_inode_exact=True,newly_selected_missing_SHA_only=True,failed_V1_process_out_checked_before_any_V2_target=True,unused64_future_BOOT_binding_corrected_before_execution=True,wrapper=str(wrapper),source_AST=True),f,indent=2)
print(json.dumps(dict(V2=str(dest),wrapper=str(wrapper),AST=True)))
