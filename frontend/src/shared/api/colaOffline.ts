import { createStore, del, entries, set } from 'idb-keyval';

// Reportes hechos sin señal: se guardan en IndexedDB (sobrevive a cerrar la app) y se reenvían al volver la red.
const store = createStore('naangareko', 'cola');

export type Cuerpo =
  | { tipo: 'json'; datos: unknown }
  | { tipo: 'form'; campos: Record<string, string | Blob> };

export type Pendiente = { path: string; cuerpo: Cuerpo };

export const encolar = (p: Pendiente) => set(`${Date.now()}-${Math.random()}`, p, store);
export const pendientes = () => entries<string, Pendiente>(store);
export const quitar = (clave: string) => del(clave, store);
