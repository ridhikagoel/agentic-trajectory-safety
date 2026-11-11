import json,re,datetime,subprocess,concurrent.futures,hashlib
from pathlib import Path
p=Path(__file__).resolve().parents[1]/'fulltext_audit'
rs=json.loads((p/'retrieval_manifest.json').read_text()); cutoff=datetime.datetime(2026,9,30)
def header(txt):
 m=re.search(r'arXiv:(\d+\.\d+v(\d+))\s*\[[^\]]+\]\s*(\d{1,2} \w{3} \d{4})',txt)
 return (m.group(1),int(m.group(2)),datetime.datetime.strptime(m.group(3),'%d %b %Y')) if m else None
def fix(r):
 aid=r['arxiv_id']; t=p/'text'/f'{aid}.txt';h=header(t.read_text())
 if not h:r['version_status']='header_missing';return r
 r['downloaded_version']=h[0];r['version_date']=h[2].date().isoformat()
 if h[2]>cutoff:
  ar=p/'later_versions';ar.mkdir(exist_ok=True)
  (ar/f'{h[0]}.pdf').write_bytes((p/'pdf'/f'{aid}.pdf').read_bytes())
  (ar/f'{h[0]}.txt').write_text(t.read_text())
  for v in range(h[1]-1,0,-1):
   vid=re.sub(r'v\d+$','',aid)+f'v{v}';pp=ar/f'{vid}.pdf';tt=ar/f'{vid}.txt'
   z=subprocess.run(['curl','-sSL','--fail','--max-time','60',f'https://arxiv.org/pdf/{vid}','-o',str(pp)],capture_output=True)
   if z.returncode:continue
   subprocess.run(['pdftotext','-layout',str(pp),str(tt)],capture_output=True)
   hh=header(tt.read_text())
   if hh and hh[2]<=cutoff:
    (p/'pdf'/f'{aid}.pdf').write_bytes(pp.read_bytes());t.write_text(tt.read_text());h=hh;r['downloaded_version']=hh[0];r['version_date']=hh[2].date().isoformat();break
 r['url']=f"https://arxiv.org/pdf/{r['downloaded_version']}";r['sha256']=hashlib.sha256((p/'pdf'/f'{aid}.pdf').read_bytes()).hexdigest();r['version_status']='within_cutoff' if h[2]<=cutoff else 'unresolved';return r
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
 rr=list(pool.map(fix,rs))
(p/'retrieval_manifest.json').write_text(json.dumps(rr,indent=2))
for r in rr:
 if r['version_status']!='within_cutoff' or r['downloaded_version']!=re.sub(r'v\d+$','',r['arxiv_id'])+'v1':print(r['arxiv_id'],r.get('downloaded_version'),r['version_status'])
