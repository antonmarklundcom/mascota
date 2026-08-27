import type { IvaRate } from '@/db/schema';

export type SeedVariant = {
  sku: string;
  label: string;
  pricePyg: number;
  compareAtPyg?: number;
  onHand: number;
};

export type SeedProduct = {
  slug: string;
  name: string;
  description: string;
  categorySlug: string;
  brand: string;
  ivaRate: IvaRate;
  variants: SeedVariant[];
};

/**
 * El catálogo de arranque de Mascota PY.
 *
 * Es un **punto de partida mostrable**, no el catálogo real: NEW-STORE.md §4
 * dice que se reemplaza por el del comercio, de a uno desde `/admin/productos`
 * o entero con `pnpm importar:productos lista.csv`. Los precios son de góndola
 * paraguaya, en guaraníes enteros y con IVA incluido, para que una demo no
 * muestre cifras imposibles.
 *
 * Las cuatro categorías son las que después tienen ilustración propia en
 * `public/placeholders/` (ver `src/lib/images.ts`): si acá se agrega una
 * quinta, o le hacés su SVG o cae en el placeholder genérico.
 */
export const SEED_CATEGORIES = [
  { slug: 'alimentos', name: 'Alimento', position: 1 },
  { slug: 'juguetes', name: 'Juguetes', position: 2 },
  { slug: 'accesorios', name: 'Accesorios', position: 3 },
  { slug: 'higiene-y-salud', name: 'Higiene y Salud', position: 4 },
] as const;

/** Precios reales de góndola paraguaya, IVA incluido, en guaraníes enteros. */
export const SEED_PRODUCTS: SeedProduct[] = [
  // --- Alimento ------------------------------------------------------------
  {
    slug: 'alimento-perro-adulto-carne',
    name: 'Alimento para perro adulto sabor carne',
    description:
      'Alimento balanceado completo para perros adultos de raza mediana y grande, con proteína de carne y cereales.',
    categorySlug: 'alimentos',
    brand: 'Pedigree',
    ivaRate: 10,
    variants: [
      { sku: 'ALP-ADU-3K', label: '3 kg', pricePyg: 62000, onHand: 40 },
      { sku: 'ALP-ADU-15K', label: '15 kg', pricePyg: 265000, compareAtPyg: 295000, onHand: 22 },
    ],
  },
  {
    slug: 'alimento-cachorro-pollo',
    name: 'Alimento para cachorro sabor pollo',
    description:
      'Balanceado para cachorros hasta 12 meses, con calcio y DHA para el desarrollo de huesos y visión.',
    categorySlug: 'alimentos',
    brand: 'Dog Chow',
    ivaRate: 10,
    variants: [
      { sku: 'ALP-CAC-2K', label: '2 kg', pricePyg: 58000, onHand: 35 },
      { sku: 'ALP-CAC-8K', label: '8 kg', pricePyg: 195000, onHand: 18 },
    ],
  },
  {
    slug: 'alimento-gato-adulto-pescado',
    name: 'Alimento para gato adulto sabor pescado',
    description:
      'Balanceado para gatos adultos con taurina y control de bolas de pelo. Croqueta chica.',
    categorySlug: 'alimentos',
    brand: 'Whiskas',
    ivaRate: 10,
    variants: [
      { sku: 'ALG-ADU-1K', label: '1 kg', pricePyg: 39000, onHand: 50 },
      { sku: 'ALG-ADU-7K', label: '7 kg', pricePyg: 215000, compareAtPyg: 240000, onHand: 16 },
    ],
  },
  {
    slug: 'lata-humeda-perro-mix',
    name: 'Alimento húmedo en lata para perro',
    description: 'Trozos de carne y vegetales en salsa, lata de 340 g. Ideal para mezclar con el balanceado.',
    categorySlug: 'alimentos',
    brand: 'Pedigree',
    ivaRate: 10,
    variants: [
      { sku: 'ALH-PER-340', label: 'Lata 340 g', pricePyg: 18000, onHand: 90 },
      { sku: 'ALH-PER-PACK6', label: 'Pack x6 latas', pricePyg: 99000, compareAtPyg: 108000, onHand: 24 },
    ],
  },
  {
    slug: 'snacks-huesitos-dentales',
    name: 'Snacks dentales para perro',
    description: 'Huesitos masticables que ayudan a reducir el sarro. Bolsa de 7 unidades.',
    categorySlug: 'alimentos',
    brand: 'Dentastix',
    ivaRate: 10,
    variants: [{ sku: 'SNK-DEN-7U', label: 'Bolsa x7', pricePyg: 32000, onHand: 60 }],
  },
  {
    slug: 'snacks-gato-atun',
    name: 'Snacks cremosos para gato sabor atún',
    description: 'Premio cremoso en sachet, se da a mano o sobre el plato. Caja de 4 sachets.',
    categorySlug: 'alimentos',
    brand: 'Whiskas',
    ivaRate: 10,
    variants: [{ sku: 'SNK-GAT-4S', label: 'Caja x4', pricePyg: 24000, onHand: 70 }],
  },

  // --- Juguetes ------------------------------------------------------------
  {
    slug: 'pelota-caucho-resistente',
    name: 'Pelota de caucho resistente',
    description: 'Pelota maciza que rebota y flota, para perros mordedores. No se deshace de una tarde.',
    categorySlug: 'juguetes',
    brand: 'Kong',
    ivaRate: 10,
    variants: [
      { sku: 'JUG-PEL-M', label: 'Mediana', pricePyg: 48000, onHand: 30 },
      { sku: 'JUG-PEL-G', label: 'Grande', pricePyg: 65000, onHand: 20 },
    ],
  },
  {
    slug: 'mordillo-cuerda-trenzada',
    name: 'Mordillo de cuerda trenzada',
    description: 'Cuerda de algodón con nudos, para jugar al tira y afloja y limpiar los dientes.',
    categorySlug: 'juguetes',
    brand: 'PetPlay',
    ivaRate: 10,
    variants: [{ sku: 'JUG-CUE-35', label: '35 cm', pricePyg: 29000, onHand: 45 }],
  },
  {
    slug: 'rascador-gato-poste',
    name: 'Rascador para gato con poste',
    description: 'Base de madera con poste forrado en sisal y pelota colgante. Salva los sillones.',
    categorySlug: 'juguetes',
    brand: 'MiauHouse',
    ivaRate: 10,
    variants: [
      { sku: 'JUG-RAS-45', label: '45 cm', pricePyg: 145000, onHand: 14 },
      { sku: 'JUG-RAS-70', label: '70 cm', pricePyg: 245000, compareAtPyg: 275000, onHand: 8 },
    ],
  },
  {
    slug: 'varita-plumas-gato',
    name: 'Varita con plumas para gato',
    description: 'Caña flexible con plumas y cascabel. El juguete que más activa el instinto de caza.',
    categorySlug: 'juguetes',
    brand: 'MiauHouse',
    ivaRate: 10,
    variants: [{ sku: 'JUG-VAR-PLU', label: 'Única', pricePyg: 22000, onHand: 55 }],
  },
  {
    slug: 'juguete-dispensador-premios',
    name: 'Juguete dispensador de premios',
    description: 'Se rellena con snacks y los suelta de a poco: entretiene al perro que queda solo.',
    categorySlug: 'juguetes',
    brand: 'Kong',
    ivaRate: 10,
    variants: [{ sku: 'JUG-DIS-M', label: 'Mediano', pricePyg: 89000, onHand: 18 }],
  },
  {
    slug: 'peluche-chillon-perro',
    name: 'Peluche con chillón para perro',
    description: 'Peluche blando con silbato interno, costuras reforzadas. Para perros de mordida suave.',
    categorySlug: 'juguetes',
    brand: 'PetPlay',
    ivaRate: 10,
    variants: [{ sku: 'JUG-PEL-CHI', label: 'Única', pricePyg: 35000, onHand: 40 }],
  },

  // --- Accesorios ----------------------------------------------------------
  {
    slug: 'cama-acolchada-perro',
    name: 'Cama acolchada para perro',
    description: 'Cama con borde elevado y funda lavable a máquina. Base antideslizante.',
    categorySlug: 'accesorios',
    brand: 'CasaPet',
    ivaRate: 10,
    variants: [
      { sku: 'ACC-CAM-M', label: 'Mediana (60 cm)', pricePyg: 185000, onHand: 12 },
      { sku: 'ACC-CAM-G', label: 'Grande (80 cm)', pricePyg: 265000, compareAtPyg: 299000, onHand: 7 },
    ],
  },
  {
    slug: 'casita-cueva-gato',
    name: 'Casita cueva para gato',
    description: 'Cueva de fieltro con almohadón desmontable: el escondite que los gatos eligen solos.',
    categorySlug: 'accesorios',
    brand: 'MiauHouse',
    ivaRate: 10,
    variants: [{ sku: 'ACC-CAS-GAT', label: 'Única', pricePyg: 215000, onHand: 9 }],
  },
  {
    slug: 'collar-regulable-hebilla',
    name: 'Collar regulable con hebilla',
    description: 'Collar de nylon con hebilla de seguridad y argolla para la chapita.',
    categorySlug: 'accesorios',
    brand: 'CasaPet',
    ivaRate: 10,
    variants: [
      { sku: 'ACC-COL-S', label: 'Chico', pricePyg: 35000, onHand: 40 },
      { sku: 'ACC-COL-M', label: 'Mediano', pricePyg: 42000, onHand: 35 },
      { sku: 'ACC-COL-L', label: 'Grande', pricePyg: 49000, onHand: 25 },
    ],
  },
  {
    slug: 'correa-retractil-5m',
    name: 'Correa retráctil 5 m',
    description: 'Correa extensible con freno y traba de una mano, hasta 25 kg.',
    categorySlug: 'accesorios',
    brand: 'Flexi',
    ivaRate: 10,
    variants: [{ sku: 'ACC-COR-5M', label: '5 m', pricePyg: 125000, onHand: 20 }],
  },
  {
    slug: 'comedero-doble-acero',
    name: 'Comedero doble de acero inoxidable',
    description: 'Dos boles de acero sobre base antideslizante: uno para el agua, otro para la comida.',
    categorySlug: 'accesorios',
    brand: 'CasaPet',
    ivaRate: 10,
    variants: [{ sku: 'ACC-COM-DOB', label: 'Único', pricePyg: 78000, onHand: 28 }],
  },
  {
    slug: 'transportadora-rigida',
    name: 'Transportadora rígida',
    description: 'Kennel de plástico con puerta metálica y rejillas de ventilación. Apta para viajar.',
    categorySlug: 'accesorios',
    brand: 'CasaPet',
    ivaRate: 10,
    variants: [
      { sku: 'ACC-TRA-S', label: 'Chica (hasta 8 kg)', pricePyg: 235000, onHand: 10 },
      { sku: 'ACC-TRA-M', label: 'Mediana (hasta 15 kg)', pricePyg: 345000, onHand: 6 },
    ],
  },

  // --- Higiene y Salud -----------------------------------------------------
  {
    slug: 'shampoo-perro-pelo-corto',
    name: 'Shampoo para perro de pelo corto',
    description: 'Shampoo con pH neutro para piel canina, deja brillo sin resecar. Frasco de 500 ml.',
    categorySlug: 'higiene-y-salud',
    brand: 'PetClean',
    ivaRate: 10,
    variants: [{ sku: 'HIG-SHA-500', label: '500 ml', pricePyg: 45000, onHand: 40 }],
  },
  {
    slug: 'piedra-sanitaria-gato',
    name: 'Piedra sanitaria para gato',
    description: 'Arena aglomerante con control de olor, hace pella y se retira fácil. Bolsa de 4 kg.',
    categorySlug: 'higiene-y-salud',
    brand: 'PetClean',
    ivaRate: 10,
    variants: [
      { sku: 'HIG-PIE-4K', label: '4 kg', pricePyg: 42000, onHand: 60 },
      { sku: 'HIG-PIE-10K', label: '10 kg', pricePyg: 92000, compareAtPyg: 105000, onHand: 25 },
    ],
  },
  {
    slug: 'pipeta-antipulgas-perro',
    name: 'Pipeta antipulgas y garrapatas para perro',
    description:
      'Pipeta de aplicación en la nuca, protege un mes. Elegí la medida según el peso del perro.',
    categorySlug: 'higiene-y-salud',
    brand: 'Frontline',
    ivaRate: 10,
    variants: [
      { sku: 'HIG-PIP-10', label: 'Hasta 10 kg', pricePyg: 68000, onHand: 30 },
      { sku: 'HIG-PIP-20', label: '10 a 20 kg', pricePyg: 82000, onHand: 22 },
      { sku: 'HIG-PIP-40', label: '20 a 40 kg', pricePyg: 98000, onHand: 15 },
    ],
  },
  {
    slug: 'cepillo-quita-pelo',
    name: 'Cepillo quita pelo muerto',
    description: 'Cepillo de púas finas con botón para soltar el pelo. Para perros y gatos de pelo largo.',
    categorySlug: 'higiene-y-salud',
    brand: 'PetClean',
    ivaRate: 10,
    variants: [{ sku: 'HIG-CEP-QP', label: 'Único', pricePyg: 55000, onHand: 32 }],
  },
  {
    slug: 'toallitas-humedas-mascota',
    name: 'Toallitas húmedas para mascotas',
    description: 'Toallitas sin alcohol para patas y hocico, envase de 100 unidades.',
    categorySlug: 'higiene-y-salud',
    brand: 'PetClean',
    ivaRate: 10,
    variants: [{ sku: 'HIG-TOA-100', label: 'Pack x100', pricePyg: 28000, onHand: 65 }],
  },
  {
    slug: 'bolsitas-sanitarias-paseo',
    name: 'Bolsitas sanitarias para el paseo',
    description: 'Rollos de bolsas biodegradables con dispensador para enganchar a la correa.',
    categorySlug: 'higiene-y-salud',
    brand: 'PetClean',
    ivaRate: 10,
    variants: [{ sku: 'HIG-BOL-8R', label: '8 rollos + dispensador', pricePyg: 33000, onHand: 48 }],
  },
];

export const SEED_SHIPPING_ZONES = [
  {
    slug: 'asuncion',
    name: 'Asunción',
    cities: ['Asunción'],
    pricePyg: 25000,
    freeThresholdPyg: 500000,
    position: 1,
  },
  {
    slug: 'gran-asuncion',
    name: 'Gran Asunción',
    cities: [
      'San Lorenzo',
      'Fernando de la Mora',
      'Luque',
      'Lambaré',
      'Capiatá',
      'Ñemby',
      'Mariano Roque Alonso',
      'Villa Elisa',
      'San Antonio',
      'Limpio',
      'Itauguá',
      'Areguá',
    ],
    pricePyg: 35000,
    freeThresholdPyg: 700000,
    position: 2,
  },
  {
    slug: 'ciudades-del-interior',
    name: 'Ciudades del interior',
    cities: [
      'Ciudad del Este',
      'Encarnación',
      'Coronel Oviedo',
      'Caaguazú',
      'Villarrica',
      'Pedro Juan Caballero',
      'Concepción',
      'Paraguarí',
      'San Juan Bautista',
      'Caacupé',
    ],
    pricePyg: 60000,
    freeThresholdPyg: 1500000,
    position: 3,
  },
  {
    slug: 'resto-del-pais',
    name: 'Resto del país',
    cities: [
      'Filadelfia',
      'Loma Plata',
      'Mariscal Estigarribia',
      'Pilar',
      'Salto del Guairá',
      'Ayolas',
      'Santa Rita',
      'Fuerte Olimpo',
    ],
    pricePyg: 95000,
    freeThresholdPyg: null,
    position: 4,
  },
] as const;
