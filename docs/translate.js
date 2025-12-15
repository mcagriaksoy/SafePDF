(function(){
  function setCookie(name, value, days){
    var d = new Date(); d.setTime(d.getTime() + (days*24*60*60*1000));
    document.cookie = name + "=" + value + ";path=/;expires=" + d.toUTCString();
  }

  function googleTranslateElementInit(){
    if (typeof google === 'undefined' || !google.translate) return;
    new google.translate.TranslateElement({pageLanguage: 'en', includedLanguages: 'en,tr,de', layout: google.translate.TranslateElement.InlineLayout.SIMPLE}, 'google_translate_element');
  }

  function triggerTranslate(lang){
    var attempt = function(){
      var combo = document.querySelector('.goog-te-combo');
      if(combo){ combo.value = lang; combo.dispatchEvent(new Event('change')); }
      else if(window.google && window.google.translate){ setTimeout(attempt,300); }
    };
    attempt();
  }

  function attachListeners(){
    var selects = Array.prototype.slice.call(document.querySelectorAll('.language-select, #language-select'));
    selects.forEach(function(sel){
      sel.addEventListener('change', function(e){
        var lang = e.target.value;
        document.documentElement.lang = lang || 'en';
        setCookie('site_lang', lang, 365);
        triggerTranslate(lang);
      });
    });
  }

  // ensure hidden translate container exists
  if(!document.getElementById('google_translate_element')){
    var d = document.createElement('div'); d.id = 'google_translate_element'; d.style.display = 'none'; document.body.appendChild(d);
  }

  // expose callback
  window.googleTranslateElementInit = googleTranslateElementInit;

  // attach listeners on DOM ready
  if(document.readyState === 'loading') document.addEventListener('DOMContentLoaded', attachListeners);
  else attachListeners();

  // load Google Translate script
  (function(){
    var s = document.createElement('script');
    s.src = '//translate.google.com/translate_a/element.js?cb=googleTranslateElementInit';
    s.async = true; s.defer = true;
    document.head.appendChild(s);
  })();
})();
