// Common head elements for SafePDF website
// Note: Critical SEO meta tags are now in static HTML for better SEO
function createCommonHead(pageConfig) {
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
    <link rel="apple-touch-icon" sizes="180x180" href="/icons/apple-touch-icon.png">
    <link rel="apple-touch-icon" sizes="152x152" href="/icons/apple-touch-icon-152x152.png">
    <link rel="apple-touch-icon" sizes="120x120" href="/icons/apple-touch-icon-120x120.png">
    <link rel="apple-touch-icon" sizes="76x76" href="/icons/apple-touch-icon-76x76.png">
    <meta name="msapplication-TileColor" content="#0f1720">
    <meta name="msapplication-TileImage" content="/icons/mstile-150x150.png">

    <!-- Web Manifest -->
    <link rel="manifest" href="/site.webmanifest">

    <!-- Performance / fonts -->
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link id="deferred-google-fonts" data-href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
    
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" integrity="sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA==" crossorigin="anonymous" referrerpolicy="no-referrer">
    
    <!-- Preload hero image to improve LCP -->
    <link rel="preload" as="image" href="https://github.com/mcagriaksoy/SafePDF/raw/main/img/SafePDF_Ad.avif">

    <!-- Canonical and hreflang tags for multilingual SEO -->
    <script>
        // Dynamically set canonical, hreflang, and HTML lang attribute
        (function() {
            var base = '${pageConfig.baseUrl}';
            var url = new URL(window.location.href);
            var lang = url.searchParams.get('lang') || 'en';
            
            // Validate language is ISO standard (en, tr, de)
            if (!['en', 'tr', 'de'].includes(lang)) {
                lang = 'en';
            }
            
            // Update HTML lang attribute to match
            document.documentElement.lang = lang;
            
            var canon = base;
            if(lang === 'tr') canon = base + '?lang=tr';
            else if(lang === 'de') canon = base + '?lang=de';
            // Canonical
            var linkCanon = document.createElement('link');
            linkCanon.rel = 'canonical';
            linkCanon.href = canon;
            document.head.appendChild(linkCanon);
            // Hreflang alternates
            var langs = [
                {code:'en', url: base},
                {code:'tr', url: base+'?lang=tr'},
                {code:'de', url: base+'?lang=de'}
            ];
            langs.forEach(function(l) {
                var link = document.createElement('link');
                link.rel = 'alternate';
                link.hreflang = l.code;
                link.href = l.url;
                document.head.appendChild(link);
            });
            // x-default
            var linkDef = document.createElement('link');
            linkDef.rel = 'alternate';
            linkDef.hreflang = 'x-default';
            linkDef.href = base;
            document.head.appendChild(linkDef);
        })();
    </script>

    <!-- JSON-LD structured data -->
    <script type="application/ld+json">
    {
      "@context": "https://schema.org",
      "@type": "SoftwareApplication",
      "name": "SafePDF",
      "url": "${pageConfig.canonicalUrl}",
      "description": "Privacy-first offline PDF toolkit for compressing, splitting, merging, converting, rotating and repairing PDF documents.",
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
      "applicationCategory": "DeveloperTool",
      "offers": {
        "@type": "Offer",
        "price": "0",
        "priceCurrency": "USD"
      },
      "aggregateRating": {
        "@type": "AggregateRating",
        "ratingValue": "4.9",
        "ratingCount": "127",
        "bestRating": "5",
        "worstRating": "1"
      },
      "featureList": [
        "Offline PDF processing",
        "Privacy-focused operations",
        "PDF compression",
        "Split and merge PDFs",
        "Convert PDF to JPG/TXT/DOCX",
        "Rotate PDF pages",
        "Repair corrupted PDFs",
        "Edit PDF metadata"
      ]
    }
    </script>
    `;

    // Insert into head
    document.head.insertAdjacentHTML('beforeend', headContent);

    // Load deferred fonts
    loadDeferredFonts();
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