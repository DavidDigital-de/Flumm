# FLUMM Plattformen v3: SNES-Look + 3D, hochaufgelöst (K-fache Abtastung)
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import math,json,sys
K=4;W,H=84,72
BY=[[0,8,2,10],[12,4,14,6],[3,11,1,9],[15,7,13,5]]
def hx(c):c=c.lstrip('#');return (int(c[0:2],16),int(c[2:4],16),int(c[4:6],16),255)
def lerp(a,b,t):return tuple(int(a[i]+(b[i]-a[i])*t) for i in range(3))+(255,)
def pick(ramp,s,X,Y):
    # weicher Verlauf zwischen Stufen, leichtes Dither für SNES-Charakter
    s=max(0,min(len(ramp)-1.001,s));i=int(s);f=s-i
    b=(BY[(Y//2)%4][(X//2)%4]+.5)/16
    f=min(1,max(0,(f-.5)*1.6+.5+(b-.5)*.35))
    return lerp(hx(ramp[i]),hx(ramp[min(len(ramp)-1,i+1)]),f)
def hn(x,y,k=1):
    x=int(math.floor(x));y=int(math.floor(y))
    n=(x*374761393+y*668265263+k*1442695041)&0xffffffff;n=((n^(n>>13))*1274126177)&0xffffffff;return (n&0xffff)/65535
P={'grass':['#E4FF9C','#B8F06A','#8EDB45','#6CC333','#4FA327','#37801E','#25601A'],
'dirt':['#F5CF97','#DDA868','#C48B50','#A6703E','#87572F','#683F22','#4A2B17','#311C10'],
'stone':['#FBFAFF','#E2DEF0','#C4BED8','#A49EBD','#857F9F','#67617F','#4B4562','#332F45'],
'wood':['#FFE2A8','#F2C07A','#DDA15C','#C08343','#9C6533','#7A4C26','#58351A','#3B2311'],
'ice':['#E3F9FF','#B9EDFD','#8BD9F7','#62BEEC','#449FDA','#3080C2','#235F99'],
'lava':['#8E7C94','#6E5E76','#56475E','#43364A','#33283A','#251C2B','#18111D'],
'glow':['#FFF8C2','#FFE066','#FFB23D','#FF7A1F','#E0441A'],
'cloud':['#FFFFFF','#F4F9FF','#E2EEFF','#CADDF9','#AFC8F0','#94B0E2'],
'cap':['#FFC2CC','#FF8EA2','#F65C74','#E03D58','#BE2944','#951B35','#6C1227'],
'stem':['#FFF8EA','#F4E4C8','#E2CBA6','#C9AE86','#A78D67'],
'icing':['#FFF0F7','#FFC9E2','#FFA3CF','#F77DB6','#DC5C99','#B8447E'],
'dough':['#FCE0A4','#EDBE72','#DAA154','#BF853E','#9C672C','#784C1E'],
'crys':['#F0DEFF','#D6B4FF','#B98AFF','#9A63EE','#7A45CF','#5A2EA6','#3E1D78'],
'metal':['#FFFFFF','#E8ECF3','#CBD2DE','#AEB6C6','#9099AC','#737C90','#575F73','#3D4354'],
'hazard':['#FFE680','#FFC93C','#E0A21E','#B57A10'],
'sand':['#FFF4CF','#FBE3A2','#F2CC7A','#E0B060','#C8934A','#A87638','#85592A'],
'sstone':['#F6D7A6','#E8BC82','#D3A066','#B9834F','#9A683D','#7A4F2E','#593821'],
'terra':['#F3B98A','#E09A68','#C97C4E','#AB623C','#8A4B2E','#683722','#4A2618'],
'moss':['#D7F59A','#A9DE5E','#7FC43F','#5EA530','#438427','#2E631D','#1F4516'],
'honey':['#FFF3B0','#FFDF66','#FFC531','#F2A61C','#D98514','#B0650E','#7E4709'],
'comb':['#F9D98A','#EDBB5E','#D99B3F','#BB7C2C','#96601F','#704515'],
'bark':['#C99566','#A9764A','#8A5B35','#6E4426','#55321B','#3D2312'],
'ring':['#FFE7B8','#F5CE8C','#E5B26A','#CC9452'],
'cactus':['#B6F07A','#7FD04A','#58B034','#3E8C26','#2A6A1B'],
'red':['#FFB0B0','#FF6B6B','#E5484D','#B8303A','#86202A'],
'lift':['#E6F4FF','#B9DEFF','#86C3F5','#5AA3E3','#3E82C8','#2D63A3','#20477A'],
'gold':['#FFF8D6','#FFEA8A','#FFD84A','#F5BE22','#DB9D17','#B47C10','#82570A'],
'snow':['#FFFFFF','#F4F9FF','#E1EDFA','#C8DAF0','#ABC3E4','#8EA9D4','#7390C0'],
'rb':[['#FF8A8A','#FF5C5C','#E04545'],['#FFC680','#FFA23D','#E08419'],['#FFF08A','#FFE04D','#E6C21F'],['#A7F59A','#6FDB5E','#46B83A'],['#9AD6FF','#5FB8F5','#3A93D6'],['#C7A8FF','#A07BF5','#7C55D6']]}
class C:
    def __init__(s):s.im=Image.new('RGBA',(W*K,H*K),(0,0,0,0));s.px=s.im.load();s.m=set()
    def put(s,X,Y,c):s.px[X,Y]=c;s.m.add((X,Y))
    def fill(s,fn):  # fn(x,y,X,Y)-> color or None ; x,y logische Koordinaten
        for Y in range(H*K):
            y=(Y+.5)/K
            for X in range(W*K):
                c=fn((X+.5)/K,y,X,Y)
                if c:s.put(X,Y,c)
    def dot(s,x,y,c,r=.5):  # logischer "Pixel" (rund, weich) – Deko
        for Y in range(int((y-r)*K),int((y+r)*K)+1):
            for X in range(int((x-r)*K),int((x+r)*K)+1):
                if 0<=X<W*K and 0<=Y<H*K and ((X+.5)/K-x)**2+((Y+.5)/K-y)**2<=r*r:s.put(X,Y,c)
    def done(s):
        px=s.px;m=s.m;edge=set()
        for (X,Y) in m:
            for dx in range(-2,3):
                for dy in range(-2,3):
                    q=(X+dx,Y+dy)
                    if q not in m and dx*dx+dy*dy<=5 and 0<=q[0]<W*K and 0<=q[1]<H*K:edge.add((q,(X,Y)))
        out={}
        for q,src in edge:
            b=px[src];out[q]=(int(b[0]*.22+28),int(b[1]*.22+20),int(b[2]*.22+44),255)
        for q,c in out.items():px[q]=c
        return s.im
# ---------- Grundformen ----------
CX,CY,A,B=W/2,18,36,11
def topell(x,y):dx=(x-CX)/A;dy=(y-CY)/B;return dx,dy,dx*dx+dy*dy
def island(top,body,texT=None,texF=None,lipL=3,depth=34,cel=True):
    c=C()
    def fn(x,y,X,Y):
        dx,dy,r=topell(x,y)
        if r<=1:
            v=(dy+1)/2;s=.5+v*1.9+max(0,dx)*.9
            if r>.84 and dy<0:s=-.3+ (r-.84)*2
            if texT:
                t=texT(x,y,dx,dy)
                if isinstance(t,tuple):return t
                s+=t
            return pick(top,s,X,Y)
        if dy>0 and abs(dx)<1:
            ey=CY+B*math.sqrt(1-dx*dx);L=lipL+2.2*hn(x/3,0,7)
            if y<ey+L:return pick(top,2.6+(y-ey)/L*1.7+max(0,dx)*1.3,X,Y)
            fv=(y-ey)/depth;col=math.floor(x/6)
            lim=1-(max(0,fv)**1.7)*.92+(hn(col,math.floor(fv*5),3)-.5)*.13
            if 0<=fv<=1 and abs(dx)<=lim:
                fac=hn(col,math.floor(fv*3+hn(col,1,2)*1.5),5)
                s=fv*2.6+dx*1.5+(fac-.5)*1.6
                if cel:s=round(s*2)/2
                s+=1.2
                if abs(dx)>lim-.07:s+=1.4
                if (x%6)<.45 and fv>.1:s+=.9
                if texF:
                    t=texF(x,y,dx,fv)
                    if isinstance(t,tuple):return t
                    s+=t
                return pick(body,s,X,Y)
    c.fill(fn);return c
def box(top,front,texT=None,texF=None,hgt=20,side=None):
    c=C();x0,x1,ty,th,sk=8,70,11,14,8
    def fn(x,y,X,Y):
        if ty<=y<ty+th:
            k=(ty+th-y)/th;xl=x0+sk*k;xr=x1+sk*k
            if xl<=x<xr:
                u=(x-xl)/(xr-xl);s=.4+(1-k)*1.3+u*.5
                if y<ty+.7:s=-.3
                if texT:
                    t=texT(x,y,u,1-k)
                    if isinstance(t,tuple):return t
                    s+=t
                return pick(top,s,X,Y)
        if ty+th<=y<ty+th+hgt and x0<=x<x1:
            v=(y-ty-th)/hgt;u=(x-x0)/(x1-x0);s=2+v*2+u*.6+(1.3 if y<ty+th+.8 else 0)
            if texF:
                t=texF(x,y,u,v)
                if isinstance(t,tuple):return t
                s+=t
            return pick(front,s,X,Y)
        if x1<=x<x1+sk:
            o=x-x1;yt=ty+th-o*th/sk
            if yt<=y<yt+hgt:
                v=(y-yt)/hgt;s=4.1+v*1.8
                if texF:
                    t=texF(x,y,1,v)
                    if isinstance(t,tuple):return t
                    s+=t*.6
                return pick(side or front,s,X,Y)
    c.fill(fn);return c
def balls(c,ramp,bl,zcut=None):
    L=(-.5,-.75,.55);n=math.sqrt(sum(q*q for q in L));L=[q/n for q in L]
    def fn(x,y,X,Y):
        if zcut and not zcut(x,y):return None
        best=None
        for (bx,by,r) in bl:
            d=((x-bx)/r)**2+((y-by)/r)**2
            if d<=1:
                z=math.sqrt(1-d)
                if best is None or z*r>best[0]:best=(z*r,(x-bx)/r,(y-by)/r,z)
        if best:
            _,nx,ny,z=best;dif=max(0,nx*L[0]+ny*L[1]+z*L[2]);spec=dif**18
            if spec>.5:return hx('#FFFFFF')
            return pick(ramp,(1-dif)*(len(ramp)-1.3),X,Y)
    c.fill(fn);return c
# ---------- Deko-Helfer ----------
def tuft(c,x,y,ramp,s=1):
    for (dx,dy,i) in [(0,0,3),(0,-1,2),(0,-2,1),(-1,-1,3),(-2,-2,2),(-2.6,-2.8,1),(1,-1,3),(2,-3,1),(2.6,-3.6,0),(1,0,4),(-1,0,4)]:c.dot(x+dx*s,y+dy*s,hx(ramp[i]),.62)
def flower(c,x,y,pet='#FFFFFF',mid='#FFC93C'):
    for dx,dy in((0,-1),(-1,0),(1,0),(0,1)):c.dot(x+dx,y+dy,hx(pet),.7)
    c.dot(x,y,hx(mid),.6)
def spike(c,x,yb,h,ramp,w=2.4):
    for i in range(int(h*K)):
        d=i/K;ww=w*(1-d/h)
        Y=int((yb-d)*K)
        for X in range(int((x-ww)*K),int((x+ww)*K)+1):
            u=((X+.5)/K-x+ww)/(2*ww+1e-6);c.put(X,Y,pick(ramp,u*3.2+.3,X,Y))
# ---------- Designs ----------
def grassT(x,y,dx,dy):return 1.1 if hn(x/2,y,2)>.95 else 0
def dirtF(x,y,dx,fv):return -1.3 if hn(x/4,y/3,4)>.93 else 0
def d_grass():
    c=island(P['grass'],P['dirt'],grassT,dirtF)
    for x,y in [(16,15),(29,11),(56,12),(66,18),(24,22)]:tuft(c,x,y,P['grass'])
    flower(c,45,17);flower(c,58,22,'#FFD3E6','#FF6FAE');return c
def d_stone():
    def T(x,y,u,v):return 1.4 if ((x-8*(1-v))%12<.5 or (y-11)%7<.45) else 0
    def F(x,y,u,v):
        o=6*(math.floor(v*3)%2)
        if (x+o)%12<.5 or (v*30)%10<.45:return 2.2
        if (x+o)%12<1:return -.8
        return 0
    return box(P['stone'],P['stone'],T,F)
def d_wood():
    def T(x,y,u,v):
        xx=x-8*(1-v)
        return 2.4 if xx%10<.5 else (-.6 if xx%10<1.1 else (.6 if hn(xx/2,y*2,6)>.9 else 0))
    def F(x,y,u,v):return 2.2 if x%10<.5 else (1.5 if (v*20)%10>9 else 0)
    c=box(P['wood'],P['wood'],T,F,hgt=13)
    for x in (12,66):c.dot(x,28,hx('#E8ECF3'),.8);c.dot(x+.4,28.4,hx('#737C90'),.4)
    return c
def d_ice():
    def T(x,y,dx,dy):return -1.8 if (x-y*2)%19<1.2 else 0
    def F(x,y,dx,fv):return -1.6 if (x+fv*16)%15<.8 else 0
    return island(P['ice'],P['ice'][1:],T,F,cel=False)
def d_lava():
    def T(x,y,dx,dy):
        if (((x+y)//2)%11==0 and hn(x,y,8)>.5) or hn(x/2,y/2,9)>.93:return pick(P['glow'],1+hn(x,y)*2,int(x*K),int(y*K))
        return 0
    def F(x,y,dx,fv):
        if (x+y*.4)%13<.9:return pick(P['glow'],.5+fv*3,int(x*K),int(y*K))
        return 0
    return island(P['lava'],P['lava'],T,F)
def d_cloud():return balls(C(),P['cloud'],[(20,30,13),(36,22,17),(54,22,16),(68,31,11),(44,34,15),(28,36,11),(60,37,11)])
def d_shroom():
    c=C()
    def stem(x,y,X,Y):
        if 34<=x<50 and y>=30:u=(x-34)/16;return pick(P['stem'],abs(u-.35)*4+(1 if y<35 else 0),X,Y)
    c.fill(stem)
    balls(c,P['cap'],[(42,36,27),(24,35,14),(60,35,14)],zcut=lambda x,y:y<31)
    def gills(x,y,X,Y):
        if 31<=y<34 and 16<=x<68:return pick(P['stem'],2.4+(y-31)*.7+abs(x-42)/20,X,Y)
    c.fill(gills)
    for (sx,sy,r) in [(30,20,4.2),(46,14,3.5),(58,22,4.5),(38,26,3),(22,27,2.5)]:
        for Y in range(int((sy-r)*K),int((sy+r)*K)):
            for X in range(int((sx-r)*K),int((sx+r)*K)):
                x,y=(X+.5)/K,(Y+.5)/K
                if (X,Y) in c.m and ((x-sx)/r)**2+((y-sy)/(r*.8))**2<=1:c.put(X,Y,pick(P['stem'],((x-sx)/r+1)*1.2,X,Y))
    return c
def d_candy():
    def F(x,y,dx,fv):
        drip=.08+(math.sin(x*.9)+1)*.09
        if fv<drip:return pick(P['icing'],3+fv*8,int(x*K),int(y*K))
        return 0
    c=island(P['icing'],P['dough'],texF=F,lipL=2)
    cs=['#5FB8F5','#FFE066','#4FCB8A','#FFFFFF','#B58CFF']
    for i in range(30):
        x=10+hn(i,1)*64;y=9+hn(i,2)*17;dx,dy,r=topell(x,y)
        if r<.8:
            a=hn(i,3)*3.1
            for t in (-.8,-.3,.3,.8):c.dot(x+math.cos(a)*t,y+math.sin(a)*t,hx(cs[i%5]),.45)
    c.dot(60,13,hx('#E5484D'),2.4);c.dot(59.2,12.2,hx('#FF8A8A'),.8)
    return c
def d_crystal():
    c=island(P['crys'],P['crys'][1:])
    for (x,y,h) in [(18,18,11),(23,19,7),(55,16,13),(61,18,8),(40,14,6)]:spike(c,x,y,h,P['crys'])
    return c
def d_metal():
    def F(x,y,u,v):
        if v>.42 and ((x+y)//4)%2==0:return pick(P['hazard'],(v-.42)*4+(1 if u>=1 else 0),int(x*K),int(y*K))
        if v>.42:return 4.5
        return 0
    c=box(P['metal'],P['metal'],texF=F,hgt=17)
    for x in (13,64):c.dot(x,28.5,hx('#FFFFFF'),.9);c.dot(x+.4,28.9,hx('#737C90'),.5)
    return c
def d_sand():
    def T(x,y,dx,dy):return .8 if math.sin(x*.5+dy*6)>.85 else 0
    c=island(P['sand'],P['sstone'],T)
    for (x,y,r) in [(24,15,2.2),(52,20,1.8)]:balls(c,P['sstone'],[(x,y,r)])
    return c
def d_moss():
    def F(x,y,dx,fv):
        hang=.08+hn(math.floor(x/2),0,4)*.35
        if fv<hang:return pick(P['moss'],2+fv*9,int(x*K),int(y*K))
        return 0
    c=island(P['moss'],P['stone'],texF=F)
    for x,y in [(14,17),(31,12),(50,11),(67,17)]:tuft(c,x,y,P['moss'],1.1)
    return c
def d_ruin():
    def T(x,y,u,v):
        if hn(x/2,y/2,11)>.82:return pick(P['moss'],2+hn(x,y)*2,int(x*K),int(y*K))
        return 1.4 if ((x-8*(1-v))%14<.5 or (y-11)%7<.45) else 0
    def F(x,y,u,v):
        o=7*(math.floor(v*3)%2)
        if v<.25 and hn(x/2,1,12)>.45:return pick(P['moss'],2.5+v*6,int(x*K),int(y*K))
        if (x+o)%14<.6 or (v*30)%10<.5:return 2.4
        return .6 if hn(x/3,y/3,13)>.85 else 0
    c=box(P['stone'][1:],P['stone'][1:],T,F)
    def pillar(x,y,X,Y):
        if 30<=x<40 and 1<=y<17:
            u=(x-30)/10;s=abs(u-.3)*3.5+1+(2 if y<2.5 else 0)
            if (y%5)<.5:s+=1.5
            return pick(P['stone'],s,X,Y)
    c.fill(pillar);tuft(c,42,17,P['moss'])
    return c
def d_log():
    c=C();x0,x1,yc,R=14,74,26,12
    def fn(x,y,X,Y):
        if x0<=x<=x1 and abs(y-yc)<=R:
            ny=(y-yc)/R;s=(ny+.75)**2*1.6+(.6 if (y+math.floor(x/9)*2)%6<.6 else 0)+(x-x0)/(x1-x0)*.6
            return pick(P['bark'],s,X,Y)
        ex=(x-x0)/(R*.55);ey=(y-yc)/R
        if ex*ex+ey*ey<=1:
            rr=math.sqrt(ex*ex+ey*ey)
            if rr>.86:return pick(P['bark'],2.5,X,Y)
            return pick(P['ring'],1+.9*math.sin(rr*13),X,Y)
    c.fill(fn)
    for x,y in [(30,15),(56,15)]:tuft(c,x,y,P['grass'],1.1)
    flower(c,43,15)
    return c
def d_desert():
    c=island(P['sand'],P['terra'])
    def cac(x,y,X,Y):
        for (a,b,cc,d) in [(51,2,55,17),(46,6,49,12),(55,4,58,10)]:
            if a<=x<cc and b<=y<d:
                u=(x-a)/(cc-a);return pick(P['cactus'],abs(u-.3)*3.6+(.8 if (x-a)%2<.25 else 0),X,Y)
        if 46<=x<51 and 10<=y<12.5:return pick(P['cactus'],1.5+(y-10),X,Y)
        if 55<=x<58 and 8<=y<10.5 and False:return None
    c.fill(cac);c.dot(53.5,1.6,hx('#FF6FAE'),1.1)
    balls(c,P['sstone'],[(24,16,2.6),(30,19,1.6)])
    return c
def d_honey():
    def T(x,y,dx,dy):
        hxx=(x+ (math.floor(y/4)%2)*2.5)%5;hy=y%4
        return .9 if hxx<.5 or hy<.4 else 0
    def F(x,y,dx,fv):
        drip=.1+(math.sin(x*.7)+1)*.12+(.25 if hn(math.floor(x/5),2,3)>.75 else 0)
        if fv<drip:return pick(P['honey'],1.5+fv*6+dx,int(x*K),int(y*K))
        return 0
    return island(P['honey'],P['comb'],T,F)
def d_rainbow():
    c=balls(C(),P['cloud'],[(16,32,10),(30,28,13),(46,27,14),(62,28,12),(72,33,8),(40,36,12)])
    def band(x,y,X,Y):
        dx,dy,r=topell(x,y+3)
        if r<=1:
            i=min(5,int((dx+1)/2*6));rp=P['rb'][i];v=(dy+1)/2
            return pick(rp,v*1.6+(-.2 if r>.85 and dy<0 else 0),X,Y)
    c.fill(band);return c
def d_spring():
    c=box(P['metal'],P['metal'],hgt=9)
    def coil(x,y,X,Y):
        for cy in (16,12.5,9):
            dx=(x-42)/14;dy=(y-cy)/2.6
            r=dx*dx+dy*dy
            if .45<=r<=1 or (r<=1 and dy>0):return pick(P['hazard'],(dy+1)*1.2+max(0,dx)*1.2,X,Y)
    c.fill(coil)
    def pad(x,y,X,Y):
        dx=(x-42)/20;dy=(y-5)/3.4
        if dx*dx+dy*dy<=1:return pick(P['red'],(dy+1)*1.1+max(0,dx)*.8-(.4 if dy<-.6 else 0),X,Y)
        if abs(dx)<1 and 5<=y<8.5:return pick(P['red'],2.6+(y-5)*.35+max(0,dx),X,Y)
    c.fill(pad);return c
def d_lift():
    def F(x,y,u,v):return 0
    c=box(P['lift'],P['lift'],hgt=12)
    for X0 in (14,62):
        def post(x,y,X,Y,X0=X0):
            if X0<=x<X0+4 and 1<=y<13:return pick(P['metal'],abs((x-X0)/4-.3)*4+1,X,Y)
        c.fill(post)
    for (ax,dir) in [(42,-1),(42,1)]:
        for i in range(int(5*K)):
            d=i/K;w=3.2*(d/5)
            for X in range(int((ax-w)*K),int((ax+w)*K)+1):
                c.put(X,int((18+dir*(2+5-d) if dir<0 else 18+dir*(2+5-d))*K) if False else int(((15-5+d) if dir<0 else (25-d))*K),hx('#FFE066'))
    return c
def d_crack():
    def T(x,y,dx,dy):
        for (x0,y0,x1,y1) in [(24,10,30,16),(30,16,27,22),(30,16,37,19),(50,9,46,15),(46,15,52,21),(52,21,58,23)]:
            L=math.hypot(x1-x0,y1-y0);t=max(0,min(1,((x-x0)*(x1-x0)+(y-y0)*(y1-y0))/L/L))
            if math.hypot(x-(x0+t*(x1-x0)),y-(y0+t*(y1-y0)))<.45:return hx('#4A3424')
        return 0
    c=island(P['sstone'],P['sstone'][1:],T,depth=22)
    for i,(x,y,r) in enumerate([(26,52,1.6),(40,56,1.2),(50,50,1.4)]):balls(c,P['sstone'],[(x,y,r)])
    return c
def d_gold():
    def T(x,y,dx,dy):return -1.2 if (x-y*2)%17<1.3 else 0
    def F(x,y,dx,fv):
        if hn(x/3,y/3,21)>.88:return pick(P['gold'],1+fv*2,int(x*K),int(y*K))
        return 0
    c=island(P['gold'],P['dirt'],T,F)
    for (x,y) in [(22,13),(50,10),(62,20),(34,22)]:
        for dx,dy,r in [(0,0,.9),(1.6,0,.45),(-1.6,0,.45),(0,1.6,.45),(0,-1.6,.45)]:c.dot(x+dx,y+dy,hx('#FFFFFF'),r)
    return c
def d_snow():
    def F(x,y,dx,fv):
        hang=.06+hn(math.floor(x/3),0,6)*.22
        if fv<hang:return pick(P['snow'],2+fv*8,int(x*K),int(y*K))
        return 0
    def T(x,y,dx,dy):return -.8 if hn(x/1.5,y/1.5,31)>.93 else 0
    c=island(P['snow'],P['stone'][1:],T,F,lipL=4)
    for (x,y,r) in [(22,15,2.4),(27,16,1.6),(56,13,2.0)]:balls(c,P['snow'],[(x,y,r)])
    return c
D=[('snow','Schneeinsel',d_snow),('gold','Goldinsel',d_gold),('grass','Grasinsel',d_grass),('stone','Stein',d_stone),('wood','Holzfloß',d_wood),('sand','Sand',d_sand),('log','Waldstamm',d_log),
   ('cloud','Wolke',d_cloud),('moss','Moos',d_moss),('ice','Eisscholle',d_ice),('shroom','Pilz',d_shroom),('desert','Wüste',d_desert),
   ('ruin','Ruine',d_ruin),('donut','Süßigkeit',d_candy),('metal','Metall',d_metal),('honey','Honig',d_honey),('crystal','Kristall',d_crystal),
   ('lava','Lava',d_lava),('rainbow','Regenbogen',d_rainbow),('spring','Feder',d_spring),('lift','Aufzug',d_lift),('crack','Bröckel',d_crack)]
# Standhöhe (logische y) je Design
STAND={'cloud':15,'shroom':12,'rainbow':18,'log':16,'spring':3,'lift':17}
import os;os.makedirs('/tmp/pd/out',exist_ok=True)
meta={}
only=sys.argv[1:] 
for key,name,f in D:
    if only and key not in only:continue
    im=f().done();bb=im.getbbox();im=im.crop(bb)
    sy=STAND.get(key,CY)
    meta[key]={'top':round((sy*K-bb[1])/im.height,3),'w':im.width,'h':im.height}
    im.save(f'/tmp/pd/out/{key}.png')
json.dump(meta,open('/tmp/pd/out/meta.json','w'),indent=0)
