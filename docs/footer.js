// Footer component for SafePDF website
function createFooter() {
    const footerHTML = `
    <footer class="site-footer" id="contact">
        <div class="container footer-grid">
            <div class="footer-col">
                <p class="muted">SafePDF is a privacy-focused offline tool for PDF manipulation. Merge, compress, split,
                    and organize your PDF files securely: No internet required, your documents stay local and safe.</p>
                <p class="small">Released under <a
                        href="https://github.com/mcagriaksoy/SafePDF/blob/main/LICENSE">GPL‑3.0</a></p>
            </div>

            <div class="footer-col">
                <h4>PDF Converters</h4>
                <ul class="footer-links">
                    <li><a href="pdf-to-word.html">PDF to Word</a></li>
                    <li><a href="pdf-to-excel.html">PDF to Excel</a></li>
                    <li><a href="pdf-to-powerpoint.html">PDF to PPTX</a></li>
                    <li><a href="pdf-to-jpg.html">PDF to JPG</a></li>
                    <li><a href="pdf-to-png.html">PDF to PNG</a></li>
                    <li><a href="pdf-to-text.html">PDF to Text</a></li>
                    <li><a href="word-to-pdf.html">Word to PDF</a></li>
                    <li><a href="excel-to-pdf.html">Excel to PDF</a></li>
                    <li><a href="powerpoint-to-pdf.html">PPTX to PDF</a></li>
                    <li><a href="jpg-to-pdf.html">JPG to PDF</a></li>
                    <li><a href="png-to-pdf.html">PNG to PDF</a></li>
                </ul>
            </div>

            <div class="footer-col">
                <h4>Resources</h4>
                <ul class="footer-links">
                    <li><a href="downloads.html">Downloads</a></li>
                    <li><a href="sitemap.xml">Sitemap</a></li>
                    <li><a href="terms.html">Terms of Use</a></li>
                    <li><a href="privacy.html">Privacy & Consent</a></li>
                    <li><a href="cookie-policy.html">Cookie Policy</a></li>
                </ul>
            </div>

            <div class="footer-col">
                <h4>Community</h4>
                <ul class="footer-links">
                    <li><a href="https://github.com/mcagriaksoy/SafePDF">Source Code</a></li>
                    <li><a href="downloads.html">Download Latest Release</a></li>
                </ul>
            </div>

            <div class="footer-col">
                <h4>Download for</h4>
                <div class="footer-download-buttons">
                    <a href="downloads.html" class="footer-download-btn" title="Download for Windows">
                        <i class="fab fa-windows"></i>
                    </a>
                    <a href="downloads.html" class="footer-download-btn" title="Download for macOS">
                        <i class="fab fa-apple"></i>
                    </a>
                    <a href="downloads.html" class="footer-download-btn" title="Download for Linux">
                        <i class="fab fa-linux"></i>
                    </a>
                </div>
            </div>

            <div class="footer-col">
                <h4>Contact & Support</h4>
                <p class="muted">Need help or have feedback?</p>
                <p class="small"><a href="mailto:info@safepdf.de">info@safepdf.de</a></p>
                <p class="small"><a href="#" id="contact-btn-footer">Contact Form</a></p>
                <p class="small"><a href="#" id="cookie-settings-footer">Cookie Settings</a></p>
            </div>
        </div>
        <div class="container footer-bottom">
            <p class="muted">© <span id="copy-year"></span> SafePDF • Finally, a safe solution. <a
                    href="https://github.com/mcagriaksoy/SafePDF">Repository</a>
            </p>
                <div class="footer-social-buttons">
                    <a href="https://github.com/mcagriaksoy/SafePDF" class="footer-social-btn" title="GitHub">
                        <i class="fab fa-github"></i>
                    </a>
                    <a href="https://linkedin.com/in/mcagriaksoy" class="footer-social-btn" title="LinkedIn">
                        <i class="fab fa-linkedin-in"></i>
                    </a>
                    <a href="mailto:info@safepdf.de" class="footer-social-btn" title="Email">
                        <i class="fas fa-envelope"></i>
                    </a>
                </div>
                <div class="footer-payment-logos">
                    <img src="assets/mc.avif" alt="Mastercard Logo" style="height: 32px; margin-right: 8px;">
                    <img src="assets/vc.avif" alt="Visa Logo" style="height: 32px;">
                </div>
                <!-- BEGIN: TrustLock Badge --><a name="trustbadge" href="https://trustlock.co" ><img name="trustseal" alt="Trust Badges" style="border: 0;" src="https://trustlock.co/wp-content/uploads/2019/01/free-website-trust-badges-100-money-back-guarantee.png" width="238" height="44"></a><!-- End: TrustLock Badge -->
            <button id="back-to-top" title="Back to top"
                style="position: fixed; bottom: 20px; right: 20px; z-index: 1000;">↑</button>
            <a href="https://www.checkdomain.de/unternehmen/garantie/ssl/popup/"
                onclick="window.open(this.href + '?host=' + window.location.host,'','height=600,width=560,scrollbars=yes'); return false;"><img
                    src="https://www.checkdomain.de/assets/bundles/web/app/widget/seal/img/ssl_certificate/de/150x150.png?20251209-101640"
                    alt="SSL-Zertifikat" /></a>
        </div>
        
    </footer>
    `;

    // Insert footer before the closing body tag
    document.body.insertAdjacentHTML('beforeend', footerHTML);

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

    // Contact button functionality
    const contactBtn = document.getElementById('contact-btn-footer');
    if (contactBtn) {
        contactBtn.addEventListener('click', function (e) {
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

    // Cookie settings functionality
    const cookieSettingsBtn = document.getElementById('cookie-settings-footer');
    if (cookieSettingsBtn) {
        cookieSettingsBtn.addEventListener('click', function (e) {
            e.preventDefault();
            // Trigger cookie consent modal if available
            if (window.showCookieConsent) {
                window.showCookieConsent();
            }
        });
    }
}

// Auto-initialize footer when DOM is ready
document.addEventListener('DOMContentLoaded', function () {
    createFooter();
});