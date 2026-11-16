"""Build catalog-designs.js: which generic portal item each catalog design goes on."""
import pymupdf as fitz, json, re, sys
PDF = {'souvenir': '/mnt/user-data/uploads/Downloads/NEXCOM DSD Souvenir Catalog V2.pdf',
       'local-navy-pride': '/mnt/user-data/uploads/Downloads/NEXCOM DSD LNP Catalog.pdf'}
IMG = json.load(open('/home/claude/sales-portal-test/catalog-images/images.json'))
CLR = re.compile(r'(\d(?:-\d)?)\s+COLORS?\s*-\s*(\d)\s+LOCATION', re.I)

def styles_for(sku):
    """Generic items (without the SVN/LNP prefix) a catalog design can go on. None = apparel."""
    s = sku.upper()
    if re.match(r'^(762|BAT)-', s): return None
    if s.startswith('HAT-T'): return ['PTCHCAP']
    if s.startswith('HAT-'): return ['TWLCAP', 'TWL36CAP']
    if re.match(r'^B?EAR12HD-', s): return ['BEAR6', 'BEAR10HD', 'BEAR12HD']
    if s.startswith('BEAR12-'): return ['BEAR10', 'BEAR12']
    if s.startswith('J37-T-'): return ['J37-T', 'J37-MAG']
    if s.startswith('024-'): return ['024-6146 ASST']
    m = re.match(r'^(003-\d{4})-', s)
    if m: return [m.group(1) + '-DE']
    if s.startswith('SS-1-'): return ['SS1']
    if s.startswith('TC825-'): return ['TC825-WH']
    m = re.match(r'^(PC\d\d|TC70\d)-', s)
    if m: return [m.group(1)]
    m = re.match(r'^VD12X(6|12)-', s)
    if m: return ['VD12x' + m.group(1)]
    m = re.match(r'^(.+)-T?\d{4}$', s)
    return [m.group(1)] if m else []

def tier(n):
    lo = int(n.split('-')[0])
    return '1-2' if lo <= 2 else '3-5' if lo <= 5 else '6-9'

out = {}
for cat, path in PDF.items():
    doc = fitz.open(path); found = {}
    def lines_of(page):
        out = []
        for b in page.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                t = ''.join(sp['text'] for sp in l['spans']).strip()
                if t: out.append((l['bbox'], t))
        return out
    for pno, page in enumerate(doc, 1):
        blocks = [b for b in page.get_text('blocks') if b[4].strip()]
        words = page.get_text('words'); plines = lines_of(page)
        # a SKU can be split over two words ("PC09-NVY 4628") — join neighbours on one line
        toks = []
        for i, w in enumerate(words):
            toks.append((w[4], w))
            if i + 1 < len(words) and abs(words[i+1][1] - w[1]) < 2 and re.match(r'^\d{4}$', words[i+1][4]):
                toks.append((w[4] + '-' + words[i+1][4], w))
        for t, w in toks:
            t = t.strip('|,')
            found.setdefault(t, []).append((pno, w, blocks, plines))
    rec = []
    for im in IMG[cat]['images']:
        sku = im['sku']
        occ = found.get(sku) or []
        label, colors, locs, prints = '', None, None, ''
        def colour_for(o):
            pno, w, blocks, lines = o
            best = None
            for bb, t in lines:
                m = CLR.search(t)
                if not m: continue
                dx, dy = bb[0] - w[0], bb[1] - w[1]
                if dy <= 0 or not (-15 < dx < 95): continue
                if best is None or dy < best[0]: best = (dy, m)
            return best[1] if best else None
        hit = None
        if styles_for(sku) is None:
            for o in reversed(occ):
                if colour_for(o): hit = o; break
        hit = hit or (occ[0] if occ else None)
        if hit:
            pno, w, blocks, plines = hit
            cx, cy = (w[0] + w[2]) / 2, w[1]
            blk = next((b for b in blocks if b[0] - 1 <= cx <= b[2] + 1 and b[1] - 1 <= cy <= b[3] + 1), None)
            if blk:
                lines = [l.strip() for l in blk[4].splitlines() if l.strip()]
                lines = [l for l in lines if l != sku and not re.match(r'^(762|BAT)-', l)]
                # the line(s) right under, in the same column (descriptions run over 2 blocks)
                below = [b for b in blocks if b[1] >= blk[3] - 1 and b[1] - blk[3] < 6 and abs((b[0]+b[2])/2 - (blk[0]+blk[2])/2) < 40]
                for b in below[:1]:
                    lines += [l.strip() for l in b[4].splitlines() if l.strip()]
                lines = [l for l in lines if not re.search(r'MOQ|PRODUCTION TIME', l, re.I)]
                label = ' · '.join(lines)
            if styles_for(sku) is None:
                m = colour_for(hit)
                if m: colors, locs = m.group(1), int(m.group(2))
                # section title, e.g. "Guam Local Navy Pride Apparel Designs - 6": the one on this half of the page
                label = ''
                half = 0 if w[0] < 612 else 1
                for bb, t in plines:
                    if re.search(r'Apparel Designs', t) and bb[1] < 45 and (0 if bb[0] < 612 else 1) == half:
                        label = re.sub(r'^\d+\s*-\s*|\s*-\s*\d+$', '', t).replace(' Apparel Designs', '').strip()
        e = {'sku': sku, 'file': im['file'], 'page': im['page']}
        st = styles_for(sku)
        if st is None:
            e['apparel'] = {'colors': colors, 'tier': tier(colors) if colors else None, 'loc': locs}
        else:
            e['styles'] = st
        e['label'] = label
        if im.get('more'): e['more'] = [m['file'] for m in im['more']]
        rec.append(e)
    out[cat] = rec
json.dump(out, open('/home/claude/catimg/designs/designs.json', 'w'), indent=1)
for cat in out:
    for e in out[cat]: print(cat[:3], e['sku'], e.get('styles') or e.get('apparel'), '|', e['label'][:70])
