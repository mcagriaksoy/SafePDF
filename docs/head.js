// Common head elements for SafePDF website
// Note: Critical SEO meta tags are now in static HTML for better SEO
function createCommonHead(pageConfig = {}) {
  const canonicalUrl = pageConfig.canonicalUrl || `${window.location.origin}${window.location.pathname}`;
  const analyticsId = pageConfig.analyticsId || 'G-FRC3NLZG1V';
  const includeAnalytics = pageConfig.analytics !== false;
  const includeJsonLd = pageConfig.jsonLd !== false;
  const headContent = `
    <!-- Theme and UI Meta Tags -->
    <meta name="theme-color" content="#0f1720">
    <meta name="geo.region" content="DE">
    <meta name="geo.placename" content="Germany">
    <meta name="color-scheme" content="dark light">

    <!-- Google Site Verification -->
    <meta name="google-site-verification" content="mQnGPoNx88KSBPyDdHNruiZHFH4WV-oMpTWV8IbjlQA" />

    <!-- Privacy / browser hints -->
    <meta name="referrer" content="strict-origin-when-cross-origin">

    <!-- Apple / PWA hints -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="SafePDF">
    <meta name="msapplication-TileColor" content="#0f1720">

    <!-- Performance / fonts -->
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link id="deferred-google-fonts" data-href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
    
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" integrity="sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA==" crossorigin="anonymous" referrerpolicy="no-referrer">
    
    <!-- Preload hero image to improve LCP -->
    <!-- Hreflang: English + x-default, unless the page already defines its own -->
    <script>
        (function() {
            var base = '${canonicalUrl}';
            if (!document.querySelector('link[rel="alternate"][hreflang="en"]')) {
                [
                    { code: 'en', url: base },
                    { code: 'x-default', url: base }
                ].forEach(function(l) {
                    var link = document.createElement('link');
                    link.rel = 'alternate';
                    link.hreflang = l.code;
                    link.href = l.url;
                    document.head.appendChild(link);
                });
            }
        })();
    </script>

    ${includeJsonLd ? `
    <!-- JSON-LD structured data -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": "SafePDF",
      "@id": "${canonicalUrl}#softwareapplication",
      "url": "${canonicalUrl}",
      "description": "Open source privacy-first offline PDF toolkit for compressing, splitting, merging, converting, rotating and repairing PDF documents locally.",
      "author": { "@type": "Person", "name": "mcagriaksoy", "url": "https://github.com/mcagriaksoy" },
      "publisher": {
        "@type": "Person",
        "name": "mcagriaksoy",
        "email": "info@safepdf.de",
        "url": "https://github.com/mcagriaksoy"
      },
      "contactPoint": {
        "@type": "ContactPoint",
        "email": "info@safepdf.de",
        "contactType": "customer support"
      },
      "operatingSystem": "Windows, macOS, Linux",
      "applicationCategory": "UtilitiesApplication",
      "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "EUR"
      },
      "featureList": [
        "Offline PDF processing",
        "Open source PDF software",
        "Privacy-focused operations",
        "PDF compression",
        "Split and merge PDFs",
        "Convert PDF to JPG/TXT/DOCX",
        "Rotate PDF pages",
        "Repair corrupted PDFs",
        "Edit PDF metadata"
      ]
    }
    </script>` : ''}
    ${includeAnalytics ? `
    <!-- Consent-gated analytics -->
    <script type="text/plain" data-cookiecategory="analytics" src="https://www.googletagmanager.com/gtag/js?id=${analyticsId}" async></script>
    <script type="text/plain" data-cookiecategory="analytics">
      window.dataLayer = window.dataLayer || [];
      function gtag(){ dataLayer.push(arguments); }
      gtag('js', new Date());
      gtag('config', '${analyticsId}');
    </script>` : ''}
    `;

  // Insert into head
  document.head.insertAdjacentHTML('beforeend', headContent);

}

function loadDeferredFonts() {
  const fontLink = document.getElementById('deferred-google-fonts');
  if (fontLink) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = fontLink.dataset.href;
    document.head.appendChild(link);
    fontLink.remove();
  }
}
