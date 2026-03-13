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
            <a href="${brandLink}" class="nav-brand">SafePDF™</a>
            <ul class="nav-links">
                ${sharedLinks.map(link => `<li><a href="${link.href}">${link.text}</a></li>`).join('')}
            </ul>
            <div class="lang-selector" style="display:flex;align-items:center;gap:6px">
                <img id="lang-flag" src="${flagMap.en}" alt="Selected language flag" width="24" height="16" style="display:block;border-radius:2px;box-shadow:0 0 0 1px rgba(15,23,36,.12)">
                <label for="language-select" style="display:none">Language</label>
                <select class="language-select" id="language-select" aria-label="Language" style="background:#fff;color:#0f1724;border:1px solid #ddd;padding:4px 8px;border-radius:6px;">
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
            const url = new URL(window.location.href);
            url.searchParams.set('lang', lang);
            window.location.href = url.toString();
        });

        // Set initial flag based on URL parameter
        const urlLang = new URL(window.location.href).searchParams.get('lang');
        if (urlLang) {
            for (let i = 0; i < langSelect.options.length; i++) {
                if (langSelect.options[i].value === urlLang) {
                    langSelect.selectedIndex = i;
                    break;
                }
            }
        }
        updateFlag();
    }

}
