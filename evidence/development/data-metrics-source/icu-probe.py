import ctypes as C,hashlib,json,math,platform,subprocess
from pathlib import Path
lib=C.CDLL('/usr/lib/aarch64-linux-gnu/libicui18n.so.74')
def api(name,args,restype):
 f=getattr(lib,name+'_74');f.argtypes=args;f.restype=restype;return f
Char=C.c_uint16;Status=C.c_int32
openfmt=api('unumf_openForSkeletonAndLocale',[C.POINTER(Char),C.c_int32,C.c_char_p,C.POINTER(Status)],C.c_void_p)
openresult=api('unumf_openResult',[C.POINTER(Status)],C.c_void_p)
formatdouble=api('unumf_formatDouble',[C.c_void_p,C.c_double,C.c_void_p,C.POINTER(Status)],None)
tostring=api('unumf_resultToString',[C.c_void_p,C.POINTER(Char),C.c_int32,C.POINTER(Status)],C.c_int32)
closefmt=api('unumf_close',[C.c_void_p],None);closeresult=api('unumf_closeResult',[C.c_void_p],None)
root=Path('evidence/reference-investigations/data-metrics-20261015');rows=[]
for locale in ['en_US','de_DE','es_CL','fr_FR','ja_JP','ar_EG','hi_IN']:
 for case in json.loads((root/('locale-'+locale)/'captures.json').read_text())['formatting']:
  skeleton={'number':'.######','percent':'percent scale/100 .######','compact':'compact-short','currency':'currency/'+case['currencyCode']}[case['format']]
  raw=skeleton.encode('utf-16-le');units=(Char*(len(raw)//2)).from_buffer_copy(raw);status=Status(0)
  formatter=openfmt(units,len(units),locale.encode(),C.byref(status));text=None
  if status.value<=0:
   status.value=0;result=openresult(C.byref(status));formatdouble(formatter,float(case['value']),result,C.byref(status))
   buf=(Char*4096)();n=tostring(result,buf,len(buf),C.byref(status))
   if status.value<=0:text=C.string_at(buf,n*2).decode('utf-16-le')
   closeresult(result)
  if formatter:closefmt(formatter)
  rows.append({**case,'locale':locale,'skeleton':skeleton,'icuText':text,'icuStatus':status.value,'equal':text==case['text']})
result={'status':'read-only standalone prototype; no dependency, product, exception or acceptance change','icu':'74.2-1ubuntu3.1 / Ubuntu24.04 ARM64 system library','qtBundledIcu':'73.2 (not used by this probe)','probeSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'cases':len(rows),'matches':sum(r['equal'] for r in rows),'mismatches':sum(not r['equal'] for r in rows),'results':rows}
Path('artifacts/data-metrics/icu-comparison.json').write_text(json.dumps(result,indent=2,ensure_ascii=True)+'\n');print({k:v for k,v in result.items() if k!='results'})
