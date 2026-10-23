from pathlib import Path
import ast,json,time
D=Path(__file__).resolve().parent;R=D/'reports'
with (R/'ARCHIVE_PREP_V1_MONITOR_TRAILING_NEWLINE_READER_ORIGINAL_ERROR_ACTUAL.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),error='Traceback (most recent call last):\n  File "prepare_v4_archive_and_exact_monitor_readback_CPU_once.py", line 9, in <module>\n    for key in (\'name\',\'status\',\'rrule\',\'kind\',\'prompt\'):assert actual[key]==args[key],key\nAssertionError: prompt\n',argument_prompt_characters=14900,actual_prompt_characters=14899,first_difference=14899,only_difference='Tool removed one terminal newline; all actual prompt content matches.',no_archive_helper_or_record_started=True,no_training_failure_or_GO_change=True,old_reader_consumed_not_reexecuted=True),f,indent=2)
text=(D/'prepare_v4_archive_and_exact_monitor_readback_CPU_once.py').read_text('utf8')
old="for key in ('name','status','rrule','kind','prompt'):assert actual[key]==args[key],key"
new="for key in ('name','status','rrule','kind'):assert actual[key]==args[key],key\nassert actual['prompt']==args['prompt'].removesuffix('\\n'), 'Only tool terminal-newline normalization accepted'"
assert text.count(old)==1;text=text.replace(old,new)
text=text.replace('exact_prompt_readback=True','exact_prompt_content_after_one_terminal_newline_removed=True,requested_prompt_SHA=hashlib.sha256(args[\'prompt\'].encode()).hexdigest(),tool_removed_one_terminal_newline_only=True')
ast.parse(text);dest=D/'prepare_v4_archive_and_normalized_monitor_readback_CPU_v2_once.py';assert not dest.exists();dest.write_text(text,encoding='utf8')
print(json.dumps(dict(new_unused_reader=str(dest),only_terminal_newline_normalization=True)))
