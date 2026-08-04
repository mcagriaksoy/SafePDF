// Footer component for SafePDF website
function createFooter() {
    const footerHTML = `
    <div class="container footer-grid">
        <div class="footer-col footer-brand-col">
            <h4>SafePDF</h4>
            <p class="muted">Offline PDF toolkit for secure local processing. Merge, split, compress, convert, and repair without uploading files.</p>
            <p class="small">Released under <a href="https://github.com/mcagriaksoy/SafePDF/blob/main/LICENSE">GPL-3.0</a></p>
        </div>

        <div class="footer-col">
            <h4>Popular Tools</h4>
            <ul class="footer-links">
                <li><a href="pdf-to-word.html">PDF to Word</a></li>
                <li><a href="pdf-to-excel.html">PDF to Excel</a></li>
                <li><a href="pdf-to-powerpoint.html">PDF to PPTX</a></li>
                <li><a href="pdf-to-jpg.html">PDF to JPG</a></li>
                <li><a href="word-to-pdf.html">Word to PDF</a></li>
                <li><a href="jpg-to-pdf.html">JPG to PDF</a></li>
            </ul>
        </div>

        <div class="footer-col">
            <h4>Resources</h4>
            <ul class="footer-links">
                <li><a href="downloads.html">Downloads</a></li>
                <li><a href="offline-pdf-tools.html">Offline PDF Guide</a></li>
                <li><a href="secure-pdf-processing.html">Secure PDF Processing</a></li>
                <li><a href="sustainability.html">Sustainability</a></li>
                <li><a href="terms.html">Terms of Use</a></li>
                <li><a href="privacy.html">Privacy</a></li>
                <li><a href="cookie-policy.html">Cookie Policy</a></li>
                <li><a href="sitemap.xml">Sitemap</a></li>
            </ul>
        </div>

        <div class="footer-col">
            <h4>Contact</h4>
            <p class="small"><a href="mailto:info@safepdf.de">info@safepdf.de</a></p>
            <p class="small"><a href="https://safepdf.de/contact.html">Contact Form</a></p>
            <p class="small"><a href="https://safepdf.de/cookie-policy.html" id="cookie-settings-footer">Cookie Settings</a></p>
            <div class="footer-social-buttons">
                <a href="https://github.com/mcagriaksoy/SafePDF" class="footer-social-btn" title="GitHub" aria-label="GitHub">
                    <i class="fab fa-github"></i>
                </a>
                <a href="https://linkedin.com/in/mcagriaksoy" class="footer-social-btn" title="LinkedIn" aria-label="LinkedIn">
                    <i class="fab fa-linkedin-in"></i>
                </a>
                <a href="mailto:info@safepdf.de" class="footer-social-btn" title="Email" aria-label="Email">
                    <i class="fas fa-envelope"></i>
                </a>
            </div>
        </div>
    </div>

    <div class="container footer-bottom">
        <p class="muted">© <span id="copy-year"></span> SafePDF. All rights reserved. <a href="https://github.com/mcagriaksoy/SafePDF">Repository</a></p>
        <div class="footer-trust-badges">
            <a href="https://www.checkdomain.de/unternehmen/garantie/ssl/popup/"
               onclick="window.open(this.href + '?host=' + window.location.host,'','height=600,width=560,scrollbars=yes'); return false;" class="ssl-seal-link" title="SSL-Zertifikat">
                <img src="https://www.checkdomain.de/assets/bundles/web/app/widget/seal/img/ssl_certificate/de/150x150.png" alt="SSL-Zertifikat" class="ssl-seal-img" />
            </a>
            <div class="footer-payment-logos" aria-label="Accepted payment methods">
                <img src="assets/mc.avif" alt="Mastercard" />
                <img src="assets/vc.avif" alt="Visa" />
            </div>
        </div>
    </div>

    <button id="back-to-top" class="back-to-top" title="Back to top" aria-label="Back to top">↑</button>
    `;

    const footer = document.querySelector("footer.site-footer#contact");
    if (footer) {
        footer.innerHTML = footerHTML;
    } else {
        document.body.insertAdjacentHTML("beforeend", `<footer class="site-footer" id="contact">${footerHTML}</footer>`);
    }

    // Initialize footer functionality
    initializeFooter();
}

function initializeFooter() {
    // Set copyright year
    const copyYear = document.getElementById('copy-year');
    if (copyYear) {
        copyYear.textContent = new Date().getFullYear();
    }

    // Back to top button functionality
    const backToTopBtn = document.getElementById('back-to-top');
    if (backToTopBtn) {
        backToTopBtn.addEventListener('click', function () {
            window.scrollTo({ top: 0, behavior: 'smooth' });
        });

        // Show/hide back to top button based on scroll position
        window.addEventListener('scroll', function () {
            if (window.pageYOffset > 300) {
                backToTopBtn.style.display = 'block';
            } else {
                backToTopBtn.style.display = 'none';
            }
        });
    }

    // Cookie settings functionality
    const cookieSettingsBtn = document.getElementById('cookie-settings-footer');
    if (cookieSettingsBtn) {
        cookieSettingsBtn.addEventListener('click', function (e) {
            e.preventDefault();
            // Trigger cookie consent modal if available
            if (window.openCookieModal) {
                window.openCookieModal();
            } else if (window.showCookieConsent) {
                window.showCookieConsent();
            }
        });
    }
}

// Auto-initialize footer when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    createFooter();
});
