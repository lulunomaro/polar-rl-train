from pathlib import Path
import hashlib,json,time
N=Path(__file__).resolve().parent;T=N.parent;R=N/'reports'
src=T/'archive_ACTUAL194_original_JUMP_plane_two_hour_and188_closing_ONCE.py';s=src.read_text(encoding='utf8')
with (R/'ARCHIVE194_V1_ORIGINAL_PRE_RECORD_NEWLINE_ASSERTION_FAILURE.json').open('x',encoding='utf8') as f:
 json.dump(dict(epoch=time.time(),original_source=str(src),source_SHA=hashlib.sha256(src.read_bytes()).hexdigest(),
  original_error='AssertionError at archive_ACTUAL194_original_JUMP_plane_two_hour_and188_closing_ONCE.py line19: actual[prompt]==req[prompt]',
  actual_prompt_chars=6083,request_prompt_chars=6084,only_difference='automation_update strips one final newline',
  splitlines_equal=True,rrule_and_original_thread_equal=True,record_experiment_called=False,Git_modified=False,training_untouched=True),f,indent=2)
assert "actual['prompt']==req['prompt']" in s
s=s.replace("actual['prompt']==req['prompt']","actual['prompt']==req['prompt'].rstrip('\\n')")
s=s.replace("source=Path(__file__).resolve();dest=V/'ROOT_ARCHIVE_DRIVER.py';dest.write_bytes(source.read_bytes());selected.append(dest.relative_to(G).as_posix())",
 "source=Path(__file__).resolve();dest=V/'ROOT_ARCHIVE_DRIVER_V2.py';dest.write_bytes(source.read_bytes());selected.append(dest.relative_to(G).as_posix())\nsource=T/'archive_ACTUAL194_original_JUMP_plane_two_hour_and188_closing_ONCE.py';dest=V/'ROOT_ARCHIVE_DRIVER_V1_ORIGINAL_REFUSAL.py';dest.write_bytes(source.read_bytes());selected.append(dest.relative_to(G).as_posix())")
dest=T/'archive_ACTUAL194_original_JUMP_plane_two_hour_and188_closing_V2_ONCE.py'
with dest.open('x',encoding='utf8') as f:f.write(s)
print(json.dumps(dict(prepared=True,record_experiment_calls=0,no_model_raw_or_remote_work=True)))
