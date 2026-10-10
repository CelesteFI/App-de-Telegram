/* juegos/globos.js — Caza en el cielo: revienta solo las soluciones. */

import { escLatex, mateEcuacion, pintarMatematica } from '../dom.js';

export default {
  id: 'globos',

  crear({ ronda, responder, temporizador }) {
    const explotados = new Set();
    let segundos = ronda.segundos || 12;
    const posiciones = ronda.globos.map((_, i) => ({
      izquierda: 3 + (i % 4) * 24,
      retraso: i * 0.7,
      duracion: 7 + (i % 4),
    }));
    const reloj = { nodo: null };

    function html() {
      const globos = ronda.globos.map((globo, i) => `
        <button class="globo ${explotados.has(globo.id) ? 'globo--explotado' : ''}"
                type="button" data-id="${globo.id}"
                style="left:${posiciones[i].izquierda}%;
                       animation-duration:${posiciones[i].duracion}s;
                       animation-delay:-${posiciones[i].retraso}s;"
                 aria-label="globo ${i + 1}">🎈 ${mateEcuacion(globo.tex)}</button>`).join('');
      return `
        <div class="globos">
          <p class="globos__instruccion">🎯 ${escLatex(ronda.instruccion)}</p>
          <p class="tarjeta__nota">💥 Reventados: <b>${explotados.size}</b> · Quedan <span class="pildora" id="globos-reloj">${segundos} s</span> · ¡No toques los falsos!</p>
          <div class="globos__cielo">${globos}</div>
        </div>`;
    }

    function pintar() {
      const zona = document.getElementById('globos-zona');
      if (!zona) return;
      zona.innerHTML = html();
      reloj.nodo = document.getElementById('globos-reloj');
      pintarMatematica(zona);
    }

    function terminar() {
      responder({ ids: [...explotados] });
    }

    return {
      auto: true,

      html() {
        return `<div id="globos-zona">${html()}</div>`;
      },

      montar() {
        pintar();
        const zona = document.getElementById('globos-zona');
        zona.addEventListener('click', (evento) => {
          const globo = evento.target.closest('.globo');
          if (!globo || explotados.has(globo.dataset.id)) return;
          explotados.add(globo.dataset.id);
          globo.classList.add('globo--explotado');
          globo.animate?.(
            [{ transform: 'scale(1)' }, { transform: 'scale(1.4)' }, { transform: 'scale(0)' }],
            { duration: 300 });
          // chispas
          for (let k = 0; k < 6; k += 1) {
            const chispa = document.createElement('span');
            chispa.textContent = ['✨', '💥', '⭐'][k % 3];
            Object.assign(chispa.style, {
              position: 'absolute',
              left: `${globo.offsetLeft + 30}px`,
              top: `${globo.offsetTop}px`,
              fontSize: '18px',
              pointerEvents: 'none',
              zIndex: 50,
            });
            zona.appendChild(chispa);
            chispa.animate?.(
              [{ transform: 'translate(0,0) scale(1)', opacity: 1 },
               { transform: `translate(${(k - 2.5) * 26}px,-60px) scale(.4)`, opacity: 0 }],
              { duration: 600 });
            setTimeout(() => chispa.remove(), 650);
          }
          setTimeout(() => {
            globo.remove();
            const nota = zona.querySelector('.tarjeta__nota');
            if (nota) nota.innerHTML = `💥 Reventados: <b>${explotados.size}</b> · Quedan <span class="pildora" id="globos-reloj">${segundos} s</span> · ¡No toques los falsos!`;
            reloj.nodo = document.getElementById('globos-reloj');
          }, 300);
        });

        temporizador(() => {
          segundos = Math.max(0, segundos - 1);
          const relojFresco = document.getElementById('globos-reloj');
          if (relojFresco) relojFresco.textContent = `${segundos} s`;
          if (segundos === 0) terminar();
        }, 1000);
      },

      envio() {
        return { ids: [...explotados] };
      },
    };
  },
};
