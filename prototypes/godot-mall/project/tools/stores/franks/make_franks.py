"""Franks' neon (Steven, Oct 8 2026): the lowercase "franks" of the store's Courier ads (the menu
ad, src/franks_menu_ad.png; the Easter ad src/franks_bunny_ad.png shows the same face) traced to
the centre line of every stroke, one neon tube per stroke, for franks.gd.

1. Mask the logo (grey ink, the ad's text row cut away), 4x, and skeletonize it.
2. Split the skeleton at its junctions; chain the pieces into strokes, going straight on at a
   junction (the greedy pass), then assemble the tubes as a sign shop bends them: f's stem and
   hook as one, its bar; r; a; n; k's stem, its arm and leg as one bent tube, the short bar
   joining them to the stem; s.
3. Smooth each run, carry its ends out to the stroke's ends, resample every 10 px, and write
   franks_sign.json in metres (1.30 m tall, x centred, y up from the s's tail).

  python3 tools/stores/franks/make_franks.py   (from the project folder; numpy, scipy,
  scikit-image, pillow)
"""
import os, json, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
WORK = tempfile.mkdtemp()
os.chdir(WORK)

# ---- 1. mask and skeleton
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
from skimage.morphology import skeletonize, remove_small_objects
im=np.array(Image.open(os.path.join(HERE,'src','franks_menu_ad.png')).convert('L')).astype(float)
x0,y0,x1,y1=130,35,580,270
g=im[y0:y1,x0:x1]
S=4
g=np.array(Image.fromarray(g.astype(np.uint8)).resize((g.shape[1]*S,g.shape[0]*S),Image.BICUBIC)).astype(float)
g=ndi.gaussian_filter(g,2)
m=(g<175)
# remove text row (left of the s)
m[(220-y0)*S:, :(445-x0)*S]=False
m=remove_small_objects(m,3000)
m=ndi.binary_fill_holes(m) & m | ndi.binary_closing(m,iterations=2)
lab,nl=ndi.label(m); print('parts',nl)
Image.fromarray((m*255).astype(np.uint8)).save('mask.png')
# stroke width
dt=ndi.distance_transform_edt(m)
sk=skeletonize(m)
print('stroke width px (4x):', 2*np.median(dt[sk]))
np.save('mask.npy',m); np.save('sk.npy',sk)
v=np.dstack([m*120,m*120,m*120]).astype(np.uint8); v[sk]=[255,0,0]
Image.fromarray(v).resize((v.shape[1]//2,v.shape[0]//2)).save('sk.png')

# ---- 2. strokes
import numpy as np, json
from PIL import Image
from scipy import ndimage as ndi
sk=np.load('sk.npy'); m=np.load('mask.npy')
H,W=sk.shape
pts=set(zip(*np.nonzero(sk)))
def nb(p):
    y,x=p; return [(y+dy,x+dx) for dy in(-1,0,1) for dx in(-1,0,1) if (dy or dx) and (y+dy,x+dx) in pts]
deg={p:len(nb(p)) for p in pts}
# prune short spurs (< 25 px) iteratively
for it in range(3):
    ends=[p for p in pts if len(nb(p))==1]
    for e in ends:
        path=[e]; cur=e; prev=None
        while True:
            n=[q for q in nb(cur) if q!=prev and q not in path]
            if len(nb(cur))>2 or not n: break
            prev=cur; cur=n[0]; path.append(cur)
            if len(path)>40: break
        if len(path)<=40 and len(nb(cur))>2:
            for q in path[:-1]: pts.discard(q)
# edges between nodes (deg!=2)
def isnode(p): return len(nb(p))!=2
nodes=[p for p in pts if isnode(p)]
# cluster junction pixels
seen=set(); edges=[]
for s in nodes:
    for n0 in nb(s):
        if (s,n0) in seen: continue
        path=[s,n0]; prev=s; cur=n0
        while not isnode(cur):
            nx=[q for q in nb(cur) if q!=prev]
            # prefer 4-neighbours ambiguity: take the one not in path
            nx=[q for q in nx if q not in path]
            if not nx: break
            prev,cur=cur,nx[0]; path.append(cur)
        seen.add((s,n0)); seen.add((cur,path[-2]))
        if len(path)>3: edges.append(path)
# dedupe edges (same endpoints, similar length)
uniq=[]
for e in edges:
    key=frozenset([e[0],e[-1]]); 
    if any(frozenset([u[0],u[-1]])==key and abs(len(u)-len(e))<5 for u in uniq): continue
    uniq.append(e)
edges=uniq
print('edges',len(edges))
lab,_=ndi.label(m)
# group by letter component; order components left->right
comp={}
for i,e in enumerate(edges):
    c=lab[e[len(e)//2]]; comp.setdefault(c,[]).append(i)
order=sorted(comp, key=lambda c: min(p[1] for i in comp[c] for p in edges[i]))
def tang(path, at_end, k=25):
    a=np.array(path[-1] if at_end else path[0],float); b=np.array(path[-1-min(k,len(path)-1)] if at_end else path[min(k,len(path)-1)],float)
    d=a-b; return d/ (np.linalg.norm(d)+1e-9)
runs=[]
for ci,c in enumerate(order):
    E=list(comp[c]); used=set()
    while len(used)<len(E):
        rem=[i for i in E if i not in used]
        # start: an edge end that is a free endpoint (deg 1), lowest one first
        cands=[]
        for i in rem:
            for end in (0,1):
                p=edges[i][0] if end==0 else edges[i][-1]
                if len(nb(p))==1: cands.append((-p[0],i,end))
        if cands: _,i,end=min(cands)
        else: i=rem[0]; end=0
        path=list(edges[i]) if end==0 else list(edges[i][::-1]); used.add(i)
        while True:
            tip=path[-1]; t=tang(path,True)
            best=None
            for j in E:
                if j in used: continue
                for e2 in (0,1):
                    q=edges[j] if e2==0 else edges[j][::-1]
                    if np.hypot(q[0][0]-tip[0],q[0][1]-tip[1])<6:
                        t2=-tang(q,False)
                        score=float(np.dot(t,-t2))
                        if best is None or score>best[0]: best=(score,j,q)
            if best is None or best[0]<0.0: break
            used.add(best[1]); path+=best[2][1:]
        runs.append((ci,path))
print([ (ci,len(p)) for ci,p in runs])
json.dump([[ci,[[int(p[1]),int(p[0])] for p in path]] for ci,path in runs],open('runs_raw.json','w'))
v=np.dstack([m*60]*3).astype(np.uint8)
cols=[(255,80,80),(80,255,80),(80,160,255),(255,220,60),(255,80,255),(80,255,255),(255,160,60),(200,200,200),(160,100,255)]
for k,(ci,p) in enumerate(runs):
    for q in p: v[q]=cols[k%len(cols)]
Image.fromarray(v).resize((W//2,H//2)).save('runs.png')

# ---- 3. tubes
import json, numpy as np
from scipy.ndimage import gaussian_filter1d
from PIL import Image, ImageDraw
R=[np.array(p,float) for ci,p in json.load(open('runs_raw.json'))]
m=np.load('mask.npy')
def split_at(p,q):
    i=int(np.argmin(np.hypot(*(p-np.array(q)).T))); return p[:i+1],p[i:]
def sm(p,s=7):
    if len(p)<8: return p
    q=np.c_[gaussian_filter1d(p[:,0],s,mode='nearest'),gaussian_filter1d(p[:,1],s,mode='nearest')]
    q[0]=p[0]; q[-1]=p[-1]
    # restore ends drift: blend
    return q
def ext(p,amt,start=True,end=True):
    p=p.copy()
    if start:
        d=p[0]-p[min(15,len(p)-1)]; d/=np.linalg.norm(d); p=np.vstack([p[0]+d*amt,p])
    if end:
        d=p[-1]-p[-1-min(15,len(p)-1)]; d/=np.linalg.norm(d); p=np.vstack([p,p[-1]+d*amt])
    return p
def resample(p,step=10):
    d=np.r_[0,np.cumsum(np.hypot(*np.diff(p,axis=0).T))]; n=max(2,int(d[-1]/step)+1)
    t=np.linspace(0,d[-1],n); return np.c_[np.interp(t,d,p[:,0]),np.interp(t,d,p[:,1])]
HW=30  # half stroke width at 4x
tubes=[]
# f
lo,hi=split_at(R[0],(90,404))
stem=np.vstack([sm(lo),sm(R[1][::-1])[1:]])
tubes.append(('f', ext(sm(stem,4),HW*0.8)))
tubes.append(('f', ext(sm(hi),HW*0.8,start=False)))
tubes.append(('r', ext(sm(R[2]),HW*0.8)))
tubes.append(('a', ext(sm(R[3]),HW*0.8)))
tubes.append(('n', ext(sm(R[4]),HW*0.8)))
kst=np.vstack([R[8],R[6][::-1]]); tubes.append(('k', ext(sm(kst),HW*0.8)))
knot=np.array([1343,506.])
arm=sm(R[7]); leg=sm(R[5])[::-1]
tubes.append(('k', ext(np.vstack([arm[:-1],knot,leg[1:]]),HW*0.8)))
bar=sm(R[9]); tubes.append(('k', ext(bar,0,True,False)))
tubes.append(('s', ext(sm(R[10],9),HW*0.8)))
tubes=[(c,resample(p)) for c,p in tubes]
ys,xs=np.nonzero(m); print('mask bbox',xs.min(),xs.max(),ys.min(),ys.max())
# f height -> metres
ftop=ys.min()
json.dump({'px_per_unit':1.0,'bbox':[int(xs.min()),int(ys.min()),int(xs.max()),int(ys.max())],
 'tubes':[{'letter':c,'pts':np.round(p,1).tolist()} for c,p in tubes]},open('franks_tubes_px.json','w'))
im=Image.fromarray((m*90).astype(np.uint8)).convert('RGB'); d=ImageDraw.Draw(im)
for c,p in tubes:
    d.line([tuple(x) for x in p],fill=(255,60,40),width=14)
    for e in (p[0],p[-1]): d.ellipse([e[0]-14,e[1]-14,e[0]+14,e[1]+14],fill=(30,30,30))
im.resize((im.width//2,im.height//2)).save('tubes.png')

# ---- metres
J = json.load(open('franks_tubes_px.json'))
x0, y0, x1, y1 = J['bbox']; H = 1.30; s = H / (y1 - y0); cx = (x0 + x1) / 2
out = {'note': "Franks lowercase logo (Courier ads, 1988-95: Steven's menu ad), traced to stroke centre lines: one red neon tube per stroke, skeleton neon straight on the facade",
       'width': round((x1 - x0) * s, 4), 'height': H, 'baseline': round((y1 - 640) * s, 4),
       'tubes': [{'letter': t['letter'], 'closed': False, 'pts': [[round((p[0] - cx) * s, 4), round((y1 - p[1]) * s, 4)] for p in t['pts']]} for t in J['tubes']]}
json.dump(out, open(os.path.join(HERE, 'franks_sign.json'), 'w'))
print('franks_sign.json:', out['width'], 'x', H, 'm,', len(out['tubes']), 'tubes')
