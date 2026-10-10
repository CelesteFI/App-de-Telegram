/* juegos/completar.js — Toca la pieza y salta al hueco del pergamino. */

import { escLatex, mateToken, pintarMatematica } from '../dom.js';

export default {
  id: 'completar',

  crear({ ronda }) {
    let elegido = -1;

    function pintar() {
      const zona = document.querySelector('.completar');
      if (!zona) return;
      const base = String(ronda.enunciado || '');
      const relleno = elegido >= 0 ? mateToken(ronda.opciones[elegido]) : '… ? …';
      const clase = elegido >= 0 ? 'completar__hueco completar__hueco--lleno' : 'completar__hueco';
      const conHueco = base.includes('[')
        ? escLatex(base).replace(/\[.*?\]/, `<span class="${clase}">🧩 ${relleno}</span>`)
        : `${escLatex(base)} <span class="${clase}">🧩 ${relleno}</span>`;
      zona.querySelector('.completar__enunciado').innerHTML = `📜 ${conHueco}`;
      zona.querySelectorAll('.completar__opcion').forEach((b) => {
        const on = Number(b.dataset.indice) === elegido;
        b.classList.toggle('completar__opcion--elegida', on);
      });
      pintarMatematica(zona);
    }

    return {
      auto: false,

      html() {
        const opciones = ronda.opciones
          .map((texto, i) => `
            <button class="completar__opcion" type="button" data-indice="${i}">
              🧪 ${mateToken(texto)}
            </button>`)
          .join('');
        return `
          <div class="completar">
            <p class="completar__enunciado"></p>
            <div class="completar__opciones">${opciones}</div>
            <p class="tarjeta__nota">👆 Toca la pieza correcta: saltará al hueco del pergamino.</p>
          </div>`;
      },

      montar() {
        pintar();
        pintarMatematica(document.querySelector('.completar'));
        document.querySelector('.completar').addEventListener('click', (evento) => {
          const boton = evento.target.closest('.completar__opcion');
          if (!boton) return;
          elegido = Number(boton.dataset.indice);
          boton.animate?.(
            [{ transform: 'translateY(0) scale(1)' }, { transform: 'translateY(-14px) scale(1.12)' }, { transform: 'translateY(0) scale(1)' }],
            { duration: 320 });
          pintar();
        });
      },

      envio() {
        return elegido;
      },
    };
  },
};
