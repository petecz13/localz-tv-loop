"""Builds the two holiday menu TV slides (deploy/Holiday Turkey.html, deploy/Holiday Drinks.html).
Edit MENUS and re-run: python3 tools/holiday_menu_slides.py"""
import html, os
DATES = "Mon. Nov. 23 &ndash; Thu. Dec. 31"
MENUS = [
  {"file": "Holiday Turkey.html", "kicker": "Christmas at Localz", "title": ["Holiday", "Turkey"], "items": [
    ("The Turkey Gobbler", "$14", "Sliced turkey breast and stuffing piled on a hoagie roll with cranberry aioli.", [("red","Gravy for dipping"),("gold","Served with fries or coleslaw")]),
    ("The Holidilla", "$13", "Turkey, stuffing and melted Monterey Jack cheese with cranberry aioli.", [("red","Gravy for dipping")]),
    ("Turkey BLT", "$15", "Turkey, thick-cut bacon, lettuce and tomato with cranberry aioli on thick-sliced challah bread.", [("gold","Served with fries or coleslaw")]),
  ]},
  {"file": "Holiday Drinks.html", "kicker": "Cheers from Localz", "title": ["Holiday", "Drinks"], "items": [
    ("Apple Cider Old Fashioned", "$13", "Jim Beam bourbon, apple cider, Angostura bitters, apple slice, cinnamon stick", []),
    ("Mistletoe Margarita", "$12", "Los Sundays tequila, triple sec, fresh lime, white cranberry, sugar rim, frozen cranberries, rosemary", []),
    ("Coconut Coquito", "$11", "Captain Morgan Coconut, Fireball, cream of coconut, half &amp; half, cinnamon sugar rim", []),
  ], "feature": ("Holiday Dessert", "Deep-Fried Pumpkin Pie", "$8", "Battered and fried, whipped cream, caramel drizzle")},
]
TPL = open(os.path.join(os.path.dirname(__file__), "holiday_menu_template.html")).read()
def item(name, price, desc, tags):
    pre = "".join(f'<span class="tag {k}">{t}</span>' for k,t in tags if k=="treat")
    post = "".join(f'<span class="tag {k}">{t}</span>' for k,t in tags if k!="treat")
    return (f'<div class="item">{pre and "<div class=tags>"+pre+"</div>"}<div class="row"><div class="name">{name}</div>'
            f'<div class="price">{price}</div></div><div class="desc">{desc}</div>'
            f'{post and "<div class=tags>"+post+"</div>"}</div>')
for m in MENUS:
    out = (TPL.replace("{{TITLE_TAG}}", " ".join(m["title"])).replace("{{KICKER}}", m["kicker"])
           .replace("{{T1}}", m["title"][0]).replace("{{T2}}", m["title"][1]).replace("{{DATES}}", DATES)
           .replace("{{COUNT}}", str(len(m["items"]))).replace("{{ITEMS}}", "\n".join(item(*i) for i in m["items"])))
    f = m.get("feature")
    feat = (f'<div class="feature"><div class="flabel">&#10052; {f[0]} &#10052;</div><div class="row"><div class="name">{f[1]}</div>'
            f'<div class="price">{f[2]}</div></div><div class="desc">{f[3]}</div></div>') if f else ""
    out = out.replace("{{FEATURE}}", feat).replace("{{HASFEAT}}", " hasfeat" if f else "")
    open(os.path.join(os.path.dirname(__file__), "..", "deploy", m["file"]), "w").write(out)
    print("wrote", m["file"])
