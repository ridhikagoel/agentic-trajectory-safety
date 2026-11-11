import csv,subprocess,concurrent.futures,hashlib,json,datetime
from pathlib import Path
root=Path(__file__).resolve().parents[1]
out=root/'fulltext_audit';(out/'pdf').mkdir(exist_ok=True);(out/'text').mkdir(exist_ok=True)
rows=list(csv.DictReader((root/'coding/lit_A_final.csv').open()))
def fetch(r):
 aid=r['arxiv_id'];p=out/'pdf'/f'{aid}.pdf';t=out/'text'/f'{aid}.txt';url=f'https://arxiv.org/pdf/{aid}'
 if not p.exists():
  z=subprocess.run(['curl','-sS','-L','--fail','--max-time','75','--retry','1',url,'-o',str(p)],capture_output=True,text=True)
  if z.returncode:return dict(arxiv_id=aid,title=r['title'],url=url,status='retrieval_failed',error=z.stderr[-250:])
 if p.read_bytes()[:4]!=b'%PDF':return dict(arxiv_id=aid,title=r['title'],url=url,status='not_pdf')
 z=subprocess.run(['pdftotext','-layout',str(p),str(t)],capture_output=True,text=True)
 return dict(arxiv_id=aid,title=r['title'],url=url,status='text_ready' if z.returncode==0 else 'extraction_failed',sha256=hashlib.sha256(p.read_bytes()).hexdigest(),retrieved_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),pages=len(t.read_text(errors='replace').split('\f'))-1 if t.exists() else 0)
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
 results=[]
 for result in pool.map(fetch,rows):
  results.append(result);print(result['arxiv_id'],result['status'],flush=True)
  (out/'retrieval_manifest.json').write_text(json.dumps(results,indent=2))
print('DONE',len(results))
