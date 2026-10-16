// Corre con: npm test (usa el runner de Node, sin dependencias extra).
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { leerCoordenadas } from './coordenadas.ts';

const ok = (texto: string) => {
  const r = leerCoordenadas(texto);
  assert.ok(r.ok, `debería leer: ${texto} → ${!r.ok && r.error}`);
  return r.coord;
};

test('link de lugar: prefiere el pin (!3d!4d) sobre el centro de la vista (@)', () => {
  const url = 'https://www.google.com/maps/place/UPE/@-25.5500,-54.6000,17z/data=!3m1!4b1!4m6!3m5!8m2!3d-25.5561!4d-54.6112';
  assert.deepEqual(ok(url), { lat: -25.5561, lon: -54.6112 });
});

test('link con @ solamente', () => {
  assert.deepEqual(ok('https://www.google.com/maps/@-25.5097,-54.6111,15z'), { lat: -25.5097, lon: -54.6111 });
});

test('link de búsqueda con q= y coma codificada', () => {
  assert.deepEqual(ok('https://maps.google.com/?q=-25.4058%2C-54.6386'), { lat: -25.4058, lon: -54.6386 });
});

test('link de la API de Maps (query=)', () => {
  assert.deepEqual(ok('https://www.google.com/maps/search/?api=1&query=-25.4833,-54.8'), { lat: -25.4833, lon: -54.8 });
});

test('coordenadas pegadas a mano', () => {
  assert.deepEqual(ok('  -25.5560, -54.6110 '), { lat: -25.556, lon: -54.611 });
});

test('link corto: pide el link largo', () => {
  const r = leerCoordenadas('https://maps.app.goo.gl/AbCdEf123');
  assert.ok(!r.ok && r.error.includes('link corto'));
});

test('fuera de Alto Paraná (Asunción)', () => {
  const r = leerCoordenadas('https://www.google.com/maps/@-25.2637,-57.5759,14z');
  assert.ok(!r.ok && r.error.includes('fuera'));
});

test('texto sin coordenadas', () => {
  assert.equal(leerCoordenadas('Universidad Privada del Este').ok, false);
});
