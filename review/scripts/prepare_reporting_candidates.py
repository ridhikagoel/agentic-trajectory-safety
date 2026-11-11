from pathlib import Path
import csv,re,json
root=Path(__file__).resolve().parents[1];out=root/'fulltext_audit';rs=list(csv.DictReader((root/'coding/lit_A_final.csv').open()))
patterns={
 'cost':r'false.?positive|\bFPR\b|latenc|overhead|wall.clock|inference (time|cost)|computational cost|token (cost|usage)|execution time|runtime (cost|performance)|milliseconds|\bms\b',
 'lead':r'lead.time|early.warning|early.detection|detection.delay|timeliness|advance.warning|\bEIR\b|\bEDR\b|\bEAUPC\b|\bEAP\b|steps (before|ahead|earlier)|time.to.detect',
 'real':r'production|real.world|real.traces|deployment|deployed|live.agent|real.execution|operational',
}
all=[]
for r in rs:
 text=(out/'text'/f"{r['arxiv_id']}.txt").read_text();pages=text.split('\f');ev={k:[] for k in patterns}
 for page,txt in enumerate(pages,1):
  if re.search(r'^\s*(References|REFERENCES|Bibliography)\s*$',txt,re.M):txt=re.split(r'^\s*(?:References|REFERENCES|Bibliography)\s*$',txt,flags=re.M)[0]
  lines=txt.splitlines()
  for k,pat in patterns.items():
   for i,line in enumerate(lines):
    if re.search(pat,line,re.I):
     snippet=re.sub(r'\s+',' ',' '.join(lines[max(0,i-1):i+3])).strip()
     score=3*bool(re.search(r'\d|Table|Figure',snippet,re.I))+2*bool(re.search(r'we |our |report|measur|evaluat|achieve',snippet,re.I))+(page>1)
     ev[k].append(dict(page=page,snippet=snippet,score=score))
 for k in ev:
  seen=set();unique=[]
  for x in sorted(ev[k],key=lambda x:-x['score']):
   if x['snippet'][:100] not in seen:unique.append(x);seen.add(x['snippet'][:100])
  ev[k]=unique[:12]
 all.append(dict(**r,pages=len(pages)-1,evidence_candidates=ev))
(out/'evidence_candidates.json').write_text(json.dumps(all,indent=2))
