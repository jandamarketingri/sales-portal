"""designs.json -> sales-portal catalog-designs.js"""
import json, re
D = json.load(open('/home/claude/catimg/designs/designs.json'))
COL = {'YEL':'Yellow','TL':'Teal','GRN':'Green','NVY':'Navy','ORA':'Orange','WHT':'White','ROY':'Royal Blue','COR':'Coral','BLK':'Black',
       'COT':'Cotton','SMK':'Smoke','JADE':'Jade','BLUE':'Blue','NV':'Navy','CHB':'Cherry Blossom',
       'OIL':'Oil Green','FUS':'Fuchsia','END':'Endive','BLA':'Blue Atoll','FLA':'Flame Orange'}
ITEM = {'PC06':'Skinny Tumbler 22 oz','PC09':'Pilsner 20 oz','PC10':'Pint 16 oz','PC11':'Coffee Mug 15 oz','PC13':'Slim Can Cooler 16 oz',
        'TC701':'Nalgene Wide Mouth 32 oz','TC704':'Nalgene Wide Mouth 16 oz'}
GARM = {'CYT':'Coyote','OLV':'Olive','BLK':'Black','CRM':'Cream','LTBL':'Light Blue','MGRY':'Medium Grey'}
out = {}
for cat, key in (('souvenir', 'souvenirs'), ('local-navy-pride', 'navy-pride')):
    rows = []
    for e in D[cat]:
        sku = e['sku']
        files = [e['file']] + e.get('more', [])
        if len(files) > 1: files = files[1:] + files[:1]     # the design tile first, the catalog's model photo second
        r = {'id': sku, 'img': ['catalog-images/%s/%s' % (cat, f) for f in files], 'th': 'catalog-images/thumbs/%s/%s' % (cat, files[0])}
        lab = e['label']
        lab = re.sub(r'\b' + re.escape(sku) + r'\b\s*', '', lab)
        lab = ' · '.join(p for p in (x.strip() for x in lab.split('·'))
                         if p and not re.match(r'^(\d+ COLOR PRINT|ORNAMENTS|UP TO \d+ THREAD COLORS)$', p, re.I))
        if 'apparel' in e:
            a = e['apparel']
            n = a['colors']; loc = a['loc']
            r['tier'] = a['tier']; r['loc'] = loc
            gm = re.search(r'\d([A-Z]{3,4})$', sku)
            bits = [lab or 'Apparel', '%s color%s, %d location%s' % (n, '' if n == '1' else 's', loc, '' if loc == 1 else 's')]
            if gm and gm.group(1) in GARM: bits.append('shown on ' + GARM[gm.group(1)])
            r['label'] = ' · '.join(bits)
        else:
            r['styles'] = e['styles']
            m = re.match(r'^(PC\d\d|TC70\d)-([A-Z]+)-', sku)
            if m: lab = COL.get(m.group(2), m.group(2)) + ' · ' + ITEM[m.group(1)]
            r['label'] = lab
        rows.append(r)
    out[key] = rows
js = ('// Ready-made designs from the NEXCOM catalogs (Souvenir and Local Navy Pride).\n'
      '// Reps pick one in the Artwork box on the order pages, instead of an art request.\n'
      '// Each entry: id = the catalog number, img = pictures (th = small one), and either\n'
      '//   styles: the items it goes on (without the SVN/LNP prefix), or\n'
      '//   tier + loc: apparel, any garment, printed in that many ink colors and locations.\n'
      '// Made from the catalog PDFs; the pictures are in catalog-images/.\n'
      'var CATALOG_DESIGNS = ' + json.dumps(out, indent=0, ensure_ascii=False).replace('\n', '') + ';\n')
js = js.replace('}, {', '},\n{').replace('[{', '[\n{')
open('/home/claude/sales-portal-test/catalog-designs.js', 'w').write(js)
print(len(js), {k: len(v) for k, v in out.items()})
