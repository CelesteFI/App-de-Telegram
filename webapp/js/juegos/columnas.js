/* juegos/columnas.js — Une columnas con cables animados de colores. */

import { escLatex, mateEcuacion, pintarMatematica } from '../dom.js';

const COLORES = ['#0284c7', '#db2777', '#16a34a', '#d97706', '#7c3aed', '#059669'];

export default {
  id: 'columnas',

  crear({ ronda }) {
    const emparejado = new Array(ronda.izquierda.length).fill(null);
    let izquierdaActiva = -1;
    const usadas = new Set();

    function pintar() {
      const caja = document.getElementById('columnas');
      if (!caja) return;
      const pendientes = emparejado.filter((v) => v === null).length;
      caja.innerHTML = `
        <div class="columnas" id="columnas-mapa">
          <svg id="columnas-svg" aria-hidden="true"></svg>
          <div class="columnas__lista columnas__lista--izq">
            <p class="tarjeta__nota">🧮 <b>Ecuaciones</b>: toca una</p>
            ${ronda.izquierda.map((texto, i) => `
              <button class="opcion columnas__item ${izquierdaActiva === i ? 'columnas__item--activo' : ''} ${emparejado[i] !== null ? 'columnas__hecho' : ''}"
                      type="button" data-lado="i" data-indice="${i}">
                <span class="opcion__letra">${i + 1}</span>
                <span class="columnas__tex">${mateEcuacion(texto)}</span>
                <span class="columnas__nodo" aria-hidden="true">${emparejado[i] !== null ? '🔗' : '○'}</span>
              </button>`).join('')}
          </div>
          <div class="columnas__gutter" aria-hidden="true">${ronda.izquierda.map((_, i) => `<span style="--c:${COLORES[i % COLORES.length]}">${emparejado[i] !== null ? '🔗' : '⋮'}</span>`).join('')}</div>
          <div class="columnas__lista columnas__lista--der">
            <p class="tarjeta__nota">🧪 <b>Métodos</b>: toca su pareja</p>
            ${ronda.derecha.map((texto, i) => `
              <button class="opcion columnas__item ${usadas.has(i) ? 'columnas__hecho' : ''}"
                      type="button" data-lado="d" data-indice="${i}">
                <span class="columnas__nodo" aria-hidden="true">○</span>
                <span class="opcion__letra">${String.fromCharCode(65 + i)}</span>
                <span class="columnas__tex">${escLatex(texto)}</span>
              </button>`).join('')}
          </div>
        </div>
        <p class="tarjeta__nota" id="columnas-estado">${pendientes ? `🔌 Faltan ${pendientes} conexiones…` : '✅ ¡Todo conectado! Pulsa Comprobar.'}</p>`;
      pintarMatematica(caja);
      requestAnimationFrame(dibujarCables);
    }

    function dibujarCables() {
      const svg = document.getElementById('columnas-svg');
      const mapa = document.getElementById('columnas-mapa');
      if (!svg || !mapa) return;
      const m = mapa.getBoundingClientRect();
      if (!m.width) return;
      svg.setAttribute('viewBox', `0 0 ${m.width} ${m.height}`);
      let html = '';
      emparejado.forEach((der, izq) => {
        if (der === null || der < 0) return;
        const a = mapa.querySelector(`button[data-lado="i"][data-indice="${izq}"] .columnas__nodo`);
        const b = mapa.querySelector(`button[data-lado="d"][data-indice="${der}"] .columnas__nodo`);
        if (!a || !b) return;
        const ra = a.getBoundingClientRect();
        const rb = b.getBoundingClientRect();
        const x1 = ra.left + ra.width / 2 - m.left;
        const y1 = ra.top + ra.height / 2 - m.top;
        const x2 = rb.left + rb.width / 2 - m.left;
        const y2 = rb.top + rb.height / 2 - m.top;
        const mx = (x1 + x2) / 2;
        const color = COLORES[izq % COLORES.length];
        html += `<path d="M ${x1} ${y1} C ${mx} ${y1}, ${mx} ${y2}, ${x2} ${y2}" fill="none" stroke="${color}" stroke-width="5" stroke-linecap="round"/>`;
        html += `<circle cx="${x1}" cy="${y1}" r="8" fill="${color}" stroke="#fff" stroke-width="2.5"/><circle cx="${x2}" cy="${y2}" r="8" fill="${color}" stroke="#fff" stroke-width="2.5"/>`;
      });
      svg.innerHTML = html;
    }

    return {
      auto: false,

      html() {
        return '<div id="columnas"></div>';
      },

      montar() {
        pintar();
        const caja = document.getElementById('columnas');
        window.addEventListener('resize', dibujarCables);
        caja.addEventListener('click', (evento) => {
          const boton = evento.target.closest('button[data-lado]');
          if (!boton) return;
          const indice = Number(boton.dataset.indice);
          if (boton.dataset.lado === 'i') {
            izquierdaActiva = izquierdaActiva === indice ? -1 : indice;
            pintar();
            return;
          }
          if (izquierdaActiva < 0) {
            const est = document.getElementById('columnas-estado');
            if (est) {
              est.textContent = '👈 Primero toca una ecuación de la izquierda.';
              est.animate?.([{ transform: 'translateX(0)' }, { transform: 'translateX(-6px)' }, { transform: 'translateX(6px)' }, { transform: 'translateX(0)' }], { duration: 250 });
            }
            return;
          }
          for (let k = 0; k < emparejado.length; k += 1) {
            if (emparejado[k] === indice) emparejado[k] = null;
          }
          emparejado[izquierdaActiva] = indice;
          usadas.add(indice);
          boton.animate?.([{ transform: 'scale(1)' }, { transform: 'scale(1.08)' }, { transform: 'scale(1)' }], { duration: 280 });
          izquierdaActiva = -1;
          pintar();
        });
      },

      envio() {
        return emparejado.map((v) => (v === null ? -1 : v));
      },
    };
  },
};
