import { Suspense } from "react";
import Link from "next/link";
import { PawPrint } from "lucide-react";

import { TIENDA } from "@/config/tienda";
import { CartButton } from "@/components/cart-button";
import { CuentaHeaderEntry } from "@/components/cuenta/header-entry";
import { SearchBox } from "@/components/search-box";
import { getCategories } from "@/db/queries";
import { t } from "@/i18n";

/**
 * El header de la tienda — **piel** (NEW-STORE.md §5).
 *
 * El diseño de Mascota PY: fondo menta, marca en serif con la huella, y las
 * acciones como píldoras a la derecha. Lo único que no es decoración es que
 * el menú de categorías sale de la base y que el header se dibuja igual si la
 * base todavía no responde — una tienda a medio instalar no puede quedarse
 * sin cabecera.
 */
export async function SiteHeader() {
  let categories: Awaited<ReturnType<typeof getCategories>> = [];
  try {
    categories = await getCategories();
  } catch {
    // Sin base todavía: el header se dibuja igual, sin el menú.
  }

  return (
    <header className="border-border/70 bg-background/90 sticky top-0 z-30 border-b backdrop-blur">
      <div className="mx-auto flex w-full max-w-6xl items-center gap-3 px-4 py-3">
        <Link
          href="/"
          className="text-primary flex shrink-0 items-center gap-2 text-lg font-normal tracking-tight sm:text-xl"
        >
          <span className="bg-primary text-primary-foreground flex size-9 items-center justify-center rounded-full">
            <PawPrint className="size-5" aria-hidden />
          </span>
          <span className="font-display">{TIENDA.nombre}</span>
        </Link>

        <Suspense fallback={null}>
          <SearchBox className="mx-auto hidden w-full max-w-sm sm:block" />
        </Suspense>

        <div className="ml-auto flex items-center gap-2 sm:ml-0">
          {/* Devuelve null con `TIENDA.cuentasClientes` apagado: sin el flag,
              este header es idéntico al de antes de la feature. */}
          <Suspense fallback={null}>
            <CuentaHeaderEntry />
          </Suspense>
          <CartButton />
        </div>
      </div>

      <nav aria-label={t("header.categorias")} className="border-border/60 border-t">
        <div className="mx-auto flex w-full max-w-6xl gap-2 overflow-x-auto px-4 py-2 text-sm">
          {categories.map((category) => (
            <Link
              key={category.id}
              href={`/categoria/${category.slug}`}
              className="text-muted-foreground hover:bg-secondary hover:text-primary shrink-0 rounded-full px-3 py-1 transition-colors"
            >
              {category.name}
            </Link>
          ))}
        </div>
      </nav>

      <div className="border-border/60 border-t px-4 py-2 sm:hidden">
        <Suspense fallback={null}>
          <SearchBox />
        </Suspense>
      </div>
    </header>
  );
}
