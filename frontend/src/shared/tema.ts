export type Tema = 'sistema' | 'claro' | 'oscuro';

export const COLOR_PREDETERMINADO = '#0f766e';

export const PALETA = [
  { nombre: 'Turquesa Paraná', color: '#0f766e' },
  { nombre: 'Azul río', color: '#1d4ed8' },
  { nombre: 'Verde selva', color: '#15803d' },
  { nombre: 'Lapacho', color: '#be185d' },
  { nombre: 'Atardecer', color: '#c2410c' },
  { nombre: 'Jacarandá', color: '#7c3aed' },
  { nombre: 'Grafito', color: '#334155' },
];

function leer(clave: string, inicial: string) {
  try {
    return localStorage.getItem(clave) ?? inicial;
  } catch {
    return inicial;
  }
}

function guardar(clave: string, valor: string) {
  try {
    localStorage.setItem(clave, valor);
  } catch {
    /* sin almacenamiento: solo esta sesión */
  }
}

/** Texto blanco u oscuro según la luminancia del color, para que siempre se lea. */
export function textoSobre(hex: string): string {
  const [r, g, b] = [1, 3, 5].map((i) => {
    const c = parseInt(hex.slice(i, i + 2), 16) / 255;
    return c <= 0.03928 ? c / 12.92 : ((c + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b > 0.4 ? '#0b1412' : '#ffffff';
}

export const temaGuardado = () => leer('tema', 'sistema') as Tema;
export const colorGuardado = () => leer('color', COLOR_PREDETERMINADO);

function aplicar(tema: Tema, color: string) {
  const raiz = document.documentElement;
  if (tema === 'sistema') delete raiz.dataset.tema;
  else raiz.dataset.tema = tema;
  raiz.style.setProperty('--primario', color);
  raiz.style.setProperty('--primario-texto', textoSobre(color));
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content', color);
}

/** Cambia tema y color con una transición suave si el navegador la soporta. */
export function cambiarTema(tema: Tema, color: string) {
  guardar('tema', tema);
  guardar('color', color);
  const doc = document as Document & { startViewTransition?: (cb: () => void) => unknown };
  const reducir = matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (doc.startViewTransition && !reducir) doc.startViewTransition(() => aplicar(tema, color));
  else aplicar(tema, color);
}
