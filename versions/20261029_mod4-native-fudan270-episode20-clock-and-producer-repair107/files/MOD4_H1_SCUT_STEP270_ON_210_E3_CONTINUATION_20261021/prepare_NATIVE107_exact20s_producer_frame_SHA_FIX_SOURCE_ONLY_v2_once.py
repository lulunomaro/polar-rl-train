from pathlib import Path
T=Path(__file__).resolve().parent;P=T/'prepare_NATIVE107_exact20s_producer_frame_SHA_FIX_SOURCE_ONLY_once.py'
s=P.read_text('utf8')
s=s.replace('assert not N.exists();R.mkdir(parents=True);','assert N.exists() and not (R/\'TWO107_COHERENT20S_SEALED_PAYLOADS_ACTUAL.json\').exists();R.mkdir(parents=True,exist_ok=True);')
s=s.replace('B.mkdir(parents=True);manifest=','B.mkdir(parents=True,exist_ok=True);manifest=')
s=s.replace("   if src.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):os.link(src,dst)","   if dst.exists():\n    assert dst.stat().st_size==src.stat().st_size\n    if src.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):assert os.path.samestat(src.stat(),dst.stat())\n    else:assert H(dst)==H(src)\n    continue\n   if src.suffix.lower() in ('.pt','.pth','.npz','.usd','.usdc','.zip'):os.link(src,dst)")
s=s.replace("s=rep(p.read_text('utf8'),oldliteral,newliteral);assert s.replace(newliteral,oldliteral)==oldbytes.decode();write(p,s)","assert oldbytes.count(oldliteral.encode())==1;newbytes=oldbytes.replace(oldliteral.encode(),newliteral.encode());assert newbytes.replace(newliteral.encode(),oldliteral.encode())==oldbytes;p.write_bytes(newbytes)")
exec(compile(s,str(P),'exec'),dict(__name__='__main__',__file__=str(P)))
