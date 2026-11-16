"""Render each catalog product photo and name it by the SKU caption next to it.
usage: python extract.py catalog.pdf outdir prefix
"""
import sys, re, json, os
import pymupdf as fitz

SKU = re.compile(r'^(762-\d{4}|HAT-T?\d{4}|BAT-\d{3,4}[A-Z]{0,4}|[A-Z0-9][A-Z0-9.]*(?:[- ][A-Z0-9.]+)*-\d{4}|E?AR12HD-\d{4})$')
ZOOM = 3.0

def area(r): return max(0, r.width) * max(0, r.height)

def flat(pm):
    """Image with transparency → on white, RGB."""
    from PIL import Image
    import io
    if pm.colorspace and pm.colorspace.n == 4: pm = fitz.Pixmap(fitz.csRGB, pm)
    im = Image.open(io.BytesIO(pm.tobytes('png'))).convert('RGBA')
    bg = Image.new('RGBA', im.size, 'white'); bg.alpha_composite(im)
    out = bg.convert('RGB'); buf = io.BytesIO(); out.save(buf, 'PNG')
    return fitz.Pixmap(buf.getvalue())

def main(pdf, outdir, tag):
    os.makedirs(outdir, exist_ok=True)
    d = fitz.open(pdf)
    found, report = {}, []
    for pno in range(d.page_count):
        p = d[pno]; W, H = p.rect.width, p.rect.height
        # spreads: page box can be wider than 612 (two pages side by side)
        W = max(W, max([i['bbox'][2] for i in p.get_image_info()] + [W]))
        def big_overlap(a, b):
            i = a & b
            if i.width <= 0 or i.height <= 0: return False
            return area(i) >= 0.3 * min(area(a), area(b))
        def group(rects):
            clusters = []
            for r in rects:
                hit = [c for c in clusters if any(big_overlap(r, m) for m in c)]
                merged = [r]
                for c in hit: merged += c; clusters.remove(c)
                clusters.append(merged)
            out = []
            for c in clusters:
                b = fitz.Rect(c[0])
                for m in c[1:]: b |= m
                if b.width >= 25 and b.height >= 45 or b.width >= 45 and b.height >= 25: out.append(b)
            return out
        # Pass 1: photos (raster images), grouped when they overlap a lot (bottle + cap, mug halves).
        img_rects, xref_of, all_imgs = [], {}, []
        for i in p.get_image_info(xrefs=True):
            all_imgs.append(fitz.Rect(i['bbox']))
            r = fitz.Rect(i['bbox']) & fitz.Rect(0, 0, W, H)
            if r.width < 30 or r.height < 30: continue
            if r.width > 0.45 * W and r.height > 0.6 * H: continue      # backgrounds
            img_rects.append(r); xref_of[tuple(r)] = i.get('xref', 0)
        img_boxes = [b for b in group(img_rects) if b.width >= 45 and b.height >= 45]
        # Pass 2 (only for captions with no photo): vector artwork.
        vec_rects = []
        drawings = p.get_drawings()
        for dr in drawings:
            r = fitz.Rect(dr['rect'])
            big_side, small_side = max(r.width, r.height), min(r.width, r.height)
            solid = dr.get('fill') is not None or any(it[0] in ('re', 'qu') for it in dr['items'])
            if solid and big_side >= 60 and small_side >= 25 and r.width <= 0.4 * W and r.height <= 0.6 * H: vec_rects.append(r)
        vec_boxes = group(vec_rects)
        caps = []
        for b in p.get_text('dict')['blocks']:
            for l in b.get('lines', []):
                t = re.sub(r'\s+', ' ', ''.join(s['text'] for s in l['spans']).strip())
                toks = [t] if SKU.match(t) else [x for x in re.findall(r'[A-Z0-9.]+(?:-[A-Z0-9.]+)*-\d{4}', t) if SKU.match(x)]
                for tok in toks: caps.append((tok, fitz.Rect(l['bbox'])))
        def match(boxes, todo, cap_box, used):
            pairs = []
            for ci in todo:
                sku, cr = caps[ci]
                for bi, b in enumerate(boxes):
                    dx = max(b.x0 - cr.x1, cr.x0 - b.x1, 0); dy = max(b.y0 - cr.y1, cr.y0 - b.y1, 0)
                    dist = (dx * dx + dy * dy) ** 0.5
                    if dist > 60: continue
                    cx = (cr.x0 + cr.x1) / 2
                    if not (b.x0 - 15 <= cx <= b.x1 + 15) and dx > 0: dist += 25          # off to the side
                    if b.y1 <= cr.y0 + 12: dist *= 0.7                                    # photo above its caption
                    pairs.append((dist, ci, bi))
            pairs.sort()
            for dist, ci, bi in pairs:
                if ci in cap_box or bi in used: continue
                cap_box[ci] = boxes[bi]; used.add(bi)
        def holds(b, cr):
            cx, cy = (cr.x0 + cr.x1) / 2, (cr.y0 + cr.y1) / 2
            return b.x0 <= cx <= b.x1 and b.y0 <= cy <= b.y1
        img_boxes = [b for b in img_boxes if sum(1 for _, cr in caps if holds(b, cr)) <= 1]   # not a backdrop behind several products
        # One photo of several products in a row, each with its caption underneath: cut it into slices.
        split = []
        for b in img_boxes:
            below = sorted([(cr.x0 + cr.x1) / 2 for _, cr in caps
                            if -12 <= cr.y0 - b.y1 <= 45 and b.x0 - 10 <= (cr.x0 + cr.x1) / 2 <= b.x1 + 10], key=float)
            if len(below) >= 3:
                edges = [b.x0] + [(below[k] + below[k + 1]) / 2 for k in range(len(below) - 1)] + [b.x1]
                split += [fitz.Rect(edges[k], b.y0, edges[k + 1], b.y1) for k in range(len(below))]
            else:
                split.append(b)
        img_boxes = split
        vec_boxes = [b for b in vec_boxes if sum(1 for _, cr in caps if holds(b, cr)) <= 1]
        cap_box = {}
        if os.environ.get('DBG') == str(pno + 1):
            print('img', [[round(v) for v in b] for b in img_boxes]); print('vec', [[round(v) for v in b] for b in vec_boxes])
            print('caps', [(t, [round(v) for v in r]) for t, r in caps])
        match(img_boxes, range(len(caps)), cap_box, set())
        taken = list(cap_box.values())
        vec_free = [b for b in vec_boxes if not any(big_overlap(b, t) and area(t) < 2 * area(b) for t in taken)]
        match(vec_free, [ci for ci in range(len(caps)) if ci not in cap_box], cap_box, set())
        for ci, (sku, cr) in enumerate(caps):
            sku = re.sub(r'^(PC09-NVY) (\d{4})$', r'\1-\2', sku)
            if ci not in cap_box:
                report.append({'sku': sku, 'page': pno + 1, 'problem': 'no photo next to caption'}); continue
            clip = cap_box[ci]
            # A photo whose neighbours overlap it (hats drawn edge to edge): take the photo file itself,
            # so no part of the next product shows. Only when it's one photo with nothing laid on top.
            members = [r for r in img_rects if big_overlap(r, clip) and (r & clip) == r]
            neighbours = [r for r in all_imgs if (r & clip).width > 0 and (r & clip).height > 0 and area(r & clip) < 0.6 * area(r)]
            raw = None
            overlays = [r for r in all_imgs if r != members[0] and area(r & clip) >= 0.6 * area(r)] if len(members) == 1 else [1]
            overlays += [1 for dr in drawings if area(fitz.Rect(dr['rect']) & clip) >= 0.6 * max(area(fitz.Rect(dr['rect'])), 1)
                         and fitz.Rect(dr['rect']).width < clip.width * 0.95]
            if len(members) == 1 and neighbours and xref_of.get(tuple(members[0]), 0) > 0 and not overlays:
                try:
                    pm = fitz.Pixmap(d, xref_of[tuple(members[0])])
                    if pm.alpha or pm.colorspace is None or pm.n > 4:
                        pm = fitz.Pixmap(fitz.csRGB, pm) if pm.colorspace and pm.colorspace.n != 3 else pm
                    raw = pm
                except Exception:
                    raw = None
            key = sku.upper()
            fn = re.sub(r'[^A-Za-z0-9.\-]+', '_', sku) + '.jpg'
            if key in found:   # same SKU shown again (e.g. on a model and as the flat design): keep as a second picture
                n = 2
                while os.path.exists(os.path.join(outdir, fn[:-4] + '_%d.jpg' % n)): n += 1
                alt = fn[:-4] + '_%d.jpg' % n
                pix = p.get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM), clip=clip, alpha=False)
                pix.save(os.path.join(outdir, alt), jpg_quality=88)
                found[key].setdefault('more', []).append({'file': alt, 'page': pno + 1})
                continue
            pix = flat(raw) if raw is not None else p.get_pixmap(matrix=fitz.Matrix(ZOOM, ZOOM), clip=clip, alpha=False)
            pix.save(os.path.join(outdir, fn), jpg_quality=88)
            found[key] = {'sku': sku, 'file': fn, 'page': pno + 1, 'w': pix.width, 'h': pix.height}
    json.dump({'catalog': tag, 'images': list(found.values()), 'issues': report}, open(os.path.join(outdir, 'index.json'), 'w'), indent=1)
    print(tag, len(found), 'images;', len(report), 'issues')
    for r in report: print('  ', r)

if __name__ == '__main__':
    main(*sys.argv[1:4])
