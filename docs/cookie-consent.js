(function(){
  const KEY = 'safepdf_cookie_prefs';
  const COOKIE_NAME = 'safepdf_cookie_consent';
  const COOKIE_MAX_AGE = 31536000; // 1 year

  function getPrefs(){
    try{ return JSON.parse(localStorage.getItem(KEY)) || null; }catch(e){return null}
  }

  function savePrefs(p){
    const prefs = Object.assign({ necessary:true, preferences:false, analytics:false, marketing:false }, p);
    prefs.ts = new Date().toISOString();
    prefs.version = 1;
    localStorage.setItem(KEY, JSON.stringify(prefs));
    document.cookie = COOKIE_NAME + '=' + encodeURIComponent(JSON.stringify({ts:prefs.ts,version:prefs.version})) + '; path=/; max-age=' + COOKIE_MAX_AGE + '; SameSite=Lax';
    applyPrefs(prefs);
  }

  function applyPrefs(prefs){
    // load fonts / preferences resources
    if(prefs.preferences){ loadDeferredFonts(); }
    // activate blocked scripts for allowed categories
    activateBlockedScripts(prefs);
    // hide banner
    hideBanner();
  }

  function activateBlockedScripts(prefs){
    const scripts = document.querySelectorAll('script[type="text/plain"][data-cookiecategory]');
    scripts.forEach(s => {
      const cat = s.getAttribute('data-cookiecategory');
      if(!cat) return;
      if(prefs[cat]){
        const ns = document.createElement('script');
        // copy attributes
        if(s.src){ ns.src = s.src; }
        if(s.dataset && s.dataset.nomodule) ns.noModule = true;
        if(!s.src) ns.text = s.textContent;
        ns.async = s.async;
        s.parentNode.insertBefore(ns, s);
        s.parentNode.removeChild(s);
      }
    });
  }

  function loadDeferredFonts(){
    const link = document.getElementById('deferred-google-fonts');
    if(!link) return;
    const href = link.getAttribute('data-href');
    if(!href) return;
    // avoid loading twice
    if(link.getAttribute('data-loaded') === '1') return;
    const l = document.createElement('link');
    l.rel = 'stylesheet';
    l.href = href;
    l.crossOrigin = 'anonymous';
    document.head.appendChild(l);
    link.setAttribute('data-loaded','1');
  }

  function showBanner(){
    const b = document.getElementById('cookie-banner');
    if(b) b.style.display = 'block';
  }
  function hideBanner(){
    const b = document.getElementById('cookie-banner');
    if(b) b.style.display = 'none';
  }

  function openCookieModal(){
    const m = document.getElementById('cookie-modal');
    if(!m) return; m.style.display = 'flex';
    const prefs = getPrefs() || { necessary:true, preferences:false, analytics:false, marketing:false };
    const form = document.getElementById('cookie-form');
    if(form){
      form.preferences.checked = !!prefs.preferences;
      form.analytics.checked = !!prefs.analytics;
      form.marketing.checked = !!prefs.marketing;
    }
  }

  function closeCookieModal(){
    const m = document.getElementById('cookie-modal'); if(m) m.style.display = 'none';
  }

  function acceptAllCookies(){
    savePrefs({ necessary:true, preferences:true, analytics:true, marketing:true });
    closeCookieModal();
  }

  function rejectAllCookies(){
    savePrefs({ necessary:true, preferences:false, analytics:false, marketing:false });
    closeCookieModal();
  }

  function saveCookiePreferences(){
    const form = document.getElementById('cookie-form');
    if(!form) return;
    const prefs = {
      necessary: true,
      preferences: !!form.preferences.checked,
      analytics: !!form.analytics.checked,
      marketing: !!form.marketing.checked
    };
    savePrefs(prefs);
    closeCookieModal();
  }

  function init(){
    const prefs = getPrefs();
    if(!prefs){
      // show banner after small delay
      setTimeout(showBanner, 600);
    } else {
      applyPrefs(prefs);
    }
    // wire modal controls
    const cookieClose = document.getElementsByClassName('cookie-close')[0];
    cookieClose && (cookieClose.onclick = closeCookieModal);
    window.addEventListener('click', function(e){ const cookieModal = document.getElementById('cookie-modal'); if(e.target == cookieModal) closeCookieModal(); });
    const cookieFooterBtn = document.getElementById('cookie-settings-footer');
    cookieFooterBtn && cookieFooterBtn.addEventListener('click', function(e){ e.preventDefault(); openCookieModal(); });
  }

  // expose functions used by inline buttons
  window.openCookieModal = openCookieModal;
  window.closeCookieModal = closeCookieModal;
  window.acceptAllCookies = acceptAllCookies;
  window.rejectAllCookies = rejectAllCookies;
  window.saveCookiePreferences = saveCookiePreferences;
  window.showCookieBanner = showBanner;
  window.hideCookieBanner = hideBanner;

  // initialize when DOM is ready
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init); else init();

})();
