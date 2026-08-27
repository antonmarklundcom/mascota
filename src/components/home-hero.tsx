import Image from "next/image";
import Link from "next/link";
import { ArrowRight, PawPrint } from "lucide-react";

import { Button } from "@/components/ui/button";
import type { Hero } from "@/config/tienda";
import { t } from "@/i18n";
import { productImageUrl } from "@/lib/images";

/**
 * La portada de la home (PLAN.md FASE 2, PR O), con el diseño de Mascota PY.
 *
 * Server Component sin estado: es un cartel, no una feature. La decisión de
 * si existe la toma `src/app/page.tsx` mirando `TIENDA.hero`; acá sólo se
 * dibuja lo que llegó.
 *
 * **Es piel** (NEW-STORE.md §5). Lo que se mantuvo del template al repintarlo
 * es el caso "sin foto" —el estado en el que arranca toda tienda recién
 * clonada, y en el que está ésta hasta que carguen Cloudinary—: sin
 * `CLOUDINARY_CLOUD_NAME` la portada sale como bloque de color con el título
 * en serif, nunca como un rectángulo roto.
 *
 * Lo que **no** se copió del diseño, a propósito: el "98 mil+ clientes
 * felices" y el "4,6" de puntuación. Son números inventados, y una tienda que
 * abre mañana no los tiene. Las tres chips de abajo dicen sólo lo que esta
 * tienda sí cumple.
 */
export function HomeHero({ hero }: { hero: Hero }) {
  const imagen = hero.imagen ?? null;
  // `null` cuando falta `CLOUDINARY_CLOUD_NAME`: el hero se dibuja igual, con
  // el fondo de siempre, en vez de con un rectángulo roto.
  const src = productImageUrl(imagen?.cloudinaryId, "hero");

  const chips = [t("home.hero.chip.envios"), t("home.hero.chip.iva"), t("home.hero.chip.whatsapp")];

  return (
    <section className="border-border/70 bg-secondary relative isolate overflow-hidden rounded-3xl border">
      {src ? (
        <>
          <Image
            src={src}
            alt={imagen?.alt ?? ""}
            fill
            priority
            sizes="(max-width: 1152px) 100vw, 1152px"
            className="object-cover"
          />
          {/*
            El velo no es decoración: sin él, un título claro sobre una foto
            clara deja de leerse, y qué foto va a cargar la tienda es
            exactamente lo que no se puede saber desde acá. `aria-hidden`
            porque no aporta nada a quien no ve la foto.
          */}
          <div className="absolute inset-0 -z-0 bg-black/45" aria-hidden />
        </>
      ) : null}

      <div
        className={`relative px-6 py-12 text-center sm:px-10 sm:py-20 ${
          src ? "min-h-[320px] sm:min-h-[420px]" : ""
        }`}
      >
        <h1
          className={`font-display mx-auto max-w-3xl text-4xl leading-[1.05] tracking-tight text-balance sm:text-6xl ${
            src ? "text-white" : "text-primary"
          }`}
        >
          {hero.titulo}
        </h1>

        {hero.texto ? (
          <p
            className={`mx-auto mt-4 max-w-xl text-sm text-pretty sm:text-base ${
              src ? "text-white/90" : "text-muted-foreground"
            }`}
          >
            {hero.texto}
          </p>
        ) : null}

        {hero.cta ? (
          <div className="mt-7 flex flex-wrap justify-center gap-3">
            <Button
              asChild
              size="lg"
              className="bg-accent text-accent-foreground hover:bg-accent/90 rounded-full px-7"
            >
              <Link href={hero.cta.href}>
                {hero.cta.label}
                <ArrowRight className="size-4" aria-hidden />
              </Link>
            </Button>
          </div>
        ) : null}

        <ul
          className={`mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs sm:text-sm ${
            src ? "text-white/90" : "text-muted-foreground"
          }`}
        >
          {chips.map((chip) => (
            <li key={chip} className="flex items-center gap-1.5">
              <PawPrint className="text-accent size-4" aria-hidden />
              {chip}
            </li>
          ))}
        </ul>
      </div>
    </section>
  );
}
