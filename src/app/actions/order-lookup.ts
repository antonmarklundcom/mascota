"use server";

import { headers } from "next/headers";
import { after } from "next/server";
import { z } from "zod";

import { cuentasClientesHabilitadas } from "@/config/tienda";
import { findCustomerById } from "@/domain/customers";
import { resolveMessageSender, type MessageSender } from "@/domain/messaging";
import { findOrderByNumberAndPhone, orderUrl } from "@/domain/order-access";
import { buyerOrderUrl } from "@/domain/order-messages";
import { t, tPlural } from "@/i18n";
import { currentCustomer } from "@/lib/customer-session";
import { normalizePhonePY } from "@/lib/py";
import { LOOKUP_LIMIT, LOOKUP_WINDOW_MS, clientIp, rateLimit } from "@/lib/rate-limit";

/**
 * Búsqueda del pedido por número + teléfono (PLAN.md 3.9).
 *
 * **El link privado nunca vuelve en la respuesta a quien no probó nada.** Un
 * número de pedido es correlativo (PY-000123) y un teléfono no es un secreto:
 * con los dos, cualquiera podía abrir el pedido de otra persona —nombre,
 * dirección, teléfono— y subirle un comprobante. Ahora:
 *
 * 1. Con la plantilla `WHATSAPP_CLOUD_TEMPLATE_CLIENTE_RECUPERAR_PEDIDO`, el
 *    link se manda **al WhatsApp del pedido**, después de responder.
 * 2. Sin plantilla, sólo lo recibe en pantalla una clienta con sesión cuyo
 *    teléfono ya está verificado y es el del pedido.
 * 3. En cualquier otro caso, el mismo mensaje genérico: exista o no el pedido,
 *    coincida o no el teléfono. Cualquier diferencia convierte el formulario
 *    en un oráculo de números de pedido válidos.
 *
 * Límites por IP, por teléfono y por número de pedido: rotar uno solo no da
 * intentos nuevos.
 */

/**
 * Una función y no una constante: `t()` se resuelve al importar el módulo, y
 * una constante de módulo la congelaría antes de que nadie la pida. Cuesta
 * nada y evita el bug tonto del día que el catálogo se elija en runtime.
 */
const genericError = (): string => t("error.buscarPedido.noEncontrado");

const LookupSchema = z.object({
  orderNumber: z.string().trim().min(3).max(16),
  phone: z.string().trim().min(6).max(30),
});

export type LookupResult =
  | { ok: true; redirectTo: string }
  | { ok: true; message: string }
  | { ok: false; error: string };

/**
 * Con qué mandar el link, o `null` si esta tienda no lo pidió. Sin plantilla
 * no sale nada, ni por la consola de dev: mandar el link es una decisión de
 * cada tienda, no un default.
 */
function recoveryNotifier(): { sender: MessageSender; templateName?: string } | null {
  const templateName = process.env.WHATSAPP_CLOUD_TEMPLATE_CLIENTE_RECUPERAR_PEDIDO?.trim();
  if (!templateName) return null;
  const sender = resolveMessageSender();
  if (!sender) return null;
  return sender.channel === "whatsapp" ? { sender, templateName } : { sender };
}

export async function lookupOrder(input: unknown): Promise<LookupResult> {
  const ip = clientIp(await headers());
  const limit = rateLimit(`lookup:${ip}`, { limit: LOOKUP_LIMIT, windowMs: LOOKUP_WINDOW_MS });

  if (!limit.ok) {
    const minutes = Math.ceil(limit.retryAfterSeconds / 60);
    return { ok: false, error: tPlural("error.buscarPedido.demasiados", minutes) };
  }

  const parsed = LookupSchema.safeParse(input);
  if (!parsed.success) {
    return { ok: false, error: genericError() };
  }

  const generic: LookupResult = { ok: true, message: t("buscarPedido.recuperacion") };
  const phone = normalizePhonePY(parsed.data.phone);
  const number = parsed.data.orderNumber.toUpperCase();
  const options = { limit: LOOKUP_LIMIT, windowMs: LOOKUP_WINDOW_MS };
  if (
    !phone ||
    !rateLimit(`lookup:phone:${phone}`, options).ok ||
    !rateLimit(`lookup:order:${number}`, options).ok
  ) {
    return generic;
  }

  const found = await findOrderByNumberAndPhone(number, phone);

  const notifier = recoveryNotifier();
  if (notifier) {
    // Después de responder: así el pedido que existe y el que no tardan lo
    // mismo, y el tiempo de respuesta tampoco delata nada.
    if (found) {
      after(async () => {
        // El sender de WhatsApp ya corta a los 10 s (AbortSignal.timeout).
        try {
          await notifier.sender.send({
            to: phone,
            body: t("wa.cliente.verPedido", { url: buyerOrderUrl(found) }),
            templateName: notifier.templateName,
          });
        } catch (error) {
          // Sólo el mensaje: el error no debe llevar el link ni el teléfono al log.
          console.error(
            "No pude mandar el link de recuperación del pedido",
            error instanceof Error ? error.message : "error desconocido",
          );
        }
      });
    }
    return generic;
  }

  // Sin mensajería, el link sólo se muestra a quien ya probó que el teléfono
  // es suyo: una cuenta con el teléfono verificado y con sesión abierta.
  const actor = cuentasClientesHabilitadas() ? await currentCustomer() : null;
  const account = actor ? await findCustomerById(actor.customerId) : null;
  if (found && account?.phoneVerifiedAt && account.phone === phone) {
    return { ok: true, redirectTo: orderUrl(found.orderNumber, found.accessToken) };
  }

  return generic;
}
