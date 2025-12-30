// Common navigation for SafePDF website
function createNavigation(navConfig) {
    const navContent = `
    <nav class="navbar">
        <div class="container">
            <a href="${navConfig.brandLink}" class="nav-brand">SafePDF™</a>
            <ul class="nav-links">
                ${navConfig.links.map(link => `<li><a href="${link.href}" ${link.id ? `id="${link.id}"` : ''}>${link.text}</a></li>`).join('')}
            </ul>
            <div class="lang-selector" style="display:flex;align-items:center;gap:6px">
                <span id="lang-flag" style="font-size:1.3em;font-family:'Apple Color Emoji','Segoe UI Emoji','Segoe UI Symbol','Noto Color Emoji',sans-serif;">🇬🇧</span>
                <label for="language-select" style="display:none">Language</label>
                <select class="language-select" id="language-select" aria-label="Language" style="background:#fff;color:#0f1724;border:1px solid #ddd;padding:4px 8px;border-radius:6px;">
                    <option value="en" data-flag="🇬🇧">English</option>
                    <option value="tr" data-flag="🇹🇷">Türkçe</option>
                    <option value="de" data-flag="🇩🇪">Deutsch</option>
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
            const flagMap = { en: '🇬🇧', tr: '🇹🇷', de: '🇩🇪' };
            const lang = langSelect.value;
            langFlag.textContent = flagMap[lang] || '🌐';
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

    // Contact button functionality (only for nav contact button)
    const contactBtn = document.getElementById('nav-contact-btn');
    if (contactBtn) {
        contactBtn.addEventListener('click', function(e) {
            e.preventDefault();
            // Show contact modal instead of scrolling
            const modal = document.getElementById('contact-modal');
            if (modal) {
                modal.style.display = 'block';
                // Generate captcha if function exists
                if (typeof generateCaptcha === 'function') {
                    generateCaptcha();
                }
            } else {
                // Fallback: scroll to contact section
                const contactSection = document.getElementById('contact');
                if (contactSection) {
                    contactSection.scrollIntoView({ behavior: 'smooth' });
                }
            }
        });
    }
}