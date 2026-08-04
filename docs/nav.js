// Common navigation for SafePDF website
const flagMap = {
    en: "assets/flag-en.svg",
    tr: "assets/flag-tr.svg",
    de: "assets/flag-de.svg"
};

function createNavigation(navConfig) {
    const isHomePage = window.location.pathname.endsWith('/') || window.location.pathname.endsWith('/index.html') || window.location.pathname.endsWith('index.html');
    const sharedLinks = isHomePage ? [
        { href: "#features", text: "Features" },
        { href: "#converters", text: "Converters" },
        { href: "#why-offline", text: "Why Offline" },
        { href: "#buy-pro", text: "Compare Plans" },
        { href: "downloads.html", text: "Downloads" },
        { href: "offline-pdf-tools.html", text: "Guides" },
        { href: "sustainability.html", text: "Sustainability" },
        { href: "contact.html", text: "Contact" }
    ] : [
        { href: "index.html#features", text: "Features" },
        { href: "index.html#converters", text: "Converters" },
        { href: "index.html#why-offline", text: "Why Offline" },
        { href: "index.html#buy-pro", text: "Compare Plans" },
        { href: "downloads.html", text: "Downloads" },
        { href: "offline-pdf-tools.html", text: "Guides" },
        { href: "sustainability.html", text: "Sustainability" },
        { href: "contact.html", text: "Contact" }
    ];
    const brandLink = isHomePage ? "" : "index.html";
    const navContent = `
    <nav class="navbar">
        <div class="container">
            <a href="${brandLink}" class="nav-brand">
                <svg class="nav-logo-icon" width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2L3 7V12C3 17.55 6.84 22.74 12 24C17.16 22.74 21 17.55 21 12V7L12 2Z" fill="url(#brand-grad)"/>
                    <path d="M12 6.5C9.5 6.5 7.5 8.5 7.5 11V12.5H6.5V17.5H17.5V12.5H16.5V11C16.5 8.5 14.5 6.5 12 6.5ZM12 8.3C13.5 8.3 14.7 9.5 14.7 11V12.5H9.3V11C9.3 9.5 10.5 8.3 12 8.3Z" fill="white"/>
                    <defs>
                        <linearGradient id="brand-grad" x1="3" y1="2" x2="21" y2="24" gradientUnits="userSpaceOnUse">
                            <stop stop-color="#E11D48"/>
                            <stop offset="1" stop-color="#991B1B"/>
                        </linearGradient>
                    </defs>
                </svg>
                <span>SafePDF<span class="brand-tm">™</span></span>
            </a>
            <ul class="nav-links">
                ${sharedLinks.map(link => `<li><a href="${link.href}">${link.text}</a></li>`).join('')}
            </ul>
            <div class="lang-selector">
                <img id="lang-flag" src="${flagMap.en}" alt="Selected language flag" width="22" height="15" class="lang-flag-img">
                <label for="language-select" style="display:none">Language</label>
                <select class="language-select" id="language-select" aria-label="Language">
                    <option value="en">English</option>
                    <option value="tr">Türkçe</option>
                    <option value="de">Deutsch</option>
                </select>
            </div>
        </div>
    </nav>
    `;

    // Insert at the beginning of body
    document.body.insertAdjacentHTML('afterbegin', navContent);

    // Initialize navigation functionality
    initializeNavigation();
}

function initializeNavigation() {
    // Language switcher functionality
    const langSelect = document.getElementById('language-select');
    const langFlag = document.getElementById('lang-flag');

    if (langSelect && langFlag) {
        function updateFlag() {
            const lang = langSelect.value;
            langFlag.src = flagMap[lang] || flagMap.en;
            langFlag.alt = `${langSelect.options[langSelect.selectedIndex].text} flag`;
        }

        langSelect.addEventListener('change', function() {
            updateFlag();
            const lang = langSelect.value;
            
            // Set cookie so other pages know the language choice
            var d = new Date(); d.setTime(d.getTime() + (365*24*60*60*1000));
            document.cookie = "site_lang=" + lang + ";path=/;expires=" + d.toUTCString() + ";SameSite=Lax";
            
            const url = new URL(window.location.href);
            url.searchParams.set('lang', lang);
            window.location.href = url.toString();
        });

        // Set initial flag based on URL parameter or cookie
        const urlLang = new URL(window.location.href).searchParams.get('lang');
        const cookieLang = getCookie('site_lang');
        const activeLang = urlLang || cookieLang;
        if (activeLang) {
            for (let i = 0; i < langSelect.options.length; i++) {
                if (langSelect.options[i].value === activeLang) {
                    langSelect.selectedIndex = i;
                    break;
                }
            }
        }
        updateFlag();
    }

}

function getCookie(name) {
    var value = "; " + document.cookie;
    var parts = value.split("; " + name + "=");
    if (parts.length === 2) return parts.pop().split(";").shift();
    return null;
}
