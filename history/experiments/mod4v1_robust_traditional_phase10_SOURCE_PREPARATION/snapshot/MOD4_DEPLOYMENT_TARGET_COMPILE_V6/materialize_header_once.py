"""Exactly one authorized original ZIP member payload; no archive code or native tool."""
from pathlib import Path,PurePosixPath
import json,hashlib,zipfile,zlib,stat,traceback
O=Path(__file__).resolve().parent;R=O.parent
load=lambda p:json.loads(p.read_bytes())
def rec(p):
 b=p.read_bytes();return {'path':str(p),'bytes':len(b),'SHA':hashlib.sha256(b).hexdigest()}
def save(n,x):
 with(O/n).open('x',encoding='utf-8',newline='\n')as f:json.dump(x,f,ensure_ascii=False,indent=2);f.write('\n')
scope_path=O/'PARENT_CMSIS_DEPENDENCY_SCOPE.json';scope=load(scope_path);a=scope['exact_one_payload_permission']
member='StandardRobotpp-balance1/Middlewares/Third_Party/FreeRTOS/Source/CMSIS_RTOS/cmsis_os.h'
assert a['member']==member and a['bytes']==53065 and a['CRC32']=='61803e9e'and a['maximum_members']==1 and a['maximum_member_bytes']==1048576
v5path=R/'MOD4_DEPLOYMENT_DEPENDENCY_STATIC_V5/HEADER_OVERLAY_PLAN_V5.json';v5=load(v5path);v5receipt=load(R/'MOD4_DEPLOYMENT_DEPENDENCY_STATIC_V5/RECEIPT_V5_FINAL.json');assert rec(v5path)==v5receipt['plan'] and v5receipt['payload_reads_or_extracts']==v5receipt['native_toolchain_or_compiles']==0
assert v5['header_count']==1 and v5['candidates'][0]['member']==member and v5['candidates'][0]['bytes']==53065 and v5['candidates'][0]['CRC32']=='61803e9e'and v5['source_payload_read_count']==v5['native_toolchain_count']==0
raw_path=O/'cmsis_header_overlay/cmsis_os.h';readable=O/'readable/cmsis_os.h'
assert not raw_path.exists()and not readable.exists()and not(O/'HEADER_INPUT_RECEIPT_01.json').exists()and not(O/'HEADER_ERROR_01.json').exists()
archive=Path(a['archive']);s=archive.stat();assert s.st_size==a['archive_expected_bytes']==76134913
before={'bytes':s.st_size,'mtime_ns':s.st_mtime_ns};attempts=0
try:
 with zipfile.ZipFile(archive,'r')as z:
  matched=[x for x in z.infolist()if x.filename==member];assert len(matched)==1;i=matched[0]
  assert not i.is_dir()and not stat.S_ISLNK(i.external_attr>>16)and i.file_size==53065 and i.CRC==int('61803e9e',16)and i.file_size<a['maximum_member_bytes']
  assert not PurePosixPath(member).is_absolute()and'..'not in PurePosixPath(member).parts
  attempts+=1;data=z.read(i) # the ONLY original ZIP member payload read
 assert len(data)==53065 and'%08x'%(zlib.crc32(data)&0xffffffff)=='61803e9e'
 after_s=archive.stat();after={'bytes':after_s.st_size,'mtime_ns':after_s.st_mtime_ns};assert after==before
 raw_path.parent.mkdir(exist_ok=True)
 with raw_path.open('xb')as f:f.write(data)
 codecs=[];decoded=None;used=None
 for codec in ('utf-8-sig','gb18030','cp1252'):
  try:
   text=data.decode(codec,errors='strict');codecs.append({'codec':codec,'strict_decode_success':True})
   if decoded is None:decoded=text;used=codec
  except UnicodeDecodeError as e:codecs.append({'codec':codec,'strict_decode_success':False,'start':e.start,'end':e.end,'reason':e.reason})
 if decoded is not None:
  readable.parent.mkdir(exist_ok=True)
  with readable.open('x',encoding='utf-8',newline='\n')as f:f.write(decoded)
 h=rec(raw_path);assert h['bytes']==53065 and h['SHA']==hashlib.sha256(data).hexdigest()
 receipt={'status':'EXACT_ORIGINAL_RAW_HEADER_VERIFIED_READABLE_READY_FOR_REVIEW'if decoded is not None else'RAW_VERIFIED_CODEC_UNKNOWN_NATIVE_GATE_NOT_READY','scope':rec(scope_path),'method':rec(O/'METHOD.md'),'V5_static_plan':rec(v5path),'materializer':rec(Path(__file__).resolve()),'archive_path':str(archive),'archive_stat_before':before,'archive_stat_after':after,'whole_archive_SHA_computed':False,'member':member,'member_uncompressed_bytes':i.file_size,'member_compressed_bytes':i.compress_size,'central_CRC32':'%08x'%i.CRC,'actual_payload_CRC32':'%08x'%(zlib.crc32(data)&0xffffffff),'raw_compiler_overlay':h,'readable_only_never_compiler_input':rec(readable)if decoded is not None else None,'strict_decode_attempts':codecs,'chosen_successful_strict_codec':used,'unique_original_charset':'UNPROVEN_COMPATIBLE_DECODING_ONLY','original_member_payload_read_attempts':attempts,'other_member_payload_reads':0,'compiler_input_transcoded':False,'native_invocations':0}
 save('HEADER_INPUT_RECEIPT_01.json',receipt);print(json.dumps({'status':receipt['status'],'raw_header':h,'CRC32':receipt['actual_payload_CRC32'],'chosen_strict_codec':used,'readable':receipt['readable_only_never_compiler_input'],'receipt':rec(O/'HEADER_INPUT_RECEIPT_01.json'),'payload_member_reads':attempts,'native':0},ensure_ascii=False,indent=2))
except BaseException:
 save('HEADER_ERROR_01.json',{'status':'STOP_NO_PAYLOAD_RETRY_OR_NATIVE','authorized_payload_read_attempts':attempts,'error':traceback.format_exc(),'scope':rec(scope_path)});raise
