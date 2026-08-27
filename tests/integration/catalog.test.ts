import { execFile } from "node:child_process";
import { promisify } from "node:util";

import { afterAll, beforeAll, describe, expect, it } from "vitest";

import {
  getBrands,
  getCategories,
  getCategoryBySlug,
  getCategoryProducts,
  getProductBySlug,
  getSitemapEntries,
  searchProducts,
} from "@/db/queries";
import { getDb } from "@/db";
import { products } from "@/db/schema";
import { eq } from "drizzle-orm";

import { reserveStock } from "@/domain/stock";

import { TEST_DATABASE_URL, closeTestDb, hasTestDb, resetTables } from "../helpers/db";
import { createOrder } from "../helpers/factories";

const run = promisify(execFile);

describe.skipIf(!hasTestDb)("queries del catálogo", () => {
  beforeAll(async () => {
    await resetTables();
    await run("pnpm", ["exec", "tsx", "scripts/seed.ts"], {
      // Que no quede colgado para siempre si la DB no responde.
      timeout: 90_000,
      cwd: process.cwd(),
      env: { ...process.env, DATABASE_URL: TEST_DATABASE_URL },
    });
  }, 120_000);
  afterAll(closeTestDb);

  it("lista las categorías activas en orden", async () => {
    const categories = await getCategories();
    expect(categories.map((category) => category.slug)).toEqual([
      "alimentos",
      "juguetes",
      "accesorios",
      "higiene-y-salud",
    ]);
  });

  it("pagina la categoría", async () => {
    const first = await getCategoryProducts({ categorySlug: "alimentos", perPage: 4, page: 1 });
    expect(first.products).toHaveLength(4);
    expect(first.total).toBe(6);
    expect(first.totalPages).toBe(2);

    const second = await getCategoryProducts({ categorySlug: "alimentos", perPage: 4, page: 2 });
    expect(second.products).toHaveLength(2);

    const overlap = first.products.filter((product) =>
      second.products.some((other) => other.id === product.id)
    );
    expect(overlap).toEqual([]);
  });

  it("ordena por precio mínimo de las variantes", async () => {
    const asc = await getCategoryProducts({
      categorySlug: "accesorios",
      sort: "precio-asc",
      perPage: 60,
    });
    const prices = asc.products.map((product) =>
      Math.min(...product.variants.map((variant) => variant.pricePyg))
    );
    expect([...prices]).toEqual([...prices].sort((a, b) => a - b));

    const desc = await getCategoryProducts({
      categorySlug: "accesorios",
      sort: "precio-desc",
      perPage: 60,
    });
    expect(desc.products[0]?.slug).toBe("transportadora-rigida");
  });

  it("filtra por rango de precio y por marca", async () => {
    const baratos = await getCategoryProducts({
      categorySlug: "alimentos",
      maxPricePyg: 100000,
      perPage: 60,
    });
    for (const product of baratos.products) {
      expect(Math.min(...product.variants.map((v) => v.pricePyg))).toBeLessThanOrEqual(100000);
    }

    const brands = await getBrands("alimentos");
    const pedigree = brands.find((facet) => facet.brand === "Pedigree");
    expect(pedigree).toBeDefined();

    const soloPedigree = await getCategoryProducts({
      categorySlug: "alimentos",
      brand: "Pedigree",
      perPage: 60,
    });
    expect(soloPedigree.products.every((product) => product.brand === "Pedigree")).toBe(true);
    expect(soloPedigree.total).toBe(soloPedigree.products.length);

    // El conteo del filtro tiene que ser el mismo número que va a aparecer al
    // usarlo. Si se separan, "Pedigree (12)" lleva a una grilla de 3 y el
    // filtro deja de ser confiable para siempre.
    expect(pedigree?.total).toBe(soloPedigree.total);
  });

  it("las marcas salen ordenadas y sin las de otras categorías", async () => {
    const alimentos = await getBrands("alimentos");
    const nombres = alimentos.map((facet) => facet.brand);

    // Con `localeCompare("es")` y no con el `.sort()` pelado: el orden lo hace
    // MySQL con `utf8mb4_general_ci`, donde la Ñ vale lo mismo que la N, así
    // que "Ñande Moda" va antes que "Totto". El `.sort()` de JS compara code
    // points y la manda al final — no es que la consulta esté desordenada, es
    // que son dos alfabetos distintos.
    expect(nombres).toEqual([...nombres].sort((a, b) => a.localeCompare(b, "es")));
    expect(new Set(nombres).size).toBe(nombres.length);
    expect(alimentos.every((facet) => facet.total > 0)).toBe(true);

    const juguetes = (await getBrands("juguetes")).map((facet) => facet.brand);
    expect(juguetes).not.toContain("Pedigree");
  });

  it("trae la ficha del producto con sus variantes", async () => {
    const product = await getProductBySlug("alimento-perro-adulto-carne");
    expect(product).not.toBeNull();
    expect(product?.categorySlug).toBe("alimentos");
    expect(product?.variants.map((variant) => variant.label).sort()).toEqual(["15 kg", "3 kg"]);
    expect(product?.variants[0]?.available).toBeGreaterThan(0);
  });

  it("un slug inexistente devuelve null, no explota", async () => {
    expect(await getProductBySlug("no-existe-este-producto")).toBeNull();
    expect(await getCategoryBySlug("tampoco-existe")).toBeNull();
  });

  it("la disponibilidad del listado descuenta reservas vigentes", async () => {
    const before = await getProductBySlug("snacks-huesitos-dentales");
    const variant = before?.variants[0];
    expect(variant).toBeDefined();

    const orderId = await createOrder();
    await reserveStock(orderId, [{ variantId: variant!.id, qty: 4 }], {
      expiresAt: new Date(Date.now() + 3600_000),
    });

    const after = await getProductBySlug("snacks-huesitos-dentales");
    expect(after?.variants[0]?.available).toBe(variant!.available - 4);
  });

  it("busca por FULLTEXT y por prefijo", async () => {
    const exact = await searchProducts("rascador");
    expect(exact.map((product) => product.slug)).toContain("rascador-gato-poste");

    const prefix = await searchProducts("rasca");
    expect(prefix.map((product) => product.slug)).toContain("rascador-gato-poste");
  });

  it("cae al LIKE con términos cortos que FULLTEXT ignora", async () => {
    // "cama" tiene 4 caracteres: entra justo, pero el fallback es lo que
    // salva a "collar" y compañía si ft_min_word_len sube.
    const camas = await searchProducts("cama");
    expect(camas.map((product) => product.slug)).toContain("cama-acolchada-perro");
  });

  it("no devuelve nada con términos vacíos o de una letra", async () => {
    expect(await searchProducts("")).toEqual([]);
    expect(await searchProducts("a")).toEqual([]);
    expect(await searchProducts("   ")).toEqual([]);
  });

  it("no rompe con caracteres especiales del modo booleano", async () => {
    await expect(searchProducts('collar +-><()~*"@')).resolves.toBeInstanceOf(Array);
  });

  /**
   * El sitemap le enseña al buscador qué existe. Un producto despublicado que
   * siga en el XML es una promesa de 404 —y peor, es publicar algo que el
   * comercio decidió esconder—, así que el filtro tiene que ser el mismo de la
   * vidriera y no una consulta paralela que se olvide de `published_at`.
   */
  it("el sitemap lista sólo lo que la vidriera muestra", async () => {
    const antes = await getSitemapEntries();
    expect(antes.categories.map((category) => category.slug)).toEqual([
      "alimentos",
      "juguetes",
      "accesorios",
      "higiene-y-salud",
    ]);
    expect(antes.products.map((product) => product.slug)).toContain("cama-acolchada-perro");

    await getDb()
      .update(products)
      .set({ publishedAt: null })
      .where(eq(products.slug, "cama-acolchada-perro"));

    const despues = await getSitemapEntries();
    expect(despues.products.map((product) => product.slug)).not.toContain("cama-acolchada-perro");
    expect(despues.products).toHaveLength(antes.products.length - 1);

    await getDb()
      .update(products)
      .set({ publishedAt: new Date() })
      .where(eq(products.slug, "cama-acolchada-perro"));
  });
});
