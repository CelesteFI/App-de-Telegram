/* juegos/memoria.js — Memorama fiesta con volteo 3D y confeti. */

import { api } from '../api.js';
import { aviso } from '../avisos.js';
import { esc, mateEcuacion, pintarMatematica } from '../dom.js';

// Un solo reverso para todas las cartas: si cada una tuviera un emoji
// distinto, se podrian reconocer por el dibujo sin memorizar el contenido.
const TAPA = '🌟';

export default {
  id: 'memoria',

  crear({ ronda, indice, intento, responder }) {
    const reveladas = new Set();
    const emparejadas = new Set();
    let completas = 0;
    let errores = 0;
    let pendiente = null;
    let bloqueado = false;

    function pintar() {
      const caja = document.getElementById('memoria');
      if (!caja) return;
      const texto = completas >= ronda.pares
        ? '🎉 ¡Tablero completo!'
        : `💫 ${completas} de ${ronda.pares} parejas` + (errores ? ` · 💥 ${errores} fallo(s)` : '');
      caja.innerHTML = `
        <div class="memoria">
          <p class="memoria__progreso">🃏 Encuentra cada concepto con su fórmula · ${texto}</p>
          <div class="memoria__tablero">
            ${ronda.cartas.map((carta, i) => {
    const clases = ['memoria__carta'];
    if (reveladas.has(carta.id)) clases.push('memoria__carta--vista');
    if (emparejadas.has(carta.id)) clases.push('memoria__carta--hecha');
    return `
                <button class="${clases.join(' ')}" type="button" data-id="${carta.id}"
                        ${emparejadas.has(carta.id) ? 'disabled' : ''} aria-label="carta ${i + 1}">
                  <span class="memoria__cara memoria__cara--tapa">${TAPA}</span>
                  <span class="memoria__cara memoria__cara--texto">${carta.cara === 'mate' ? mateEcuacion(carta.texto) : esc(carta.texto)}</span>
                </button>`;
  }).join('')}
          </div>
        </div>`;
      pintarMatematica(caja);
    }

    function fiesta() {
      const capa = document.createElement('div');
      capa.className = 'fiesta';
      const colores = ['#ea580c', '#db2777', '#7c3aed', '#16a34a', '#0284c7', '#facc15'];
      for (let i = 0; i < 36; i += 1) {
        const p = document.createElement('i');
        p.style.left = `${Math.random() * 100}%`;
        p.style.background = colores[i % colores.length];
        p.style.animationDelay = `${Math.random() * 0.4}s`;
        capa.appendChild(p);
      }
      document.body.appendChild(capa);
      setTimeout(() => capa.remove(), 1900);
    }

    async function sonPareja(idA, idB) {
      try {
        const datos = await api.post('/api/minijuegos/pareja', {
          intento, ronda: indice, a: idA, b: idB,
        });
        return Boolean(datos.pareja);
      } catch (error) {
        aviso(error.message, true);
        return false;
      }
    }

    async function voltear(carta) {
      const id = carta.dataset.id;
      if (bloqueado || emparejadas.has(id) || reveladas.has(id)) return;

      if (!pendiente) {
        pendiente = id;
        reveladas.add(id);
        pintar();
        return;
      }

      bloqueado = true;
      const antes = pendiente;
      pendiente = null;
      reveladas.add(id);
      pintar();

      if (await sonPareja(antes, id)) {
        emparejadas.add(antes);
        emparejadas.add(id);
        completas += 1;
        pintar();
        fiesta();
        bloqueado = false;
        if (completas >= ronda.pares) responder({ completas, errores });
        return;
      }

      errores += 1;
      pintar();
      setTimeout(() => {
        reveladas.delete(antes);
        reveladas.delete(id);
        bloqueado = false;
        pintar();
      }, 1100);
    }

    return {
      auto: true,

      html() {
        return '<div id="memoria"></div>';
      },

      montar() {
        pintar();
        document.getElementById('memoria').addEventListener('click', (evento) => {
          const carta = evento.target.closest('.memoria__carta');
          if (carta) voltear(carta);
        });
      },

      envio() {
        return { completas, errores };
      },
    };
  },
};
