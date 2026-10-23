from pathlib import Path
import ast,hashlib,json,time
T=Path(r'C:/Users/lulu/Desktop/claude/mjcf/MOD4_H1_SCUT_STEP270_ON_210_E3_CONTINUATION_20261021');N=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V51_20261024';P=T/'H1_STEP270_REWARD_TUCK_CLEARANCE_V4_RESOURCE_V49_20261023';B=T/'H1_STEP270_REWARD_PATH_V1_20261022'
s=(P/'relocate_missing_closed48_44_after_closed49_TLS_V4_once.py').read_text('utf8').replace('CLOSED49','CLOSED51').replace('OLD48','OLD49').replace('RESOURCE_V48_20261023','RESOURCE_V49_20261023').replace("('48' if batch==0 else '44')","('49' if batch==0 else '44')")
a=ast.parse(s); literal=next(x.value for x in a.body if isinstance(x,ast.Assign) and any(isinstance(y,ast.Name) and y.id=='INVENTORY' for y in x.targets));old=ast.literal_eval(literal)
new=old.replace('if free+total>25*1024**3 and total<=',"if free+total>25*1024**3+v['install_copy_planning_bytes'] and total<=")
assert new!=old
s=s[:literal.col_offset]+s[literal.col_offset:] if False else s
lines=s.splitlines(keepends=True);start=sum(map(len,lines[:literal.lineno-1]))+literal.col_offset;end=sum(map(len,lines[:literal.end_lineno-1]))+literal.end_col_offset;s=s[:start]+repr(new)+s[end:]
s=s.replace("max_bytes=maximum)","max_bytes=maximum,install_copy_planning_bytes=80247048)")
s=s.replace("combined_preflight_before_any_target_controller=True)","combined_preflight_before_any_target_controller=True,known_H1_manifest_bytes=63469832,install_copy_planning_bytes=80247048,copy_planning_not_new_training_gate=True)")
ast.parse(s);dest=N/'relocate_missing_closed49_44_after_closed51_TLS_V4_once.py';assert not dest.exists();dest.write_text(s,'utf8')
w=(B/'same_authorized_session_compressed_transport_v24.py').read_text('utf8');anchor="        'relocate_missing_install_headroom_after_failed50_TLS_V4_once.py',";assert w.count(anchor)==1;w=w.replace(anchor,anchor+"\n        '"+dest.name+"',");ast.parse(w);target=B/'same_authorized_session_compressed_transport_v25.py';assert not target.exists();target.write_text(w,'utf8')
with (N/'reports/CLOSED51_OLD49_44_MISSING_ONLY_SOURCE_AST_AND_COPY_PLANNING_ACTUAL.json').open('x',encoding='utf8') as f:json.dump(dict(epoch=time.time(),helper=str(dest),helper_SHA=hashlib.sha256(dest.read_bytes()).hexdigest(),source_clone=str(P/'relocate_missing_closed48_44_after_closed49_TLS_V4_once.py'),changes=['current51 and old49/44 namespaces','minimum subset also leaves known80247048 install copy planning bytes','wrapper25 adds only this exact basename'],unselected_stat_only=True,protocol_TLS_unchanged=True,no_training_or_budget_mutation=True,not_executed_yet=True),f,indent=2)
print(dest)