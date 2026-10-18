// Common navigation for SafePDF website
// The link set is defined in one place so every page stays consistent.
// Language switching uses real, static URLs (/de/, /tr/) so search engines
// see correctly localised pages instead of client-side machine translation.
const flagMap = {
    en: "assets/flag-en.svg",
    tr: "assets/flag-tr.svg",
    de: "assets/flag-de.svg"
};

const flagMapLangFolder = {
    en: "../assets/flag-en.svg",
    tr: "../assets/flag-tr.svg",
    de: "../assets/flag-de.svg"
};

const navLabels = {
    en: { features: "Features", converters: "Converters", pricing: "Pricing", downloads: "Downloads", guides: "Guides" },
    de: { features: "Funktionen", converters: "Konverter", pricing: "Preise", downloads: "Downloads", guides: "Anleitungen" },
    tr: { features: "Özellikler", converters: "Dönüştürücüler", pricing: "Fiyatlar", downloads: "İndir", guides: "Rehberler" }
};

function getCurrentLang() {
    if (/^\/de(\/|$)/.test(window.location.pathname)) return "de";
    if (/^\/tr(\/|$)/.test(window.location.pathname)) return "tr";
    return "en";
}

// Pages that have a static de/tr translation. When the current page has one,
// switching language keeps the user on the same page; otherwise it falls back
// to the localised homepage.
const TRANSLATED_PAGES = new Set([
    "pdf-to-word.html", "pdf-to-excel.html", "pdf-to-powerpoint.html",
    "pdf-to-jpg.html", "pdf-to-png.html", "pdf-to-text.html",
    "word-to-pdf.html", "excel-to-pdf.html", "powerpoint-to-pdf.html",
    "jpg-to-pdf.html", "png-to-pdf.html"
]);

function buildLangUrl(lang) {
    const path = window.location.pathname.replace(/^\/(de|tr)(\/|$)/, "/");
    const rel = path.replace(/index\.html$/, "");
    const isHome = rel === "/" || rel === "";
    const slug = isHome ? "" : rel.replace(/^\//, "");
    if (lang === "en") {
        return isHome ? "/" : "/" + slug;
    }
    if (isHome || TRANSLATED_PAGES.has(slug)) {
        return "/" + lang + "/" + slug;
    }
    // No localized version of this page yet: go to the localized homepage.
    return "/" + lang + "/";
}

function createNavigation() {
    const path = window.location.pathname;
    const inLangFolder = /^\/(de|tr)\//.test(path);
    const isIndex = path.endsWith('/') || path.endsWith('/index.html') || path.endsWith('index.html');

    const lang = getCurrentLang();
    const labels = navLabels[lang] || navLabels.en;
    const base = inLangFolder ? '../' : '';
    const anchorPrefix = isIndex ? '' : 'index.html';
    // index.html always lives in the same folder as the current page.
    const brandLink = 'index.html';
    const flags = inLangFolder ? flagMapLangFolder : flagMap;

    const links = [
        { href: `${anchorPrefix}#features`, text: labels.features },
        { href: `${anchorPrefix}#converters`, text: labels.converters },
        { href: `${anchorPrefix}#buy-pro`, text: labels.pricing },
        { href: `${base}downloads.html`, text: labels.downloads },
        { href: `${base}offline-pdf-tools.html`, text: labels.guides }
    ];

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
                ${links.map(link => `<li><a href="${link.href}">${link.text}</a></li>`).join('')}
            </ul>
            <div class="lang-selector">
                <img id="lang-flag" src="${flags[lang] || flags.en}" alt="Selected language flag" width="22" height="15" class="lang-flag-img">
                <label for="language-select" style="display:none">Language</label>
                <select class="language-select" id="language-select" aria-label="Language">
                    <option value="en"${lang === 'en' ? ' selected' : ''}>English</option>
                    <option value="tr"${lang === 'tr' ? ' selected' : ''}>Türkçe</option>
                    <option value="de"${lang === 'de' ? ' selected' : ''}>Deutsch</option>
                </select>
            </div>
        </div>
    </nav>
    `;

    document.body.insertAdjacentHTML('afterbegin', navContent);

    initializeNavigation(flags, lang);
}

function initializeNavigation(flags, currentLang) {
    const langSelect = document.getElementById('language-select');
    const langFlag = document.getElementById('lang-flag');

    if (langSelect && langFlag) {
        function updateFlag() {
            const selected = langSelect.value;
            langFlag.src = flags[selected] || flags.en;
            langFlag.alt = `${langSelect.options[langSelect.selectedIndex].text} flag`;
        }

        langSelect.addEventListener('change', function () {
            const selected = langSelect.value;
            updateFlag();
            if (selected === currentLang) return;
            window.location.href = buildLangUrl(selected);
        });

        updateFlag();
    }
}
