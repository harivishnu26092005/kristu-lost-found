import re
from difflib import SequenceMatcher
def tokens(s): return set(re.findall(r'[a-z0-9]+',(s or '').lower()))
def sim(a,b):
    a=(a or '').lower().strip(); b=(b or '').lower().strip()
    if not a or not b: return 0
    x,y=tokens(a),tokens(b); j=len(x&y)/len(x|y) if x|y else 0
    return max(SequenceMatcher(None,a,b).ratio(),j)
def score_match(a,b):
    score=0; why=[]; t=sim(a.get('title'),b.get('title')); d=sim(a.get('description'),b.get('description'))
    if t>=.25: score+=t*48; why.append('similar item name')
    if a.get('category')==b.get('category'): score+=24; why.append('same category')
    if a.get('block')==b.get('block'): score+=18; why.append('same campus block')
    if a.get('sublocation')==b.get('sublocation'): score+=8; why.append('same specific location')
    if d>=.25: score+=d*12; why.append('similar description')
    return min(99,round(score)),why
def suggest_matches(source,candidates,minimum_score=20):
    out=[]
    for c in candidates:
        if c.get('id')==source.get('id'): continue
        score,why=score_match(source,c)
        if score>=minimum_score: out.append((c,score,why))
    return sorted(out,key=lambda x:x[1],reverse=True)
