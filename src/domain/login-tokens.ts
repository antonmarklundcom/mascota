import { createHash, randomBytes, timingSafeEqual } from 'node:crypto';
import type { MessageKey, Params } from '@/i18n';

import { DomainError } from './errors';

import { and, desc, eq, gt, isNull, sql } from 'drizzle-orm';

import { getDb } from '@/db';
import { customers, loginTokens } from '@/db/schema';
import { normalizePhonePY } from '@/lib/py';

import type { Executor } from './executor';
import type { MessageChannel } from './messaging';

/**
 * Códigos de un solo uso para entrar sin contraseña (PLAN.md FASE 2, PR F.1).
 *
 * Las cinco propiedades que lo hacen seguro, y por qué cada una:
 *
 * 1. **Se guarda el hash, nunca el código.** Un dump de la base, un backup o
 *    una consulta de soporte no pueden abrir la sesión de nadie.
 * 2. **Un solo uso.** `consumed_at` se escribe adentro de la transacción que
 *    lo canjea, con un UPDATE condicional: dos pestañas con el mismo código no
 *    abren dos sesiones.
 * 3. **Expira a los 10 minutos.** Es el tiempo de mirar el teléfono, no el de
 *    encontrar un WhatsApp viejo el mes que viene.
 * 4. **Pedir uno nuevo invalida los anteriores.** Si no, cada pedido suma otro
 *    código vivo y la ventana de adivinación crece con cada intento.
 * 5. **Comparación en tiempo constante.** Sobre el hash, con `timingSafeEqual`.
 * 6. **El código sólo vale junto con la cuenta.** El hash incluye el id del
 *    cliente y el canje exige el teléfono: adivinar "algún código vivo" no
 *    abre la sesión de nadie. Además cada código admite pocos intentos
 *    fallidos (`LOGIN_TOKEN_MAX_ATTEMPTS`), guardados en la base y no en
 *    memoria, así que no se reinician con el proceso ni se evaden rotando IPs.
 *
 * El código es de 6 dígitos porque se tipea desde un mensaje; lo que compensa
 * ese espacio chico es el rate limit y la expiración, no el largo.
 */

/** 10 minutos, como pide el plan. */
export const LOGIN_TOKEN_TTL_MS = 10 * 60 * 1000;

const CODE_DIGITS = 6;

/** Intentos fallidos por código; al llegar acá el código muere y hay que pedir otro. */
export const LOGIN_TOKEN_MAX_ATTEMPTS = 5;

export class LoginTokenError extends DomainError {
  constructor(code: MessageKey, params?: Params) {
    super(code, params);
    this.name = 'LoginTokenError';
  }
}

/**
 * Seis dígitos con aleatoriedad criptográfica y **sin sesgo**.
 *
 * `randomBytes % 1000000` parece equivalente y no lo es: los primeros valores
 * quedan levemente más probables. Se descarta y se vuelve a tirar en vez de
 * repartir mal el espacio, que es chico de por sí.
 */
export function generateLoginCode(): string {
  const limit = 10 ** CODE_DIGITS;
  const max = Math.floor(0xffffffff / limit) * limit;

  for (;;) {
    const value = randomBytes(4).readUInt32BE(0);
    if (value < max) return String(value % limit).padStart(CODE_DIGITS, '0');
  }
}

/**
 * SHA-256 hex, atado a la cuenta: el mismo código en dos cuentas da hashes
 * distintos. Ver el comentario de la tabla: no hace falta bcrypt acá.
 */
export function hashLoginCode(customerId: number, code: string): string {
  return createHash('sha256').update(`${customerId}:${code.trim()}`).digest('hex');
}

/**
 * Emite un código para esta cuenta e invalida los anteriores.
 *
 * Devuelve el código **en claro una sola vez**: es lo único que se le manda a
 * la persona, y no vuelve a existir en ningún lado.
 */
export async function issueLoginToken(
  customerId: number,
  channel: MessageChannel,
  executor?: Executor,
): Promise<{ code: string; expiresAt: Date }> {
  const tx = executor ?? getDb();
  const expiresAt = new Date(Date.now() + LOGIN_TOKEN_TTL_MS);

  // Invalidar primero: si esto fallara después de insertar, quedarían dos
  // códigos vivos, que es exactamente lo que la regla 4 evita.
  await tx
    .update(loginTokens)
    .set({ invalidatedAt: sql`NOW()` })
    .where(
      and(
        eq(loginTokens.customerId, customerId),
        isNull(loginTokens.consumedAt),
        isNull(loginTokens.invalidatedAt),
      ),
    );

  /**
   * Reintentar ante una colisión de hash.
   *
   * `token_hash` es UNIQUE sobre **toda la tabla**, y las filas no se borran
   * nunca (consumidas e invalidadas se conservan para poder reconstruir un
   * incidente). Con seis dígitos, el código nuevo que choca contra *cualquiera*
   * de los históricos rompe el INSERT — y el efecto es el peor posible: la
   * persona nunca recibe su código y no hay nada en pantalla que lo explique.
   *
   * La probabilidad crece con el uso: son N/1.000.000 por emisión, con N el
   * total histórico. Arranca en cero y a los diez mil logins ya es un 1%.
   *
   * La unicidad global se mantiene (así no hace falta una migración para
   * quitarla). Lo que se arregla es la reacción — tirar de nuevo, que es gratis.
   */
  for (let intento = 0; intento < 5; intento += 1) {
    const code = generateLoginCode();
    const tokenHash = hashLoginCode(customerId, code);

    try {
      await tx.insert(loginTokens).values({ customerId, tokenHash, channel, expiresAt });
      return { code, expiresAt };
    } catch (error) {
      if (!esColisionDeHash(error)) throw error;
    }
  }

  throw new LoginTokenError('error.cuenta.codigoNoPude');
}

export type ConsumedToken = { customerId: number };

/**
 * Canjea un código **de esta cuenta**. Devuelve `null` en cualquier fallo, sin
 * distinguir cuál: no existe, ya se usó, venció, lo invalidó otro pedido, se
 * agotaron los intentos o la cuenta se desactivó. Distinguirlos convertiría
 * este formulario en un oráculo.
 *
 * Un código solo nunca identifica a nadie: se busca la cuenta por teléfono y
 * sólo se compara contra el código vivo de esa cuenta. Cada fallo suma un
 * intento (en la base) y al quinto el código se invalida.
 */
export async function consumeLoginToken(
  phone: string,
  code: string,
): Promise<ConsumedToken | null> {
  const normalized = normalizePhonePY(phone);
  const candidate = code.trim();
  if (!normalized || !/^\d{6}$/.test(candidate)) return null;

  return getDb().transaction(async (tx) => {
    const customerRows = await tx
      .select({ id: customers.id, isActive: customers.isActive })
      .from(customers)
      .where(eq(customers.phone, normalized))
      .limit(1)
      .for('update');
    const customer = customerRows[0];
    if (!customer?.isActive) return null;

    const rows = await tx
      .select({
        id: loginTokens.id,
        tokenHash: loginTokens.tokenHash,
        attempts: loginTokens.attempts,
      })
      .from(loginTokens)
      .where(
        and(
          eq(loginTokens.customerId, customer.id),
          isNull(loginTokens.consumedAt),
          isNull(loginTokens.invalidatedAt),
          gt(loginTokens.expiresAt, new Date()),
        ),
      )
      .orderBy(desc(loginTokens.id))
      .limit(1)
      .for('update');
    const token = rows[0];
    if (!token) return null;

    // En tiempo constante y sobre el hash atado a la cuenta.
    const esperado = Buffer.from(token.tokenHash, 'utf8');
    const recibido = Buffer.from(hashLoginCode(customer.id, candidate), 'utf8');
    const attempts = token.attempts + 1;
    if (
      token.attempts >= LOGIN_TOKEN_MAX_ATTEMPTS ||
      esperado.length !== recibido.length ||
      !timingSafeEqual(esperado, recibido)
    ) {
      await tx
        .update(loginTokens)
        .set({
          attempts,
          ...(attempts >= LOGIN_TOKEN_MAX_ATTEMPTS ? { invalidatedAt: sql`NOW()` } : {}),
        })
        .where(eq(loginTokens.id, token.id));
      return null;
    }

    // El UPDATE condicional es el candado real del "un solo uso".
    await tx
      .update(loginTokens)
      .set({ consumedAt: sql`NOW()` })
      .where(and(eq(loginTokens.id, token.id), isNull(loginTokens.consumedAt)));

    /**
     * Entrar con un código que llegó al teléfono **prueba** que ese teléfono es
     * suyo, que es justo lo que faltaba en el PR E. A partir de acá `/cuenta`
     * puede mostrarle los pedidos viejos que hizo como invitada con ese
     * número: ya no es "alguien que tipeó un número", es su número.
     */
    await tx
      .update(customers)
      .set({ phoneVerifiedAt: sql`NOW()`, lastLoginAt: sql`NOW()` })
      .where(eq(customers.id, customer.id));

    return { customerId: customer.id };
  });
}

/** El INSERT chocó contra el UNIQUE de `token_hash` y no contra otra cosa. */
function esColisionDeHash(error: unknown): boolean {
  const code = (error as { code?: string; errno?: number } | null)?.code;
  const errno = (error as { errno?: number } | null)?.errno;
  return code === 'ER_DUP_ENTRY' || errno === 1062;
}

/** El texto que se manda. Corto: entra entero en la notificación del celular. */
export function loginCodeMessage(code: string): string {
  return `${code} es tu código para entrar. Vence en 10 minutos. Si no lo pediste, ignorá este mensaje.`;
}
