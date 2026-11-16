// AAFES on/off switch for the Sales Portal.
//
// Reps already order AAFES on the live AAFES site, so the AAFES pages here are
// hidden from them until the two portals are merged. Admins still see them.
// To show AAFES to everyone at go-live, change false to true below and upload.
var AAFES_SHOW_TO_REPS = false;

/** True if this login may see the AAFES pages. */
function aafesAllowed(auth) {
    var role = String((auth && auth.role) || '').trim().toLowerCase();
    var programs = (auth && auth.programs) || [];
    if (role === 'admin') return true;
    return AAFES_SHOW_TO_REPS && programs.indexOf('AAFES') !== -1;
}

// On an AAFES page (the script tag has data-aafes-page), send anyone else home.
(function () {
    var me = document.currentScript;
    if (!me || !me.hasAttribute('data-aafes-page')) return;
    var auth = null;
    try { auth = JSON.parse(sessionStorage.getItem('salesPortalAuth')); } catch (e) {}
    if (auth && !aafesAllowed(auth)) window.location.replace('index.html');
})();
