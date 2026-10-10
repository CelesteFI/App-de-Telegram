/* tema.js — Configuracion del quiz de un tema y arranque del intento. */

import { api } from '../api.js';
import { aviso } from '../avisos.js';
import { el } from '../dom.js';
import { estado, tema as buscarTema } from '../estado.js';
import * as nav from '../navegacion.js';

const LETRAS = (n) => Array.from({ length: n }, (_, i) => (n > 4 ? String(i + 1) : 'ABCDEFG'[i]));

function grupoOpciones(nombre, valores, actual, alCambiar, etiquetas = null) {
  const caja = el('div', { class: 'fila' });
  valores.forEach((valor, indice) => {
    const texto = etiquetas ? etiquetas[indice] : LETRAS(valores.length)(indice);
    const boton = el('button', {
      class: `boton ${actual === valor ? '' : 'boton--plano'}`,
      type: 'button',
      texto: texto,
      onclick: () => alCambiar(valor),
    });
    caja.append(boton);
  });
  caja.dataset.opciones = nombre;
  return caja;
}

export function vistaTema(materiaId, temaId) {
  const encontrado = buscarTema(materiaId, temaId);
  const datos = {
    n: 5,
    orden: 'mezclado',
    modo: 'normal',
  };

  return {
    titulo: () => encontrado?.tema.nombre || 'Tema',
    sub: () => encontrado ? encontrado.materia.nombre : '',
    pie: () => 'Puedes repetir el mismo tema las veces que quieras.',

    async entrar(raiz) {
      if (!encontrado) {
        raiz.append(el('div', { class: 'vacio', texto: 'Ese tema no existe.' }));
        return null;
      }
      const { materia, tema } = encontrado;

      raiz.append(
        el('div', { class: 'tarjeta' }, [
          el('span', { class: 'tarjeta__titulo', texto: tema.nombre }),
          el('span', { class: 'tarjeta__nota', texto: tema.resumen || '' }),
        ]),
        el('h2', { class: 'seccion', texto: 'Cuantas preguntas' }),
      );

      const cantidades = estado.config?.cantidades || [5, 10, 15, 0];
      const pintadoCantidad = { nodo: null };
      const pintadoOrden = { nodo: null };
      const pintadoModo = { nodo: null };

      function refrescar(nombre) {
        const destino = nombre === 'n' ? pintadoCantidad
          : nombre === 'orden' ? pintadoOrden : pintadoModo;
        const nuevo = nombre === 'n'
          ? grupoOpciones('n', cantidades, datos.n, (v) => { datos.n = v; refrescar('n'); },
              cantidades.map((c) => (c === 0 ? 'Todas' : String(c))))
          : nombre === 'orden'
            ? grupoOpciones('orden', ['mezclado', 'original'], datos.orden,
                (v) => { datos.orden = v; refrescar('orden'); }, ['Al azar', 'En orden'])
            : grupoOpciones('modo', ['normal', 'falladas', 'pendientes'], datos.modo,
                (v) => { datos.modo = v; refrescar('modo'); },
                ['Repaso', 'Falladas', 'Pendientes']);
        if (destino.nodo) destino.nodo.replaceWith(nuevo);
        else raiz.append(nuevo);
        destino.nodo = nuevo;
      }

      refrescar('n');
      raiz.append(el('h2', { class: 'seccion', texto: 'Como seleccionar' }));
      refrescar('orden');
      raiz.append(el('h2', { class: 'seccion', texto: 'Que repasar' }));
      refrescar('modo');

      const empezar = el('button', {
        class: 'boton boton--ancho',
        type: 'button',
        texto: 'Empezar',
        onclick: async () => {
          empezar.disabled = true;
          empezar.textContent = 'Preparando…';
          try {
            estado.quiz = await api.post('/api/quiz/iniciar', {
              materia: materia.id,
              tema: tema.id,
              n: datos.n,
              orden: datos.orden,
              modo: datos.modo,
            });
            nav.ir('quiz');
          } catch (error) {
            aviso(error.message, true);
            empezar.disabled = false;
            empezar.textContent = 'Empezar';
          }
        },
      });

      raiz.append(el('div', { class: 'seccion' }), empezar);

      if (tema.total < 5) {
        raiz.append(el('p', { class: 'tarjeta__nota',
          texto: `Este tema solo tiene ${tema.total} preguntas.` }));
      }
      return null;
    },
  };
}