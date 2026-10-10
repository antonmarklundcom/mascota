<?php
declare(strict_types=1);
// Copy to site.local.php in this PRIVATE folder only when overrides are needed.
return [
    'site_url' => 'https://mascota.com.py',
    'environment' => 'production', // Use preview on staging to send noindex headers.
    'contact_email' => '', // Optional real editorial/commercial mailbox.
    'sponsorship_enabled' => false,
    'clinic_contact_enabled' => false, // Real approved partners only.
    'clinic_click_tracking_enabled' => false, // Optional aggregate redirects, never inquiries.
    'clinic_clicks_path' => '', // Absolute .json outside app and public roots. Existing private parent required.
    // Perro destinations verified publicly on 2026-10-09. Turn off if unavailable.
    'perro_links_enabled' => true,
];
