import { encolar, pendientes, quitar, type Cuerpo } from './colaOffline';

const BASE = '/api';

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

let idMemoria: string | undefined;
const nuevoId = () => crypto.randomUUID?.() ?? `${Date.now().toString(36)}-${Math.random().toString(36).slice(2)}`;

/** Identificador anónimo del celular: el backend lo usa solo para anti-spam. */
export function deviceId(): string {
  try {
    let id = localStorage.getItem('device_id');
    if (!id) localStorage.setItem('device_id', (id = nuevoId()));
    return id;
  } catch {
    return (idMemoria ??= nuevoId());
  }
}

function aInit(c: Cuerpo): RequestInit {
  if (c.tipo === 'json') {
    return { method: 'POST', body: JSON.stringify(c.datos), headers: { 'Content-Type': 'application/json' } };
  }
  const form = new FormData();
  for (const [k, v] of Object.entries(c.campos)) {
    if (v instanceof Blob) form.append(k, v, `${k}.jpg`);
    else form.append(k, v);
  }
  return { method: 'POST', body: form };
}

async function pedir(path: string, init: RequestInit, timeoutMs: number): Promise<Response> {
  const res = await fetch(BASE + path, {
    ...init,
    headers: { ...init.headers, 'X-Device-Id': deviceId() },
    signal: AbortSignal.timeout(timeoutMs),
  });
  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(res.status, typeof body?.detail === 'string' ? body.detail : 'Datos inválidos o error del servidor');
  }
  return res;
}

export async function getJson<T>(path: string): Promise<T> {
  return (await pedir(path, {}, 10_000)).json();
}

/** POST directo, sin cola offline (acciones de administración que deben confirmarse en el momento). */
export async function postJson<T>(path: string, datos: unknown, headers: Record<string, string> = {}): Promise<T> {
  const res = await pedir(path, {
    method: 'POST', body: JSON.stringify(datos), headers: { 'Content-Type': 'application/json', ...headers },
  }, 15_000);
  return res.json();
}

export type Envio<T> = { estado: 'enviado'; data: T } | { estado: 'encolado' };

/** POST que nunca pierde el reporte: si no hay red, queda en cola y se reenvía después. */
export async function enviar<T>(path: string, cuerpo: Cuerpo): Promise<Envio<T>> {
  try {
    const res = await pedir(path, aInit(cuerpo), 45_000);
    return { estado: 'enviado', data: await res.json() };
  } catch (e) {
    if (e instanceof ApiError) throw e; // el servidor respondió: reintentar no lo arregla
    await encolar({ path, cuerpo });
    return { estado: 'encolado' };
  }
}

let reenviando = false;

/** Reenvía los reportes guardados sin señal. Devuelve cuántos se enviaron. */
export async function reenviarCola(): Promise<number> {
  if (reenviando || !navigator.onLine) return 0;
  reenviando = true;
  let enviados = 0;
  try {
    for (const [clave, p] of await pendientes()) {
      try {
        await pedir(p.path, aInit(p.cuerpo), 45_000);
        await quitar(clave);
        enviados++;
      } catch (e) {
        // Rechazo definitivo (4xx salvo 429): descartar. Red o servidor caído: probar en el próximo "online".
        if (e instanceof ApiError && e.status < 500 && e.status !== 429) await quitar(clave);
        else break;
      }
    }
  } finally {
    reenviando = false;
  }
  return enviados;
}
