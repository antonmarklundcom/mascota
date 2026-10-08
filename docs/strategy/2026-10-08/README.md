# Mascota.com.py — strategy and launch plan

Prepared 8 October 2026, America/Asuncion. **Planning only**, as requested. Source baseline: `antonmarklundcom/mascota`, `main`, `af72803d4a9d36048d32a589e80449c1e43c71e5`. No website implementation or deployment is included.

## Recommended idea

Build **Paraguay's practical pet-care guide and service directory**. The promise is: **“Cuidá a tu mascota en Paraguay. Encontrá veterinarias, entendé sus cuidados y elegí lo que necesita.”**

Make finding a suitable veterinarian the main action. Useful local guides attract visitors and help them choose services and products. Start with dogs and cats; use a broader animal index to organize later expansion.

The advantage to pursue is reliable local detail: species treated, branch address, contact, services, hours, source dates, local procedures and an easy correction process. A generic animal encyclopedia has less direct commercial intent and a much larger editorial burden. This is a strategic inference, not a measured traffic forecast.

The intended funnel is:

```text
Local search or useful guide
          ↓
Relevant clinic/service profile
          ↓
Owner contacts the chosen business
          ↓
Verified inquiry → optional booking confirmation

Guide → relevant buying checklist → merchant referral
```

## What already exists

The repository is a branded fork of the `ecom` store template. It contains Next.js 16, React, TypeScript, Drizzle/MySQL, a product catalogue, checkout, order/payment logic and administration. `src/config/tienda.ts` brands it “Mascota PY”; `README.md` and `DEPLOY.md` describe Hostinger **Node.js**, not PHP hosting. These are inspected source facts; no installed store, working payment account or populated production database has been verified.

The public [mascota.com.py](https://mascota.com.py/) displayed Hostinger's default welcome page during this review. That does not establish the hosting account's configuration or prove that no application exists elsewhere.

For the requested HTML/PHP site, the next step is a new PHP application on a dedicated branch. Preserve the existing store in Git. Reuse suitable branding, content ideas and reviewed assets; its TypeScript backend and checkout cannot run as PHP. See [the proposed implementation structure](SITE-STRUCTURE.md).

Anton also has a Perro project whose local operating manual describes moderated dog adoption and lost/found notices. Give Mascota a useful adoption/lost-pet guidance page linking to Perro where appropriate. Confirm Perro's current public availability before making that link prominent. Building a second dog-notice platform adds moderation and duplicated content without helping this launch.

## Compare the business options

| Option | Value for owners | Revenue path | Work and uncertainty | Recommendation |
| --- | --- | --- | --- | --- |
| Pet encyclopedia | Broad reference material | Advertising and referrals after audience growth | Large writing/review burden; local demand unmeasured | Supporting section, expanded gradually |
| Local care guide + directory | Find help and understand Paraguay-specific needs | Paid business promotion, then attributable inquiries | Requires fresh contacts and enough useful local coverage | **Primary business** |
| Independent online pet store | Buy products | Retail margin | Supplier, stock, delivery, payments and support | Later only if these capabilities are established |
| Adoption/lost-pet marketplace | Community outcomes | Limited direct revenue; sponsorship possible | Daily moderation and sensitive contact handling | Link to the existing Perro project initially |

Existing competition includes [Guía's veterinary directory](https://guia.com.py/servicio/veterinarias/), [AsuGuide's local listings](https://asuguide.com.py/categoria/veterinarias-y-pet-shops/) and retailers such as [4Pets](https://www.4pets.com.py/) and [Tiempo de Mascotas](https://www.tiempodemascotas.com.py/). Their observed pages show that listings and pet commerce already exist. No traffic, market-share or sales comparison was performed. Mascota should earn repeat use through accuracy and practical detail.

## Site sections

| Section | Purpose | First release |
| --- | --- | --- |
| Veterinarias | Search by city, species and service; contact a selected branch | Main conversion section |
| Mascotas | Choose an animal and understand its care commitments | Substantial dog/cat hubs and a useful broader index |
| Cuidados en Paraguay | Practical local ownership guides | 15 reviewed guides, listed in the structure document |
| Leyes y trámites | Understand responsibilities and reach official sources | National rules, wildlife, reporting, travel; city-specific scope |
| Productos | Explain buying criteria and refer to suitable merchants | Initially a small editorial section; offers only with real partners |
| Servicios | Grooming, boarding, training, pet sitting and other providers | Add after the veterinary pilot |
| Para profesionales | Claim/correct a listing and learn about paid promotion | Free claim process and an inquiry form |

Do not create hundreds of empty species/city/service pages. The structure can accommodate them without publishing thin content.

## How to make money

Start with **free accurate listings plus optional monthly promotion**. A basic listing includes contact details, branch address, supported species/services, source date and free corrections. Payment must never determine whether an identity/registration check passes.

An experimental paid package could include a clearly marked sponsored position on a relevant city page, a business offer, extra promotional media and a monthly activity report. **Gs. 200,000/month is a proposed interview/pilot price, not a researched market rate.** Test willingness to pay with local businesses and an explicit deliverable. Accurate organic results and emergency contacts remain accessible.

After proving real inquiry flow, consider qualified service-request billing for scheduled consultations, grooming or boarding. A click on WhatsApp is a contact intent event: it does not prove a message, appointment or sale. Confirm the event with the business or user before reporting it as a lead or booking.

Before any paid lead pilot, define accepted services, response expectations, unique/duplicate rules, invalid-lead credits, attribution, price and a monthly cap. Review professional advertising/referral rules before offering veterinary performance fees. An accepted lead is a real request for an offered service, in the service area, from a reachable person who agreed to contact sharing. It is not every phone-button click.

Product monetization should start with negotiated referrals or sponsored guides. No Paraguayan merchant affiliate programme or commission rate was confirmed in this review. Test accessories, carriers, beds, bowls, toys and grooming supplies first. Separate merchant offers from editorial criteria. Feed/medicine promotions need the appropriate product/regulatory checks; avoid personalized medication or dosing recommendations. SENACSA describes its registration/control role for [veterinary products and animal feeds](https://senacsa.gov.py/servicios/servicios-tecnicos/productos-de-uso-veterinario/).

### Illustrative economics, not a forecast

| Assumption | Calculation | Gross monthly amount |
| --- | --- | --- |
| 10 promotional subscribers at Gs. 200,000 | 10 × 200,000 | Gs. 2,000,000 |
| 50 accepted requests at an agreed Gs. 20,000 | 50 × 20,000 | Gs. 1,000,000 |
| 100 attributed product orders averaging Gs. 150,000 at a negotiated 5% | 100 × 150,000 × 0.05 | Gs. 750,000 |

These are independent examples, not additive baseline expectations. They exclude tax, refunds, hosting, editorial review, acquisition and sales/maintenance time. No demand, conversion or commission assumptions have been validated. Break-even subscriber count is monthly operating cost divided by contribution per subscriber; include Anton's/admin time when deciding whether the project is worthwhile.

## First 90 days after approval

| Period | Work | Evidence to collect |
| --- | --- | --- |
| Days 1–14 | Interview approximately 10 owners and 10 clinics; clarify the main problem, business response process and pilot offer. Inspect search terms and relevant competitors. | Notes on actual problems and willingness to pay; no invented keyword volumes |
| Days 15–35 | Build the PHP foundation; prepare 30–50 clinic branches across four city areas and 15 reviewed guides. | Profile contact/source checks, editorial sign-off, working correction process |
| Days 36–60 | Run a small pilot with 3–5 willing clinics. Track contact intent separately from confirmed inquiries and bookings. | Reachability, response times, attribution confidence, user satisfaction |
| Days 61–90 | Offer a paid promotion pilot if partners see value; test one real product-referral arrangement. Expand pages only where demand and usable data justify them. | Renewals, accepted requests, net contribution, actual merchant attribution |

Proposed decision gate: expand when at least three pilot businesses voluntarily renew/pay and tracking reliably distinguishes contact clicks from accepted inquiries. If they do not, first improve directory usefulness or reposition the offer before adding hundreds of articles. This gate is a managerial proposal, not an industry benchmark.

Launch geography: Asunción, Luque, San Lorenzo and Fernando de la Mora. Add Lambaré, Capiatá and other Central cities after the first coverage is useful; Ciudad del Este and Encarnación follow with real local partners and data. Do not imply national emergency coverage while the directory is incomplete.

## Editorial and data operation

Use named veterinary reviewers for clinical material, source links and a visible review date. General content may discuss care planning and questions for a vet; individualized diagnoses, prescription decisions and dosing are outside the site's initial service. Local costs must come from dated real observations with city/service context.

Keep laws and procedure guides attached to the responsible authority, jurisdiction and last check. The current SENACSA clinic page displays **15 September 2026**; an older search snippet displayed October 2025. The newer page is the source for this plan, but presence in its list does not establish current contact details, hours, emergency availability or every practitioner's registration. See [source register and limitations](SOURCES.md).

Recheck emergency claims frequently; proposed operation is weekly confirmation for emergency/on-call labels and monthly contact/hour review for active pilot partners. Use “confirmá por teléfono” when availability is uncertain. Permit businesses and owners to report errors without paying.

Initially send owners directly to their chosen business through a phone/WhatsApp link. Add a stored lead form only when the operator, privacy process and recipient routing are ready. The user selects the recipient and explicitly authorizes sharing; marketing opt-in is separate. No broadcasting private requests to every clinic. Keep lead records out of public pages, Git and operation manuals.

## Decisions to make before implementation

1. Accept or revise the proposed positioning and first four city areas.
2. Identify the real site operator, contact address and clinical reviewer.
3. Confirm Hostinger's PHP website slot, document root, supported runtime and Git/deployment behavior.
4. Choose the first clinics and merchants to approach; outreach has not been performed.
5. Agree on the promotion deliverable and pilot price, then measure renewal rather than relying on theoretical revenue.

The practical next deliverable is a PHP directory and guide MVP based on [SITE-STRUCTURE.md](SITE-STRUCTURE.md). The original Next.js store stays available in Git for future retail work.
