# Mascota — proposed site and HTML/PHP structure

8 October 2026. Implementation brief, **not implemented**. Read [strategy](README.md) and [sources](SOURCES.md) first. Public-facing language: Spanish for Paraguay, with clear local wording and prices in guaraníes where applicable. Guaraní content can follow with a competent reviewer.

## Navigation and homepage

Main navigation: **Veterinarias · Mascotas · Cuidados · Leyes y trámites · Productos**. “Para profesionales” is a separate utility link. On mobile, veterinary search and contact actions should be easy to reach.

Homepage structure:

1. Header and promise: **“Todo para cuidar a tu mascota en Paraguay.”**
2. Primary search: city, animal type, service; **“Buscar veterinaria”**. Secondary link: **“Ver cuidados y guías”**.
3. Quick links to dog/cat guides, veterinary search, travel procedures and legal responsibilities.
4. Recent, source-checked local guides with author/reviewer and date.
5. Suitable directory branches with clear contact/availability information. Sponsored results occupy a labelled area.
6. A concise pet-type index and an adoption/lost-pet guidance link to the existing Perro project when its live status is confirmed.
7. Useful buying guides and real merchant offers if configured.
8. Footer: operator, methodology, source policy, correction/contact route, privacy and sponsorship disclosures.

No fabricated testimonial, star rating, clinic count, response time or “open now” claim. Emergency discovery should open available direct contacts, without requiring registration or a request form. Hours and holiday/on-call availability require current confirmation.

## Proposed URLs

| URL | Page purpose | Release |
| --- | --- | --- |
| `/` | Search and guide entry point | MVP |
| `/veterinarias/` | Search/filter directory | MVP |
| `/veterinarias/asuncion/` | Useful city page with real branches | MVP |
| `/veterinarias/luque/` | City page | MVP |
| `/veterinarias/san-lorenzo/` | City page | MVP |
| `/veterinarias/fernando-de-la-mora/` | City page | MVP |
| `/veterinaria/{branch-slug}/` | One clinic branch, contact and sources | MVP |
| `/mascotas/` | Pet-category index and selection criteria | MVP |
| `/mascotas/perros/` and `/mascotas/gatos/` | Substantial care hubs | MVP |
| `/mascotas/{species-group}/` | Reviewed specialist hubs | Later |
| `/cuidados/` and `/cuidados/{article-slug}/` | Practical guides | MVP |
| `/leyes-y-tramites/` | Source index with national/local scope | MVP |
| `/leyes-y-tramites/{topic-slug}/` | Responsibilities, wildlife, travel, reporting | MVP |
| `/productos/` and `/productos/{guide-slug}/` | Buying criteria and merchant referrals | Small initial section, then partner pilot |
| `/servicios/{service}/` | Grooming, boarding, training, pet sitting | Later, real data first |
| `/adopcion-y-mascotas-perdidas/` | Guidance and existing Perro link | MVP if link verified |
| `/profesionales/` | Free listing claim/correction; promotion explanation | MVP |
| `/solicitar-contacto/` | Explicit request to a selected provider | Later, after direct-contact pilot |
| `/metodologia/`, `/fuentes/`, `/contacto/` | Editorial/data policy and corrections | MVP |
| `/privacidad/`, `/terminos/`, `/publicidad/` | Actual operator/data/commercial policies | MVP, operator details required |

Filter combinations stay ordinary search results and should not automatically create indexable pages. Publish extra city/species/service landing pages only when they contain distinctive, maintained material and enough relevant providers. Maintain one stable canonical profile per branch.

## Pet taxonomy: broad scope, staged publication

This is a practical coverage taxonomy, not a claim to list every possible pet species or approve its possession in Paraguay. Record common and scientific names on individual species pages, with legal/source status. Legal status must be checked for the exact species and origin.

| Family | Examples to organize future content | Priority/condition |
| --- | --- | --- |
| Dogs | Puppies, adults, senior dogs; mixed-breed and breed-specific needs | First; organize mainly by care need, not hundreds of breed pages |
| Cats | Kittens, adults, senior cats; indoor/outdoor management | First |
| Rabbits | Domestic rabbit care | Second; reviewer/provider availability required |
| Small rodents | Guinea pigs, hamsters, domestic rats/mice, chinchillas, gerbils | Second; individual species checks |
| Other small mammals | Ferrets and other animals people may inquire about | Later; origin, legal status and specialist-care review first |
| Birds | Domestic canaries, budgerigars, cockatiels; separate wild-bird issues | Second; never imply all parrots are lawful pets |
| Freshwater fish | Species profiles and aquarium care/compatibility | Second |
| Marine fish and aquaria | Saltwater systems and specialist care | Later |
| Reptiles | Turtles, lizards, snakes | Specialist educational coverage; exact legal/origin checks before recommendations |
| Amphibians | Frogs, salamanders, newts | Specialist educational coverage with legal/origin checks |
| Invertebrates | Aquarium shrimp/snails, ornamental insects and arachnids | Later; legal, ecological and care review |
| Equines | Horses, ponies, donkeys kept as companions | Separate later section; different provider/space needs |
| Backyard animals | Chickens, ducks, geese and other companion animals in suitable settings | Later; separate from livestock production and municipal restrictions |
| Paraguayan wildlife | Identification, conservation, rescue authority and why wildlife belongs in its habitat | Education, not a pet-sale or acquisition catalogue |

MADES advises against keeping wildlife as pets and describes exceptional authorized possession. Build wildlife pages around conservation and official guidance. The site must not turn “Paraguayan pet information” into promotion of wild-animal commerce. [MADES source](https://www.mades.gov.py/2024/11/10/los-animales-silvestres-no-son-mascotas/).

Every substantive animal page covers: suitability; time/space commitments; housing; care planning; veterinary access; costs with dated local observations; legal/origin considerations; product selection criteria; reviewer/source dates; related local services. Detailed health advice waits for review.

## First 15 guides

These are proposed titles/intents, not already written articles. Local clinical topics require a veterinary reviewer; no disease-prevalence or search-volume claims were verified.

| # | Working Spanish title/topic | Useful next action |
| --- | --- | --- |
| 1 | Primer perro: qué preparar antes de llevarlo a casa | Dog hub and routine vet search |
| 2 | Primer gato: espacio, seguridad y primera consulta | Cat hub and routine vet search |
| 3 | ¿Qué mascota se adapta a tu hogar? | Compare care/space and check species rules |
| 4 | Qué preguntar en un control veterinario | Consultation checklist |
| 5 | Cuidar a las mascotas durante el calor | Reviewed care guide and direct-help route |
| 6 | Pulgas y garrapatas: preguntas para tu veterinario | Preventive-care consultation; no dosing tool |
| 7 | Vacunas: cómo organizar el plan con un veterinario | Keep an individual vet-approved plan |
| 8 | Castración: qué consultar antes y después | Find a suitable provider |
| 9 | Cómo elegir una veterinaria y comprobar sus datos | Directory methodology and SENACSA links |
| 10 | Cómo buscar atención de urgencia y confirmar disponibilidad | Direct contacts; no guaranteed availability |
| 11 | Cuánto cuesta cuidar una mascota: presupuesto en guaraníes | Dated local cost worksheet, no invented prices |
| 12 | Tenencia responsable: leyes nacionales y reglas de tu ciudad | Official sources, precise jurisdiction |
| 13 | Fauna silvestre: por qué no es una mascota y a quién consultar | MADES guidance |
| 14 | Viajar con perros y gatos: trámites de entrada y salida | SENACSA, destination authority and airline links |
| 15 | Cómo denunciar maltrato animal por los canales oficiales | Official reporting page; no public accusations |

Avoid simultaneously publishing guide #12 as near-identical pages in `/cuidados/` and `/leyes-y-tramites/`: choose one canonical location and link from both hubs.

## Directory profile and contact flow

Store branches individually. Minimum fields: business name; stable slug; city/barrio; street address; public business phone/WhatsApp; map link; species and services confirmed by the provider; regular hours; emergency/on-call claim and confirmation date; source URL/date; contact-check date; identity/registration-check evidence where available; edit/claim status; sponsorship state.

Use separate labels for **“Datos confirmados por el establecimiento”**, **“Listado en SENACSA, fuente del [fecha]”** and paid promotion. A listed business, a currently registered professional and a business that has confirmed its phone/hours are different facts. Do not collapse them into one “verified” badge.

Default organic sorting: service/species fit, locality and useful data freshness; describe the rule on the methodology page. Include a labelled sponsor area without making payment a clinical recommendation. Do not publish third-party reviews or logos/photos without appropriate rights.

First flow: owner searches → reads profile → taps call or WhatsApp → contacts that selected business. A prepared message can say “Hola, vi su ficha en Mascota.com.py. Quiero consultar por [servicio].” It should not contain owner identity or other private details unless the owner enters them. Opening a WhatsApp draft does not send a message.

Optional later request: owner selects a participating provider and service → sees exactly who receives the request → enters minimal contact details → explicitly agrees to sharing → receives a reference → provider acknowledges/accepts. Record separate statuses: `submitted`, `delivered`, `accepted`, `contacted`, `booked`, `invalid`, `closed`. Delivery is not acceptance, and acceptance is not a booking. Duplicates/invalid requests follow the agreed credit policy. Keep promotional consent separate and optional.

## PHP architecture proposal

Use server-rendered **HTML/CSS + small JavaScript**, PHP **8.4 if supported by the actual Hostinger slot**, and MySQL/MariaDB through PDO for mutable directory/claim/request data. Pin the runtime during implementation; the installed Hostinger runtime is unverified. No Node runtime is required for the proposed public site. Keep article content/version history in reviewed files initially; a full editorial CMS is unnecessary for the first 15 guides.

Suggested layout inside a future branch:

```text
php-site/
  public/              # Only this folder is publicly served
    index.php          # Front controller and route dispatch
    .htaccess          # Rewrites and web access rules
    assets/            # CSS, small JS, optimized owned/licensed images
    robots.txt
  app/
    bootstrap.php
    Routing/
    Controllers/
    Repositories/      # PDO access and prepared statements
    Views/             # Escaped server-rendered templates
  content/             # Reviewed articles and source metadata
  config/
    config.example.php # Names/placeholders only; real config is private
  database/migrations/ # Versioned schema changes when implemented
  tools/               # Private CLI import/export and checks
  tests/               # Meaningful functional/security checks
docs/strategy/2026-10-08/
```

Planned tables, introduced only when their features ship:

| Table/group | Purpose |
| --- | --- |
| businesses + branches | Legal/business identity and individual locations |
| branch_services + species + hours | Actual directory filtering and availability metadata |
| source_checks + claims | Provenance, confirmation and ownership/correction review |
| sponsors + offers | Labelled paid placements with start/end dates |
| requests + request_events | Optional private request/consent/status history |
| administrators + audit_events | Authenticated changes and operational history |

For MVP, vet/operator editing should use a small authenticated administration surface, or a controlled import process plus a moderated correction queue. Claims do not immediately overwrite public records. Require authentication, authorization, CSRF protection, parameterized queries, output escaping and rate limiting for mutations. Keep real configuration, lead records, exports and backups outside the document root and outside Git.

## Hostinger preparation

[Hostinger supports Git deployment for custom PHP/HTML sites](https://www.hostinger.com/support/1583302-how-to-deploy-a-git-repository-in-hostinger/). That establishes provider capability, not this account's exact layout or automatic deployment settings.

During the future build, determine the domain's actual document root. A recommended layout puts the application/private configuration beside `public_html`, with only the contents of `php-site/public` publicly served. The bootstrap paths must match that final deployment layout. Do not deploy the repository root containing the old application, docs and private configuration into the public root.

Hostinger's documented Git “root directory” is a deployment destination; do not assume it can select a repository subfolder as the application's public source. Validate the current UI. If it cannot, prepare a reviewed public release package plus private application files for SFTP/SSH deployment, or use a dedicated deployment branch/layout designed for that slot. Choose one procedure and test staging before production.

Future configuration names may include `MASCOTA_SITE_URL`, `MASCOTA_DB_DSN`, `MASCOTA_DB_USER`, `MASCOTA_DB_PASSWORD`, `MASCOTA_OPERATOR_NAME`, `MASCOTA_CONTACT_EMAIL` and mail-transport settings only if email is used. These are proposed names, not existing integrations. Missing provider/contact settings should disable the corresponding feature; do not invent a business WhatsApp number.

At launch use HTTPS and `America/Asuncion` for directory availability logic. Preview/staging must stay out of the search index; the final canonical hostname, redirects and sitemap are confirmed during deployment. Structured data describes actual content only; omit fabricated ratings and medical endorsements.

## Acceptance criteria for a future build

- Mobile directory search, city pages, branch contact links and corrections work with JavaScript disabled except optional enhancements.
- Each published branch has reviewed contact/source information; claimed services and emergency availability are dated and accurate.
- Each clinical/legal guide has the required reviewer/source/jurisdiction metadata; placeholder articles and demo clinic data never appear publicly.
- Unknown routes return a real 404; canonical URLs and the sitemap contain only useful published pages; search filters do not produce unlimited duplicate indexable URLs.
- Admin/claim/request functions enforce access control, validation, CSRF protection, output escaping and private-data isolation.
- Contact clicks, accepted requests and bookings remain separate in reporting. Billing cannot treat an unverified click as a lead.
- Backup and restore are tested in an isolated copy with synthetic data; code rollback preserves legitimate new private data.
- Test the chosen Hostinger PHP version, private-path isolation, HTTPS, mail if enabled, and real contact destinations on staging.

No application tests were run in this strategy task because application code, dependencies and databases were not changed. The next implementation request should choose the proposed scope before replacing any current build/deployment layout.
