import Link from "next/link";
import { PawPrint } from "lucide-react";

import { TIENDA } from "@/config/tienda";
import { getCategories } from "@/db/queries";
import { t } from "@/i18n";
import { comercioWhatsApp } from "@/lib/comercio";
import { formatPhonePY } from "@/lib/py";

/**
 * El pie — **piel** (NEW-STORE.md §5).
 *
 * Bloque verde profundo, que es como el diseño cierra la página: la vidriera
 * entera es menta y el pie es el único lugar donde el verde de la marca ocupa
 * todo el ancho. Los datos (categorías, WhatsApp) siguen saliendo de donde
 * salían.
 */
export async function SiteFooter() {
  let categories: Awaited<ReturnType<typeof getCategories>> = [];
  try {
    categories = await getCategories();
  } catch {
    // idem SiteHeader: el pie no debería tirar la página abajo.
  }
  const phone = comercioWhatsApp();

  return (
    <footer className="bg-primary text-primary-foreground mt-16">
      <div className="mx-auto grid w-full max-w-6xl gap-8 px-4 py-12 text-sm sm:grid-cols-3">
        <div>
          <p className="font-display flex items-center gap-2 text-lg">
            <PawPrint className="size-5" aria-hidden />
            {TIENDA.nombre}
          </p>
          <p className="text-primary-foreground/75 mt-3 max-w-xs">{TIENDA.tagline}</p>
        </div>

        <div>
          <p className="font-medium">{t("footer.categorias")}</p>
          <ul className="text-primary-foreground/75 mt-3 space-y-2">
            {categories.map((category) => (
              <li key={category.id}>
                <Link
                  href={`/categoria/${category.slug}`}
                  className="hover:text-primary-foreground transition-colors"
                >
                  {category.name}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <p className="font-medium">{t("footer.contacto")}</p>
          <ul className="text-primary-foreground/75 mt-3 space-y-2">
            {phone ? <li>{t("footer.whatsapp", { telefono: formatPhonePY(phone) })}</li> : null}
            <li>
              <Link
                href="/pedido/buscar"
                className="hover:text-primary-foreground transition-colors"
              >
                {t("footer.seguirPedido")}
              </Link>
            </li>
          </ul>
        </div>
      </div>
    </footer>
  );
}
