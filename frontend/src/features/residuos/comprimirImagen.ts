/**
 * Achica la foto antes de subirla (datos móviles caros, señal débil) y, al redibujarla,
 * descarta los metadatos EXIF del celular.
 */
export async function comprimirImagen(archivo: File, maxLado = 1280, calidad = 0.7): Promise<Blob> {
  const bmp = await createImageBitmap(archivo, { imageOrientation: 'from-image' });
  const escala = Math.min(1, maxLado / Math.max(bmp.width, bmp.height));
  const canvas = document.createElement('canvas');
  canvas.width = Math.round(bmp.width * escala);
  canvas.height = Math.round(bmp.height * escala);
  canvas.getContext('2d')!.drawImage(bmp, 0, 0, canvas.width, canvas.height);
  bmp.close();
  return new Promise((ok, mal) =>
    canvas.toBlob((b) => (b ? ok(b) : mal(new Error('No se pudo procesar la foto.'))), 'image/jpeg', calidad),
  );
}
