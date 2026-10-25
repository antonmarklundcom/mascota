import { eq } from 'drizzle-orm';
import { afterAll, beforeEach, describe, expect, it, vi } from 'vitest';

import { lookupOrder } from '@/app/actions/order-lookup';
import { customers, orders } from '@/db/schema';
import { registerCustomer } from '@/domain/customers';
import { resetRateLimitKey, resetRateLimits } from '@/lib/rate-limit';

import { closeTestDb, getTestDb, hasTestDb, resetTables } from '../helpers/db';
import { createOrder } from '../helpers/factories';

/**
 * "Buscar mi pedido" (número + teléfono) contra MySQL.
 *
 * Número de pedido y teléfono no son secretos, así que lo que se prueba es que
 * con esos dos datos solos **nunca** vuelva el link privado del pedido: o sale
 * por WhatsApp al teléfono del pedido, o se lo ve una cuenta que ya verificó
 * ese teléfono.
 */

const mocks = vi.hoisted(() => ({
  actor: null as null | { customerId: number; phone: string; name: string },
  after: vi.fn(),
}));

vi.mock('next/headers', () => ({
  headers: async () => new Headers({ 'x-forwarded-for': '127.0.0.1' }),
}));
vi.mock('next/server', () => ({ after: mocks.after }));
vi.mock('@/lib/customer-session', () => ({ currentCustomer: async () => mocks.actor }));
vi.mock('@/config/tienda', async (importOriginal) => ({
  ...(await importOriginal<typeof import('@/config/tienda')>()),
  cuentasClientesHabilitadas: () => true,
}));

async function unPedido(customerPhone?: string) {
  const id = await createOrder(customerPhone ? { customerPhone } : {});
  const [order] = await getTestDb().select().from(orders).where(eq(orders.id, id));
  return order!;
}

describe.skipIf(!hasTestDb)('buscar mi pedido', () => {
  beforeEach(async () => {
    await resetTables();
    resetRateLimits();
    mocks.actor = null;
    mocks.after.mockClear();
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
  });
  afterAll(async () => {
    vi.unstubAllEnvs();
    vi.unstubAllGlobals();
    await closeTestDb();
  });

  it('número y teléfono correctos contestan lo mismo que un pedido que no existe', async () => {
    const order = await unPedido();

    const found = await lookupOrder({ orderNumber: order.orderNumber, phone: order.customerPhone });
    const absent = await lookupOrder({ orderNumber: 'PY-999999', phone: '0982123456' });

    expect(found).toEqual(absent);
    expect(found).not.toHaveProperty('redirectTo');
    expect(JSON.stringify(found)).not.toContain(order.accessToken);
  });

  it('una cuenta sin verificar no recibe el link; la dueña verificada sí', async () => {
    const cuenta = await registerCustomer({
      phone: '0981123456',
      name: 'Rosa Giménez',
      password: 'tienda2026segura',
    });
    mocks.actor = { customerId: cuenta.id, phone: cuenta.phone, name: cuenta.name };
    const order = await unPedido(cuenta.phone);

    expect(await lookupOrder({ orderNumber: order.orderNumber, phone: cuenta.phone })).not.toHaveProperty(
      'redirectTo',
    );

    await getTestDb()
      .update(customers)
      .set({ phoneVerifiedAt: new Date() })
      .where(eq(customers.id, cuenta.id));

    expect(await lookupOrder({ orderNumber: order.orderNumber, phone: cuenta.phone })).toMatchObject({
      ok: true,
      redirectTo: expect.stringContaining(order.accessToken),
    });
  });

  it('con la plantilla de recuperación, el link sale por WhatsApp después de responder', async () => {
    vi.stubEnv('WHATSAPP_CLOUD_PHONE_NUMBER_ID', 'test-phone-id');
    vi.stubEnv('WHATSAPP_CLOUD_ACCESS_TOKEN', 'invented-test-value');
    vi.stubEnv('WHATSAPP_CLOUD_TEMPLATE_NAME', 'login_code');
    vi.stubEnv('WHATSAPP_CLOUD_TEMPLATE_CLIENTE_RECUPERAR_PEDIDO', 'order_recovery');
    const fetch = vi
      .fn()
      .mockResolvedValue(new Response(JSON.stringify({ messages: [{ id: 'test' }] }), { status: 200 }));
    vi.stubGlobal('fetch', fetch);
    const order = await unPedido();

    const result = await lookupOrder({ orderNumber: order.orderNumber, phone: order.customerPhone });
    expect(result).not.toHaveProperty('redirectTo');
    expect(JSON.stringify(result)).not.toContain(order.accessToken);
    expect(fetch).not.toHaveBeenCalled();

    await mocks.after.mock.calls[0]![0]();
    const payload = JSON.parse(fetch.mock.calls[0]![1].body);
    expect(payload.to).toBe(order.customerPhone.replace(/^\+/, ''));
    expect(payload.template.name).toBe('order_recovery');
    expect(payload.template.components[0].parameters[0].text).toContain(order.accessToken);
  });

  it('sin la plantilla de recuperación no usa la del login para mandar el link', async () => {
    vi.stubEnv('WHATSAPP_CLOUD_PHONE_NUMBER_ID', 'test-phone-id');
    vi.stubEnv('WHATSAPP_CLOUD_ACCESS_TOKEN', 'invented-test-value');
    vi.stubEnv('WHATSAPP_CLOUD_TEMPLATE_NAME', 'login_code');
    const fetch = vi.fn();
    vi.stubGlobal('fetch', fetch);
    const order = await unPedido();

    const result = await lookupOrder({ orderNumber: order.orderNumber, phone: order.customerPhone });
    expect(result).not.toHaveProperty('redirectTo');
    expect(mocks.after).not.toHaveBeenCalled();
    expect(fetch).not.toHaveBeenCalled();
  });

  it('limita por número de pedido aunque cambien la IP y el teléfono', async () => {
    const order = await unPedido();
    const cuenta = await registerCustomer({
      phone: order.customerPhone,
      name: 'Rosa Giménez',
      password: 'tienda2026segura',
    });
    await getTestDb()
      .update(customers)
      .set({ phoneVerifiedAt: new Date() })
      .where(eq(customers.id, cuenta.id));
    mocks.actor = { customerId: cuenta.id, phone: cuenta.phone, name: cuenta.name };

    // Cinco intentos con teléfonos equivocados agotan el número de pedido…
    for (let i = 0; i < 5; i += 1) {
      await lookupOrder({ orderNumber: order.orderNumber, phone: `098200000${i}` });
      // La IP del test es siempre la misma: se limpia sólo su balde.
      resetRateLimitKey('lookup:127.0.0.1');
    }
    // …y ni el teléfono correcto lo abre hasta que pase la ventana.
    expect(await lookupOrder({ orderNumber: order.orderNumber, phone: order.customerPhone })).not.toHaveProperty(
      'redirectTo',
    );
  });
});
