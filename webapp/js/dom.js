/* dom.js — Ayudas para tocar el DOM y pintar la matematica con KaTeX. */

export function el(etiqueta, atributos = {}, hijos = []) {
  const nodo = document.createElement(etiqueta);
  for (const [clave, valor] of Object.entries(atributos)) {
    if (valor === null || valor === undefined || valor === false) continue;
    if (clave === 'class') nodo.className = valor;
    else if (clave === 'html') nodo.innerHTML = valor;
    else if (clave === 'texto') nodo.textContent = valor;
    else if (clave.startsWith('on') && typeof valor === 'function') {
      nodo.addEventListener(clave.slice(2).toLowerCase(), valor);
    } else nodo.setAttribute(clave, valor === true ? '' : valor);
  }
  for (const hijo of [].concat(hijos)) {
    if (hijo === null || hijo === undefined || hijo === false) continue;
    nodo.append(hijo.nodeType ? hijo : document.createTextNode(String(hijo)));
  }
  return nodo;
}

export function esc(texto) {
  return String(texto ?? '')
    .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

export function escLatex(texto) {
  // Protege \& \% \$ \# \_ \{ \} para que KaTeX no los confunda con
  // sintaxis: se emite la entidad del backslash SIN punto y coma extra
  // (antes se colaba un ";" visible en el texto renderizado).
  return esc(texto).replace(/\\([&%$#_{}])/g, '&#92;$1');
}

// Ecuacion pura (viene del servidor en LaTeX crudo, SIN $...$):
// se envuelve en $...$ para que KaTeX si la pinte. Si ya trae sus
// delimitadores, se respeta tal cual.
export function mateEcuacion(texto) {
  const t = String(texto ?? '');
  if (!t) return '';
  if (t.includes('$')) return escLatex(t);
  return `$${escLatex(t)}$`;
}

// Token corto de "completa la forma" (ej: e^{x}, \infty, P(x), n):
// solo se envuelve si trae comandos LaTeX; las palabras sueltas
// ("Lipschitz", "separacion de variables") van en texto normal,
// porque en modo mate se pegarian sin espacios.
export function mateToken(texto) {
  const t = String(texto ?? '');
  if (!t) return '';
  if (t.includes('$')) return escLatex(t);
  if (/[\\^_]/.test(t)) return `$${escLatex(t)}$`;
  return esc(t);
}

let renderizados = 0;

export function pintarMatematica(raiz = document.body, intento = 0) {
  // auto-render (CDN con defer) puede llegar despues que el modulo:
  // se reintenta solo hasta ~3 s en vez de rendirse al primer intento,
  // que dejaba las formulas crudas ($...$) para siempre.
  if (!window.renderMathInElement) {
    if (intento < 12 && document.contains(raiz)) {
      setTimeout(() => pintarMatematica(raiz, intento + 1), 250);
    }
    return;
  }
  try {
    window.renderMathInElement(raiz, {
      delimiters: [
        { left: '$$', right: '$$', display: true },
        { left: '\\[', right: '\\]', display: true },
        { left: '$', right: '$', display: false },
        { left: '\\(', right: '\\)', display: false },
      ],
      throwOnError: false,
      trust: true,
    });
    renderizados += 1;
  } catch {
    if (intento < 5 && document.contains(raiz)) {
      setTimeout(() => pintarMatematica(raiz, intento + 1), 400);
    }
  }
}

export function avisarMarco() {
  window.dispatchEvent(new window.Event('marca:cambio'));
}

export function alPintar(raiz, accion) {
  requestAnimationFrame(() => {
    pintarMatematica(raiz);
    accion?.();
  });
}

export function vaciar(nodo) {
  while (nodo.firstChild) nodo.removeChild(nodo.firstChild);
  return nodo;
}

export function letras(indice) {
  return 'ABCDEFGHIJ'.split('')[indice] || String(indice + 1);
}

export function plural(n, singular, muchos) {
  return `${n} ${n === 1 ? singular : muchos}`;
}

export function pct(valor) {
  return `${Math.round((Number(valor) || 0) * 10) / 10}%`;
}

export function segundos(valor) {
  const n = Math.max(0, Math.round(Number(valor) || 0));
  if (n < 60) return `${n} s`;
  return `${Math.floor(n / 60)} min ${n % 60} s`;
}