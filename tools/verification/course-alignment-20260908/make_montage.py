"""Contact sheets for review; full-resolution screenshots remain alongside."""
from pathlib import Path
from PIL import Image, ImageOps, ImageDraw, ImageFont
import math
ROOT=Path(__file__).resolve().parent
font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',13)
def sheet(paths,dest,cols=3,cell=(370,325),crop=False):
    canvas=Image.new('RGB',(cols*cell[0],math.ceil(len(paths)/cols)*cell[1]),'#eef0f3')
    draw=ImageDraw.Draw(canvas)
    for i,p in enumerate(paths):
        im=Image.open(p).convert('RGB')
        if crop: im=im.crop((0,0,im.width,min(900,im.height)))
        im.thumbnail((cell[0]-16,cell[1]-44))
        x=(i%cols)*cell[0];y=(i//cols)*cell[1]
        canvas.paste(im,(x+(cell[0]-im.width)//2,y+30))
        draw.text((x+8,y+7),p.stem,font=font,fill='#1c2940')
    canvas.save(ROOT/dest)
paths=sorted((ROOT/'visual-review').glob('w01iv*.png'))
assert len(paths)==12,len(paths)
sheet(paths,'intro-all-plots.png')
paths=[]
for p in sorted((ROOT/'screenshots').glob('*.png')):
    if p.stem.endswith('_mobile'):continue
    final=ROOT/'visual-review'/p.name
    paths.append(final if final.exists() else p)
assert len(paths)==27,len(paths)
sheet(paths,'all-pages-overview.png',cols=4,cell=(275,245),crop=True)
print('Created contact sheets: 12 full plots; 27 page opening viewports (home plus 26 teaching pages). Full-page originals retained.')
