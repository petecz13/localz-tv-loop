#!/usr/bin/env python3
"""Generate every Localz food slide from one data list + one template.

Edit MENU below (text, prices, photos), then run:
    python3 tools/food_slides.py            # writes deploy/food/*.html
Layout is chosen with LAYOUT ('A' or 'B').
"""
import html, json, os, sys
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEPLOY = os.path.join(ROOT, 'deploy')
OUTDIR = os.path.join(DEPLOY, 'food')
LAYOUT = os.environ.get('LAYOUT', 'A')

NAVY, GOLD, RED = '#0C2340', '#F2AF32', '#C8102E'

HH = {'badge': ('&frac12; Price', 'At Happy Hour', '3&ndash;6 PM &middot; Mon&ndash;Fri')}
SIDE = 'Served with your choice of side'
WING_SIDE = 'Served with carrots, celery &amp; bleu cheese or ranch'

# footer tagline per category
TAG = {
    'philly': 'Phillyz &bull; Steakz &bull; Hoagiez',
    'burger': 'Burgerz &bull; Sandwichz &bull; Sidez',
    'sandwich': 'Burgerz &bull; Sandwichz &bull; Sidez',
    'wrap': 'Wrapz &bull; Saladz &bull; Fresh Daily',
    'salad': 'Wrapz &bull; Saladz &bull; Fresh Daily',
    'wings': 'Wingz &bull; Sauces &bull; Game Day',
    'app': 'Appz &bull; Totz &bull; Shareablez',
    'dog': 'Wiener Wednesday &bull; Nathan&rsquo;s All-Beef',
    'taco': 'Tacos &bull; Cervezas &bull; Margs',
}

MENU = [
 # file, category, eyebrow, top, bottom, description, chips, extra
 dict(file='Philly Cheesesteak', cat='philly', eyebrow='Signature Philly', top='Philly', bottom='Cheesesteak',
      desc='Shaved ribeye, American cheese, saut&eacute;ed onions &amp; peppers and house queso on a toasted hoagie roll.',
      chips=['8&Prime; &middot; 12&Prime;', SIDE], photo='philly cheesesteak.webp'),
 dict(file='Philly Fire Cheesesteak', cat='philly', eyebrow='Signature Philly', top='Philly Fire', bottom='Steak', spicy=True,
      desc='Shaved ribeye, ghost pepper cheese, saut&eacute;ed onions &amp; peppers, chipotle lime aioli and crispy jalape&ntilde;o strips, finished with house queso.',
      chips=['8&Prime; &middot; 12&Prime;', SIDE], photo='philly-fire-photo.webp'),
 dict(file='Double Bacon Philly', cat='philly', eyebrow='Signature Philly', top='Double Bacon', bottom='Philly',
      desc='Chopped ribeye, American cheese, saut&eacute;ed onions &amp; peppers, queso, crumbled bacon and bacon aioli on a toasted hoagie roll.',
      chips=['8&Prime; &middot; 12&Prime;', SIDE], photo='double-bacon-philly.webp'),
 dict(file='DTSP Burger', cat='burger', eyebrow='Signature Burgerz', top='DTSP', bottom='Burger',
      desc='Two half-pound Angus patties layered with American and cheddar, crispy bacon, lettuce, tomato and onion, finished with our house bacon aioli.',
      chips=[SIDE], photo='c098461d-7596-469a-9adf-7889eb06c0d0.webp'),
 dict(file='Beach Drive Burger Neon', cat='burger', eyebrow='Signature Burgerz', top='Beach Drive', bottom='Burger',
      desc='A half-pound all-beef patty smothered in melted Swiss and roasted garlic mushrooms, finished with a zesty horseradish aioli on a toasted brioche bun.',
      chips=[SIDE, 'Try it with fried Brussels sproutz'], photo='beach-drive-burger-cutout-trim.webp'),
 dict(file='Hot Honey Chicken', cat='sandwich', eyebrow='Signature Sandwichz', top='Hot Honey', bottom='Chicken', spicy=True,
      desc='Hand-breaded crispy chicken breast drizzled in hot honey, stacked with smoky bacon, melted cheddar and a fried egg on a toasted brioche bun.',
      chips=[SIDE], photo='hot-honey-chicken-trim.webp'),
 dict(file='Chicken Club', cat='sandwich', eyebrow='Signature Sandwichz', top='Chicken', bottom='Club',
      desc='Grilled chicken breast, American cheese, bacon, lettuce, tomato, red onion and bacon aioli on a brioche bun.',
      chips=[SIDE], photo='chicken-club-trim.webp'),
 dict(file='Bacon Chicken Ranch Wrap', cat='wrap', eyebrow='Signature Wrapz', top='Bacon Chicken', bottom='Ranch Wrap',
      desc='Grilled or fried chicken breast, crispy bacon, romaine, tomato and Monterey Jack with house-made ranch, pressed in a flour tortilla.',
      chips=[SIDE], photo='bacon-chicken-ranch-wrap-trim.webp'),
 dict(file='Beach Drive Chicken Wrap', cat='wrap', eyebrow='Signature Wrapz', top='Beach Drive', bottom='Chicken Wrap',
      desc='Grilled or fried chicken breast, Swiss, lettuce, tomato, saut&eacute;ed mushrooms &amp; onions with horseradish aioli, pressed in a flour tortilla.',
      chips=[SIDE], photo='beach-drive-wrap-trim.webp'),
 dict(file='Buffalo Garlic Parm Shrimp Wrap', cat='wrap', eyebrow='Signature Wrapz', top='Buffalo Garlic Parm', bottom='Shrimp Wrap',
      desc='Crispy fried shrimp, lettuce, tomato and buffalo garlic parmesan sauce with bleu cheese or ranch, pressed in a flour tortilla.',
      chips=[SIDE], photo='bgp-shrimp-wrap-v2-trim.webp'),
 dict(file='Spicy Southwest Shrimp Wrap', cat='wrap', eyebrow='Signature Wrapz', top='Spicy Southwest', bottom='Shrimp Wrap', spicy=True,
      desc='Blackened shrimp, ghost pepper cheese, lettuce, pico de gallo and black bean &amp; corn salsa with roasted jalape&ntilde;o ranch, pressed in a flour tortilla.',
      chips=[SIDE], photo='spicy-shrimp-wrap-trim.webp'),
 dict(file='Avocado Caesar Chicken Wrap', cat='wrap', eyebrow='Signature Wrapz', top='Avocado Caesar', bottom='Chicken Wrap',
      desc='Grilled chicken breast, crisp romaine, shaved parmesan and our house-made avocado Caesar dressing, pressed in a flour tortilla.',
      chips=[SIDE], photo='avocado-caesar-wrap-trim.webp'),
 dict(file='Spicy Southwest Shrimp Salad', cat='salad', eyebrow='Signature Saladz', top='Spicy Southwest', bottom='Shrimp Salad', spicy=True,
      desc='Romaine with blackened jumbo shrimp, pico de gallo, black bean &amp; corn salsa, ghost pepper cheese and crispy jalape&ntilde;o strips.',
      chips=['Roasted jalape&ntilde;o ranch'], photo='southwest-shrimp-salad-trim.webp'),
 dict(file='House Avocado Caesar Salad', cat='salad', eyebrow='Signature Saladz', top='Avocado', bottom='Caesar Salad',
      desc='Crisp romaine, shredded parmesan and fresh tomato in our house-made avocado Caesar dressing, topped with garlic croutons.',
      chips=['Add grilled chicken', 'Add shrimp'], photo='AVOCADO CAESAR SALAD-trim.webp'),
 dict(file='Blackened Chicken Cobb Salad', cat='salad', eyebrow='Signature Saladz', top='Blackened Chicken', bottom='Cobb Salad',
      desc='Spinach with blackened chicken, tomato, cucumber, red onion, avocado, bacon, bleu cheese crumbles and garlic croutons.',
      chips=['Choice of dressing'], photo='BLACKENED CHICKEN COBB-trim.webp'),
 dict(file='Buffalo Chicken Salad', cat='salad', eyebrow='Signature Saladz', top='Buffalo Chicken', bottom='Salad',
      desc='Romaine, buffalo chicken breast, tomato, cucumber, red onion, bleu cheese crumbles and crispy onion straws.',
      chips=['Choice of dressing'], photo='buffalo-chicken-salad.webp'),
 dict(file='Chicken Taco Salad', cat='salad', eyebrow='Localz Original', top='Chicken Taco', bottom='Salad', spicy=True,
      desc='Taco bowl, romaine, diced chicken, Monterey Jack, pico de gallo, black bean &amp; corn salsa and crispy jalape&ntilde;o strips.',
      chips=['Roasted jalape&ntilde;o ranch'], photo='chicken-taco-salad.webp'),
 dict(file='Roasted Beet Salad', cat='salad', eyebrow='Signature Saladz', top='Roasted Beet', bottom='Salad',
      desc='Spinach, goat cheese, black bean &amp; corn salsa, roasted beets and crispy onion straws.',
      chips=['House balsamic vinaigrette'], photo='roasted-beet-salad.webp'),
 dict(file='Chicago Dog', cat='dog', eyebrow='Wiener Wednesday', top='Chicago', bottom='Dog',
      desc='A half-pound jumbo Nathan&rsquo;s all-beef hot dog dragged through the garden: relish, pickle, tomato, red onion, sport peppers, mustard and celery salt.',
      chips=['Wednesdays only'], photo='CHICAGO DOG cutout.webp'),
 dict(file='South Philly Dog', cat='dog', eyebrow='Wiener Wednesday', top='South Philly', bottom='Dog',
      desc='A half-pound jumbo Nathan&rsquo;s all-beef hot dog loaded cheesesteak-style with chopped ribeye, saut&eacute;ed onions &amp; peppers and warm queso.',
      chips=['Wednesdays only'], photo='SOUTH PHILLY DOG cutout.webp'),
 dict(file='Bacon Chicken Ranch Taco', cat='taco', eyebrow='Taco Tuesday', top='Bacon Chicken', bottom='Ranch Tacoz',
      desc='Three tacoz stacked with diced chicken, Monterey Jack, lettuce, tomato, crispy bacon and buttermilk ranch. Served with chipz &amp; queso or pico.',
      chips=['Tuesdays only'], photo='b7023890-b0ec-4aaa-9d82-d10abb98bc55-trim.webp'),
 dict(file='Buffalo Garlic Parm Wingz Bone-In', cat='wings', eyebrow='Bone-In Wingz', top='Buffalo Garlic', bottom='Parm Wingz',
      desc='Crispy bone-in wings tossed in our buffalo garlic parmesan sauce and finished with shredded parmesan.',
      chips=[WING_SIDE], photo='wing-bgp-bonein.webp'),
 dict(file='Localz Dry Rub Wingz Bone-In', cat='wings', eyebrow='Bone-In Wingz', top='Localz', bottom='Dry Rub Wingz',
      desc='Crispy bone-in wings dusted in our signature Localz dry rub.',
      chips=[WING_SIDE], photo='wing-dryrub-bonein.webp'),
 dict(file='Peach Mango Habanero Wingz Bone-In', cat='wings', eyebrow='Bone-In Wingz', top='Peach Mango', bottom='Habanero Wingz', spicy=True,
      desc='Crispy bone-in wings glazed in sweet-and-spicy peach mango habanero sauce.',
      chips=[WING_SIDE], photo='wing-peachmango-bonein.webp'),
 dict(file='Buffalo Garlic Parm Wingz Boneless', cat='wings', eyebrow='Boneless Wingz', top='Buffalo Garlic', bottom='Parm Boneless',
      desc='Crispy boneless wings tossed in our buffalo garlic parmesan sauce and finished with shredded parmesan.',
      chips=[WING_SIDE], photo='wing-bgp-boneless.webp'),
 dict(file='Boneless Wingz', cat='wings', eyebrow='Boneless Wingz', top='Honey BBQ', bottom='Boneless',
      desc='Crispy boneless wings tossed in sweet honey barbecue sauce.',
      chips=[WING_SIDE, 'Toss in any Localz sauce'], photo='boneless-wings.webp'),
 dict(file='Chicken Quesadilla', cat='app', eyebrow='Appetizerz', top='Chicken', bottom='Quesadilla',
      desc='12&Prime; flour tortilla stuffed with Monterey Jack, marinated diced chicken and pico de gallo. Served with sour cream.',
      chips=[], photo='quesadilla-clean.webp', **HH),
 dict(file='Crispy Potato Skins', cat='app', eyebrow='Appetizerz', top='Crispy Loaded', bottom='Potato Skinz',
      desc='Fried potato skins piled with Monterey Jack, house queso, bacon and Localz dry rub, finished with sour cream and scallions.',
      chips=[], photo='crispy-potato-skins.webp', **HH),
 dict(file='Pretzel Bites', cat='app', eyebrow='Appetizerz', top='Dry Rub', bottom='Pretzel Bitez',
      desc='Fried pretzel bites tossed in our Localz dry rub, served with house queso for dipping.',
      chips=[], photo='pretzel-bites.webp', **HH),
 dict(file='Fried Pickles', cat='app', eyebrow='Appetizerz', top='Hand-Breaded', bottom='Fried Picklez',
      desc='Golden hand-breaded dill pickle chips fried crisp, served with cool ranch for dipping.',
      chips=[], photo='fried-pickles-trim.webp', **HH),
 dict(file='Philly Tots', cat='app', eyebrow='Tater Totz', top='Philly Cheesesteak', bottom='Totz',
      desc='Crispy golden tots piled high with chopped steak, saut&eacute;ed onions, melty cheese and creamy queso, topped with scallions.',
      chips=['Game day loaded'], photo='philly-tots.webp'),
 dict(file='Bacon Localz Totz', cat='app', eyebrow='Tater Totz', top='Bacon', bottom='Localz Totz',
      desc='Crispy tater tots piled with shredded cheddar, house queso, crumbled bacon and Localz dry rub, finished with ranch and scallions.',
      chips=['Fan favorite'], photo='loaded-tots-trim.webp'),
 dict(file='Lemon Pepper Goat Sproutz', cat='app', eyebrow='Brussels Sproutz', top='Lemon Pepper &amp; Goat', bottom='Sproutz',
      desc='Crispy fried Brussels sprouts tossed in lemon pepper, finished with crumbled goat cheese and scallions.',
      chips=['Add as a side to any sandwich'], photo='fried-brussels.webp'),
]


def is_cutout(photo):
    p = os.path.join(DEPLOY, 'uploads', photo)
    try:
        im = Image.open(p)
    except FileNotFoundError:
        return False
    if im.mode not in ('RGBA', 'LA'):
        return False
    a = im.getchannel('A')
    w, h = a.size
    corners = [a.getpixel((2, 2)), a.getpixel((w - 3, 2)), a.getpixel((2, h - 3)), a.getpixel((w - 3, h - 3))]
    return sum(c < 40 for c in corners) >= 3


HEAD = """<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link href="https://fonts.googleapis.com/css2?family=Anton&family=Barlow+Condensed:wght@600;700;800&family=Barlow+Semi+Condensed:wght@500;600&display=swap" rel="stylesheet">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:100%;height:100%;background:#000;overflow:hidden}}
#stage{{position:absolute;left:50%;top:50%;width:1920px;height:1080px;overflow:hidden;transform-origin:center;
  transform:translate(-50%,-50%);font-family:'Barlow Semi Condensed',sans-serif;color:#fff}}
.fit{{white-space:nowrap;display:inline-block}}
.ey{{display:flex;align-items:center;gap:22px;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:36px;letter-spacing:9px;text-transform:uppercase;color:#9fb6d6}}
.ey i{{width:70px;height:4px;background:{gold}}}
.t1{{font-family:'Anton',sans-serif;text-transform:uppercase;color:#fff;line-height:.98}}
.t2{{font-family:'Anton',sans-serif;text-transform:uppercase;color:{gold};line-height:.98;text-shadow:0 0 34px rgba(242,175,50,.35)}}
.desc{{font-weight:500;font-size:38px;line-height:1.34;color:#d7e2f0;text-wrap:pretty}}
.chips{{display:flex;flex-wrap:wrap;gap:18px}}
.chip{{border:3px solid {gold};border-radius:12px;padding:12px 26px;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:32px;letter-spacing:2px;text-transform:uppercase;color:#fff}}
.spicy{{display:inline-flex;align-items:center;gap:10px;background:{red};border-radius:10px;padding:8px 20px;font-family:'Barlow Condensed',sans-serif;font-weight:800;font-size:28px;letter-spacing:4px;text-transform:uppercase;color:#fff}}
.foot{{position:absolute;bottom:0;left:0;right:0;height:110px;display:flex;align-items:center;gap:30px;padding:0 70px;background:{navy};border-top:4px solid {gold};z-index:5}}
.foot img{{height:92px}}
.foot .tag{{font-family:'Anton',sans-serif;font-size:40px;letter-spacing:4px;text-transform:uppercase;color:{gold}}}
.foot .url{{margin-left:auto;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:30px;letter-spacing:5px;color:#9fb6d6}}
.badge{{position:absolute;z-index:4;background:linear-gradient(160deg,#d81f2f,#a50e1c);border:4px solid {gold};border-radius:16px;padding:16px 34px;text-align:center;transform:rotate(-4deg);box-shadow:0 18px 40px rgba(0,0,0,.45)}}
.badge b{{display:block;font-family:'Anton',sans-serif;font-weight:400;font-size:84px;line-height:1;color:{gold}}}
.badge span{{display:block;font-family:'Anton',sans-serif;font-size:40px;letter-spacing:3px;text-transform:uppercase;color:#fff}}
.badge em{{display:block;font-style:normal;margin-top:4px;font-family:'Barlow Condensed',sans-serif;font-weight:700;font-size:26px;letter-spacing:3px;text-transform:uppercase;color:#ffe2a6}}
{extra_css}
</style></head><body>
<div id="stage">
"""

TAIL = """
<div class="foot"><img src="../uploads/St.peteLogo.webp" alt="Localz"><span class="tag">{tag}</span><span class="url">WWW.LOCALZSPORTSBAR.COM</span></div>
</div>
<script>
// shrink any .fit line until it fits its box, then scale the 1920x1080 stage to the screen
function shrink(){{document.querySelectorAll('.fit').forEach(function(el){{
  var max=+el.dataset.max, fs=+el.dataset.fs; el.style.fontSize=fs+'px';
  while(el.offsetWidth>max && fs>40){{fs-=4; el.style.fontSize=fs+'px';}}
}});}}
shrink(); if(document.fonts){{document.fonts.ready.then(shrink);document.fonts.onloadingdone=shrink;}} setTimeout(shrink,1000); setTimeout(shrink,3000);
function fit(){{var s=Math.min(innerWidth/1920,innerHeight/1080);document.getElementById('stage').style.transform='translate(-50%,-50%) scale('+s+')';}}
fit(); addEventListener('resize',fit);
</script>
</body></html>
"""


def text_block(it, maxw):
    sp = '<div class="spicy" style="margin-bottom:22px">&#127798; Spicy</div>' if it.get('spicy') else ''
    chips = ''.join(f'<div class="chip">{c}</div>' for c in it['chips'])
    return f"""
  <div class="ey"><i></i>{it['eyebrow']}</div>
  <div style="margin-top:26px">
    <span class="t1 fit" data-fs="120" data-max="{maxw}">{it['top']}</span><br>
    <span class="t2 fit" data-fs="176" data-max="{maxw}">{it['bottom']}</span>
  </div>
  <p class="desc" style="margin-top:28px;max-width:{maxw}px">{it['desc']}</p>
  <div style="margin-top:36px">{sp}<div class="chips">{chips}</div></div>"""


def badge(it, pos):
    if 'badge' not in it:
        return ''
    a, b, c = it['badge']
    return f'<div class="badge" style="{pos}"><b>{a}</b><span>{b}</span><em>{c}</em></div>'


def photo_html(it, box, cut):
    src = '../uploads/' + it['photo']
    if cut:
        return (f'<div style="position:absolute;{box};display:flex;align-items:center;justify-content:center">'
                f'<div style="position:absolute;inset:6%;border-radius:50%;background:radial-gradient(circle,rgba(242,175,50,.38),rgba(242,175,50,0) 68%)"></div>'
                f'<img src="{src}" style="position:relative;max-width:100%;max-height:100%;object-fit:contain;filter:drop-shadow(0 30px 40px rgba(0,0,0,.6))"></div>')
    return (f'<div style="position:absolute;{box};border-radius:28px;overflow:hidden;border:5px solid {GOLD};box-shadow:0 30px 60px rgba(0,0,0,.55)">'
            f'<img src="{src}" style="width:100%;height:100%;object-fit:cover"></div>')


def layout_a(it, cut):
    css = f"#stage{{background:radial-gradient(90% 100% at 75% 45%,#1b3d6e 0%,{NAVY} 55%,#071528 100%)}}"
    body = (f'<div style="position:absolute;top:0;left:0;right:0;height:6px;background:{GOLD}"></div>'
            f'<div style="position:absolute;left:90px;top:6px;bottom:116px;width:900px;display:flex;flex-direction:column;justify-content:center"><div>{text_block(it, 880)}</div></div>'
            + photo_html(it, 'left:1010px;top:70px;width:850px;height:830px' if cut else 'left:1060px;top:110px;width:760px;height:760px', cut)
            + badge(it, 'right:70px;top:60px'))
    return css, body


def layout_b(it, cut):
    css = (f"#stage{{background:{NAVY}}}"
           f".panel{{position:absolute;top:0;bottom:0;right:0;width:900px;background:radial-gradient(80% 80% at 60% 45%,#ffc95a,{GOLD} 55%,#c98a0f);"
           f"clip-path:polygon(18% 0,100% 0,100% 100%,0 100%)}}"
           f".panel:before{{content:'';position:absolute;inset:0;background:repeating-linear-gradient(120deg,transparent 0 22px,rgba(0,0,0,.04) 22px 24px)}}"
           f".edge{{position:absolute;top:0;bottom:0;right:900px;width:0}}")
    body = (f'<div style="position:absolute;inset:0;background:radial-gradient(70% 90% at 20% 40%,#173764,{NAVY} 70%)"></div>'
            f'<div class="panel"></div>'
            f'<div style="position:absolute;left:90px;top:6px;bottom:116px;width:900px;display:flex;flex-direction:column;justify-content:center"><div>{text_block(it, 880)}</div></div>'
            + photo_html(it, 'left:960px;top:60px;width:900px;height:860px' if cut else 'left:1080px;top:120px;width:740px;height:740px', cut)
            + badge(it, 'left:1000px;bottom:150px'))
    return css, body


def build(it):
    cut = is_cutout(it['photo'])
    css, body = (layout_a if LAYOUT == 'A' else layout_b)(it, cut)
    title = html.unescape(f"{it['top']} {it['bottom']}")
    return (HEAD.format(title=html.escape(title), gold=GOLD, navy=NAVY, red=RED, extra_css=css)
            + body + TAIL.format(tag=TAG[it['cat']]))


def main(only=None):
    os.makedirs(OUTDIR, exist_ok=True)
    out = []
    for it in MENU:
        if only and it['file'] not in only:
            continue
        p = os.path.join(OUTDIR, it['file'] + '.html')
        open(p, 'w').write(build(it))
        out.append(p)
    return out


if __name__ == '__main__':
    for p in main(sys.argv[1:] or None):
        print(p)
