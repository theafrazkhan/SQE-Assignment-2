"""Draw the starter function's expanded CFG with Pillow; no external renderer."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
ROOT=Path(__file__).resolve().parents[1]
img=Image.new('RGB',(1500,2100),'white')
d=ImageDraw.Draw(img)
font_path='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
font=ImageFont.truetype(font_path,20)
small=ImageFont.truetype(font_path,17)
bold=ImageFont.truetype(font_path,28)
d.text((40,25),'registration_decision() - original starter CFG',fill='black',font=bold)
d.text((40,70),'Expanded short-circuit comparisons; explicit returns/raises share one exit.',fill='black',font=font)
# A and B are the chained comparisons inside NOT(A AND B) OR C.
labels=[('D1','dues < 0?','T'),('A','0 <= enrolled?','F'),('B','enrolled <= capacity?','F'),
        ('C','capacity < 1?','T'),('D3','dues > 1000?','T'),('D4','already registered?','T'),
        ('D5','NOT prerequisites_satisfied?','T'),('D6','NOT check_credit_limit?','T'),('D7','enrolled > capacity?','T')]
ys=[260+i*175 for i in range(9)]
returns={0:(1000,ys[0],'R1: raise Invalid dues'),1:(1000,ys[2],'R2: raise Invalid capacity / enrollment'),
         4:(1000,ys[4],'R3: DUES_BLOCK'),5:(1000,ys[5],'R4: ALREADY_REGISTERED'),
         6:(1000,ys[6],'R5: PREREQUISITES_MISSING'),7:(1000,ys[7],'R6: CREDIT_LIMIT'),8:(1000,ys[8],'R7: WAITLISTED (infeasible)')}
def arrow(points,label=None):
    d.line(points,fill='#45535e',width=3)
    x,y=points[-1]; px,py=points[-2]
    if x>px: tri=[(x,y),(x-10,y-6),(x-10,y+6)]
    elif y>py: tri=[(x,y),(x-6,y-10),(x+6,y-10)]
    else: tri=[(x,y),(x-6,y+10),(x+6,y+10)]
    d.polygon(tri,fill='#45535e')
    if label: d.text((points[0][0]+12,points[0][1]+8),label,fill='black',font=small)
def box(cx,cy,text,width=470):
    d.rounded_rectangle((cx-width/2,cy-32,cx+width/2,cy+32),radius=8,outline='#244766',width=2,fill='#eef3f6')
    d.text((cx,cy),text,anchor='mm',fill='black',font=small)
box(365,140,'ENTRY',220)
arrow([(365,172),(365,ys[0]-58)])
for i,(id,label,side) in enumerate(labels):
    y=ys[i]
    d.polygon([(365,y-58),(670,y),(365,y+58),(60,y)],outline='#244766',fill='#f3f6f9',width=2)
    d.text((365,y),id+': '+label,anchor='mm',fill='black',font=small)
    dest=returns[1] if i in (1,2,3) else returns[i]
    x2,y2,_=dest
    arrow([(670,y),(720,y),(720,y2),(765,y2)],side)
    if i<8:
        arrow([(365,y+58),(365,ys[i+1]-58)],'F' if side=='T' else 'T')
    else:
        arrow([(365,y+58),(365,1900-32)],'F')
for _,(x,y,label) in returns.items():
    box(x,y,label)
    arrow([(1235,y),(1370,y),(1370,2010),(650,2010)])
box(365,1900,'R8: REGISTERED')
arrow([(365,1932),(365,1978)])
box(365,2010,'EXIT',570)
d.text((40,2060),'N=19, E=27: V(G)=27-19+2=10; 9 predicate nodes + 1 = 10.',fill='black',font=font)
img.save(ROOT/'docs/cfg.png')
print('Created cfg.png')
