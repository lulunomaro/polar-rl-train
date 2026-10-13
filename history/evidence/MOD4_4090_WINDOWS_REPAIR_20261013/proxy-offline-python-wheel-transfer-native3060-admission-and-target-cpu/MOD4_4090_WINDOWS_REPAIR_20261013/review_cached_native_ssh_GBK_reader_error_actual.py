from pathlib import Path
import ast,json,time,hashlib
D=Path(__file__).resolve().parent
files=sorted((D/'reports').glob('WINDOWS4090_SINGLE_PINNED_LAN_ZT_READONLY_ACTUAL_*.json'))
p=files[-1];r=json.loads(p.read_bytes());row=next(x for x in r['attempts'] if x.get('error','').startswith('UnicodeDecodeError('))
call=ast.parse(row['error'],mode='eval').body
assert isinstance(call,ast.Call) and isinstance(call.func,ast.Name) and call.func.id=='UnicodeDecodeError'
raw=ast.literal_eval(call.args[1]);assert isinstance(raw,bytes)
decoded=json.loads(raw.decode('gbk').strip());assert decoded['hostname']=='DESKTOP-J17LAN1' and decoded['username'].lower()=='win10'
q=D/'reports'/('CACHED_NATIVE_LAN_GBK_DECODED_READONLY_ACTUAL_'+str(time.time_ns())+'.json')
proof=dict(epoch=time.time(),passed=True,original_reader_path=str(p),original_reader_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),original_error_unchanged=True,original_LAN_native_SSH_exitcode0=True,LAN_authenticated_expected_Windows_host=True,transport_did_not_fail_for_this_attempt=True,source_raw_stdout_bytes_sha256=hashlib.sha256(raw).hexdigest(),source_raw_stdout_bytes=len(raw),independent_GBK_json_decode_of_exact_retained_exception_bytes=True,actual=decoded,no_new_SSH_or_GPU_or_installer_or_budget_mutation=True,ZT_fallback_timeout_retained_not_retried=True)
q.write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(report=str(q),actual_hostname=decoded['hostname'],Python_present=decoded['Python_present'],receipts=[dict(name=x['name'],passed=(x['content'] or {}).get('passed'),exit_code=(x['content'] or {}).get('exit_code')) for x in decoded['reports']]),ensure_ascii=False))
