"""Original local parser rejection retained; only repair embedded NUL source escaping."""
from cleanup_io import *
source=D/'delete_authorized_old_incoming_checkpoints_once.py'
raw=source.read_bytes();assert raw.count(bytes([0]))==1
save('DELETE_SOURCE_NULL_BYTE_REVIEW.json',dict(epoch=time.time(),original_path=str(source),original_bytes=len(raw),original_SHA=H(raw),embedded_NUL_count=1,original_Python_SyntaxError_before_main_or_SSH_or_deletion=True,independent_only_NUL_literal_escape_repair=True,no_approval_scope_or_path_guard_change=True))
fixed=raw.replace(bytes([0]),bytes([92])+b'x00');compile(fixed,str(__file__),'exec')
exec(compile(fixed,str(__file__)+'#byte-escape-reviewed','exec'),dict(__file__=__file__,__name__='__main__'))
