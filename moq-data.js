/* Minimum order quantities (MOQ) from the NEXCOM DSD catalogs
 * (Local Navy Pride and Souvenir, Nov 2026). Shared by souvenirs.html,
 * navy-pride.html and art-request.html. Both catalogs use the same minimums.
 *
 * To change a minimum, edit the numbers below and upload this file to GitHub.
 * Styles are written without the SVN / LNP prefix.
 *
 *   q    = the minimum, per design
 *   note = extra rule shown next to it (optional)
 *
 * Apparel: the minimum goes by the number of ink colors. Different garments
 * and garment colors can be mixed to reach it, as long as the art is the
 * same size (catalog ordering notes).
 */
var MOQ_APPAREL = { '1-2': 48, '3-5': 72, '6-9': 145 };
var MOQ_APPAREL_NOTE = 'Mix garments and colors to reach it (same art size)';

var MOQ_DATA = {
    // Hats
    'PTCHCAP':   { q: 24 },
    'TWL36CAP':  { q: 36, note: 'Hat colors shown in the catalog only' },
    'TWLCAP':    { q: 144, note: 'Any hat color' },
    // Plush
    'J35-1': { q: 24 }, 'J34-9': { q: 24 }, 'J35-2': { q: 24 }, 'J34-8': { q: 24 },
    'J32-1': { q: 24 }, 'J60-1': { q: 24 }, 'J31-1': { q: 24 }, 'J31-6': { q: 24 }, 'J59-1': { q: 24 },
    'J37-T': { q: 24 }, 'J37-MAG': { q: 24 },
    'BEAR6': { q: 24 }, 'BEAR10': { q: 24 }, 'BEAR12': { q: 24 }, 'BEAR10HD': { q: 24 }, 'BEAR12HD': { q: 24 },
    // Lanyards and ID holders
    '632JD': { q: 50 }, '634JD': { q: 50 }, '632JDBA': { q: 50 },
    '212030BH': { q: 50 }, '212036BH': { q: 50 },
    '600TS': { q: 100 }, '600HS': { q: 100 },
    // Decals and magnets
    'VD3.5': { q: 24 }, 'VD6': { q: 24 }, 'VD6X2': { q: 24 }, 'VD10': { q: 24 },
    'VD12X6': { q: 24 }, 'VD12X12': { q: 24 }, 'VD20T': { q: 24 },
    'MAG-SM': { q: 24 }, 'MAG': { q: 24 }, 'MAG6': { q: 24 }, 'MAG8': { q: 24 }, 'MAGEURO': { q: 24 }, 'MAG10T': { q: 24 }, 'MAG12': { q: 24 },
    // Textured stickers (the catalog says 520 for the 5" x 5"; left out until that's confirmed)
    'TS2': { q: 50 }, 'TS3': { q: 35 },
    // Window clings and sticker sheets
    'CL3': { q: 50 }, 'CL5': { q: 40 }, 'CL6X2': { q: 40 }, 'CL16': { q: 20 }, 'SS1': { q: 24 },
    // Bags
    '3071': { q: 150 }, '3220': { q: 36 }, '3220E': { q: 24 },
    // Key chains
    '300JD': { q: 72 }, '301JD': { q: 72 }, '301LG': { q: 72 }, 'BOK01': { q: 48 }, 'KCSTRP-100': { q: 24 },
    // Playing cards and puzzle cubes
    'PCC': { q: 50 }, 'JCUBE': { q: 24 }, 'CUBE-KC': { q: 24 },
    // Ornaments
    '1081100': { q: 12 }, '1081101': { q: 12 }, '1081102': { q: 12 },
    '1081103': { q: 12 }, '1081104': { q: 12 }, '1081105': { q: 12 },
    // Etched glassware and mugs
    '003-7898-DE': { q: 12 }, '003-4585-DE': { q: 12 }, '003-4584-DE': { q: 12 }, '003-0012-DE': { q: 12 },
    '003-2163-DE': { q: 12 }, '003-5166-DE': { q: 12 }, '003-6416-DE': { q: 12 }, '024-6146 ASST': { q: 12 },
    // Polar Camel and Nalgene drinkware
    'PC06': { q: 24, note: '12 per color' }, 'PC09': { q: 24, note: '12 per color' }, 'PC10': { q: 24, note: '12 per color' },
    'PC11': { q: 24, note: '12 per color' }, 'PC13': { q: 24, note: '12 per color' },
    'TC701': { q: 24, note: '12 per color' }, 'TC704': { q: 24, note: '12 per color' },
    'TC825-WH': { q: 48 }
};

/** Minimum for a style such as "SVNTEE3-5-1" or "LNPPC09".
 *  Returns { q, note, key } or null when the catalog has no minimum for it.
 *  `key` groups items that count toward the same minimum. */
function moqFor(style) {
    var s = String(style || '').toUpperCase().replace(/^(SVN|LNP)/, '');
    var m = /^([A-Z]+)(\d-\d)-\d$/.exec(s);          // apparel: TEE1-2-1, HDY6-9-2 …
    if (m && MOQ_APPAREL[m[2]]) return { q: MOQ_APPAREL[m[2]], note: MOQ_APPAREL_NOTE, key: 'APPAREL ' + m[2], apparel: true };
    var keys = Object.keys(MOQ_DATA);
    for (var i = 0; i < keys.length; i++) {
        if (keys[i].toUpperCase() === s) return { q: MOQ_DATA[keys[i]].q, note: MOQ_DATA[keys[i]].note || '', key: s, apparel: false };
    }
    return null;
}

/* Lead times from the NEX DSD Item Details sheet (Nov 18 2026 meeting): how long
 * an item takes once it's ordered, so reps know how far ahead to order. Shown on
 * the order pages and the art request form. Styles without the SVN / LNP prefix.
 * Apparel isn't in that sheet: LEAD_TIME_APPAREL is used for every garment. */
var LEAD_TIME_APPAREL = '4 weeks';
var LEAD_TIMES = {
    // 4 weeks
    'J35-1': '4 weeks', 'J34-9': '4 weeks', 'J35-2': '4 weeks', 'J34-8': '4 weeks', 'J32-1': '4 weeks', 'J60-1': '4 weeks', 'J31-1': '4 weeks', 'J31-6': '4 weeks', 'J59-1': '4 weeks', 'J37-T': '4 weeks', 'J37-MAG': '4 weeks', 'BEAR10': '4 weeks', 'BEAR12': '4 weeks', 'BEAR6': '4 weeks', 'BEAR10HD': '4 weeks', 'BEAR12HD': '4 weeks', '632JD': '4 weeks', '634JD': '4 weeks', '632JDBA': '4 weeks', '212030BH': '4 weeks', '212036BH': '4 weeks', '600TS': '4 weeks', '600HS': '4 weeks', '003-7898-DE': '4 weeks', '003-4585-DE': '4 weeks', '003-4584-DE': '4 weeks', '003-0012-DE': '4 weeks', '003-2163-DE': '4 weeks', '003-5166-DE': '4 weeks', '024-6146 ASST': '4 weeks', '024-6146-AST': '4 weeks', '003-6416-DE': '4 weeks', 'PTCHCAP': '4 weeks',
    // 2 weeks
    'VD3.5': '2 weeks', 'VD6': '2 weeks', 'VD6X2': '2 weeks', 'VD10': '2 weeks', 'VD12X6': '2 weeks', 'VD12X12': '2 weeks', 'VD20T': '2 weeks', 'VD3SM': '2 weeks', 'VD6SM': '2 weeks', 'TS2': '2 weeks', 'TS3': '2 weeks', 'TS5': '2 weeks', 'SS1': '2 weeks', 'CL3': '2 weeks', 'CL5': '2 weeks', 'CL6X2': '2 weeks', 'CL16': '2 weeks', 'MAG-SM': '2 weeks', 'MAG6': '2 weeks', 'MAG8': '2 weeks', 'MAGEURO': '2 weeks', 'MAG10T': '2 weeks', 'MAG12': '2 weeks',
    // 6 weeks
    '300JD': '6 weeks', '301JD': '6 weeks', '301LG': '6 weeks', 'BOK01': '6 weeks', 'KCSTRP-100': '6 weeks', '3071': '6 weeks', '3220': '6 weeks', '3220E': '6 weeks', 'PCSS': '6 weeks', 'PCC': '6 weeks', 'JCUBE': '6 weeks', 'CUBE-KC': '6 weeks', 'TC825-WH': '6 weeks', 'PC06': '6 weeks', 'PC09': '6 weeks', 'PC10': '6 weeks', 'PC11': '6 weeks', 'PC13': '6 weeks', 'TC701': '6 weeks', 'TC704': '6 weeks', 'TWLCAP': '6 weeks', 'TWL36CAP': '6 weeks',
    // 3–5 days
    '1081103': '3–5 days', '1081105': '3–5 days', '1081100': '3–5 days', '1081101': '3–5 days', '1081104': '3–5 days', '1081102': '3–5 days'
};

/** Lead time for a style such as "SVNTEE3-5-1" or "LNPPC09" ("6 weeks"), or '' if unknown. */
function leadTimeFor(style) {
    var s = String(style || '').toUpperCase().replace(/^(SVN|LNP)/, '');
    if (/^[A-Z]+\d-\d-\d$/.test(s)) return LEAD_TIME_APPAREL;
    var keys = Object.keys(LEAD_TIMES);
    for (var i = 0; i < keys.length; i++) if (keys[i].toUpperCase() === s) return LEAD_TIMES[keys[i]];
    return '';
}
