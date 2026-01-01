// Common head elements for SafePDF website
function createCommonHead(pageConfig) {
    const headContent = `
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width,initial-scale=1" />
    <title>${pageConfig.title}</title>
    <link rel="stylesheet" href="style.css">
    <link id="deferred-google-fonts" data-href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
    <!-- FontAwesome Icons -->
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" integrity="sha512-DTOQO9RWCH3ppGqcWaEA1BIZOC6xxalwEsw9c2QQeAIftl+Vegovlnee1c9QX4TctnWMn13TZye+giMm8e2LwA==" crossorigin="anonymous" referrerpolicy="no-referrer">
    <meta name="description" content="${pageConfig.description}">
    <meta name="keywords" content="${pageConfig.keywords}">
    <meta name="author" content="mcagriaksoy">
    <meta name="robots" content="index,follow">
    <meta name="theme-color" content="#0f1720">
    <meta name="language" content="English">
    <meta name="geo.region" content="DE">
    <meta name="geo.placename" content="Germany">

    <!-- Google Site Verification -->
    <meta name="google-site-verification" content="mQnGPoNx88KSBPyDdHNruiZHFH4WV-oMpTWV8IbjlQA" />

    <!-- Open Graph -->
    <meta property="og:title" content="${pageConfig.ogTitle}">
    <meta property="og:description" content="${pageConfig.ogDescription}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="${pageConfig.canonicalUrl}">
    <meta property="og:image" content="https://github.com/mcagriaksoy/SafePDF/raw/main/img/SafePDF_Ad.avif">
    <meta property="og:image:alt" content="${pageConfig.ogImageAlt}">
    <meta property="og:site_name" content="SafePDF">
    <meta property="og:locale" content="en_US">
    <meta property="og:image:width" content="1200">
    <meta property="og:image:height" content="630">

    <!-- Twitter card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="${pageConfig.twitterTitle}">
    <meta name="twitter:description" content="${pageConfig.twitterDescription}">
    <meta name="twitter:image" content="https://github.com/mcagriaksoy/SafePDF/raw/main/img/SafePDF_Ad.avif">
    <meta name="twitter:image:alt" content="${pageConfig.twitterImageAlt}">
    <meta name="twitter:site" content="@your_twitter">
    <meta name="twitter:creator" content="@your_twitter">

    <!-- Privacy / browser hints -->
    <meta name="referrer" content="strict-origin-when-cross-origin">
    <meta name="color-scheme" content="dark light">

    <!-- Apple / PWA hints -->
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
    <meta name="apple-mobile-web-app-title" content="SafePDF">
    <meta name="msapplication-TileColor" content="#0f1720">
    <meta name="msapplication-TileImage" content="/icons/mstile-150x150.png">

    <!-- Favicons -->
    <link rel="icon" href="/favicon.ico">
    <link rel="icon" type="image/png" sizes="32x32" href="/icons/favicon-32x32.png">
    <link rel="apple-touch-icon" sizes="180x180" href="/icons/apple-touch-icon.png">
    <link rel="manifest" href="/site.webmanifest">

    <!-- Performance / fonts & manifest -->
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="manifest" href="/site.webmanifest">
    <!-- Preload hero image to improve LCP -->
    <link rel="preload" as="image" href="https://github.com/mcagriaksoy/SafePDF/raw/main/img/SafePDF_Ad.avif">

    <!-- Canonical and hreflang tags for multilingual SEO -->
    <script>
        // Dynamically set canonical and hreflang for each language version
        (function() {
            var base = '${pageConfig.baseUrl}';
            var url = new URL(window.location.href);
            var lang = url.searchParams.get('lang') || 'en';
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

    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-FRC3NLZG1V"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-FRC3NLZG1V');
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