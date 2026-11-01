"""Resume the interrupted CPU purpose from its resident carrier; no reread."""
import importlib,textwrap
try:
    import reference283 as reference_module
    Reference283=importlib.reload(reference_module).Reference283
    text=(N/'review284_actual_carrier_CPU_once.py').read_text('utf8')
    text=text[text.index('    reference=Reference283'):text.index('\nexcept BaseException:')]
    exec(compile(textwrap.dedent(text),'<CPU284 cached continuation>','exec'),globals())
except BaseException:
    put('CPU284_CACHED_CONTINUATION_ORIGINAL_ERROR_'+str(time.time_ns())+'.json',
      dict(epoch=time.time(),error=traceback.format_exc(),carrier_rereads=0))
    raise
