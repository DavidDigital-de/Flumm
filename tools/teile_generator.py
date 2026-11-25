import sys;sys.argv=['x','none']
exec(open('/tmp/pd/gen3.py').read().split("import os;os.makedirs")[0])
from PIL import Image
import math
P['feather']=['#FFFFFF','#F3F6FF','#DCE4F5','#BCC8E3','#98A6C8','#7A87AD']
P['jelly']=['#FFE3F0','#FFB3D3','#FF86B8','#F05A9A','#C93D78','#9C2A5C']
P['thr']=['#E9DCFF','#C6A6FF','#9E73F2','#7A4FD6','#5833AA']
def wing():
    c=C()
    def fn(x,y,X,Y):
        # Flügel nach links ausgebreitet, Ansatz rechts bei (70,30)
        for i,(len_,ang,w) in enumerate([(50,1.0,6.5),(46,.72,6.5),(40,.45,6),(32,.2,5.5)]):
            ax,ay=70,52;dx=-math.cos(ang);dy=-math.sin(ang)
            px,py=x-ax,y-ay;t=px*dx+py*dy;d=abs(-px*dy+py*dx)
            if 0<=t<=len_:
                ww=w*(1-(t/len_)**2.5)+1
                if d<=ww:
                    s=1+i*.5+(d/ww)*1.2+(t/len_)*.6
                    if d/ww<.2:s+=1.2
                    return pick(P['feather'],s,X,Y)
        dx,dy=(x-68)/9,(y-52)/7
        if dx*dx+dy*dy<=1:return pick(P['feather'],1+(dy+1),X,Y)
    c.fill(fn);return c
def thruster():
    c=C()
    def fn(x,y,X,Y):
        # Kristall-Antrieb: Metallring + Kristall
        dx,dy=(x-42)/14,(y-12)/5
        if dx*dx+dy*dy<=1:return pick(P['metal'],1.5+(dy+1)*1.5+max(0,dx),X,Y)
        if abs(x-42)<12*(1-(y-12)/16) and 12<=y<28:
            u=(x-42)/12;return pick(P['thr'],1+abs(u)*2+(y-12)/8+(.8 if u>0 else 0),X,Y)
    c.fill(fn);return c
def jelly():
    c=C()
    def fn(x,y,X,Y):
        dx=(x-42)/38;dy=(y-24)/14
        if dx*dx+dy*dy<=1 and y<=27:
            s=(dy+1)*1.3+max(0,dx)*1.2
            if (dx+.45)**2*3+(dy+.55)**2*6<.12:return hx('#FFFFFF')
            return pick(P['jelly'],s,X,Y)
        if abs(dx)<1 and 27<y<=30:return pick(P['jelly'],3.2+max(0,dx),X,Y)
    c.fill(fn);return c
import json
meta={}
for k,f in [('wing',wing),('thruster',thruster),('jelly',jelly)]:
    im=f().done();bb=im.getbbox();im=im.crop(bb);im.save(f'/tmp/pd/out/{k}.png');im.save(f'/tmp/pd/out/{k}.webp',quality=92,method=6);meta[k]=[im.width,im.height]
print(meta)
sh=Image.new('RGBA',(900,300),(120,190,255,255))
x=10
for k in meta:
    im=Image.open(f'/tmp/pd/out/{k}.png');sh.alpha_composite(im,(x,10));x+=im.width+20
sh.save('/tmp/pd/parts.png')
