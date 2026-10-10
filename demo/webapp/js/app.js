// app.js — Mini App de Examenes estilo Kahoot (2 areas: Teoria y Quizzes)
(function () {
  const LETRAS = 'ABCDEFGHIJ';
  const $id = (i) => document.getElementById(i);

  const S = {
    vista: 'inicio',
    code: null,          // codigo de la sesion
    examen: null,        // id del examen elegido (profesor)
    pinReq: false,
    sesion: null,        // ultima respuesta de /api/estado o /profesor/estado
    resp: {},            // respuestas propias: q -> opcion
    reporte: null,
  };

  let loopTok = 0;       // token de los bucles de polling (cambia al navegar)

  // ---------- utilidades ------------------------------------------------
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, (c) => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
    }[c]));
  }
  function msg(m) {
    try { if (App.tg && App.tg.showAlert) { App.tg.showAlert(m); return; } } catch (_) {}
    window.alert(m);
  }
  function haptic(tipo) {
    try { App.tg.HapticFeedback[tipo] && App.tg.HapticFeedback[tipo](); } catch (_) {}
  }
  function renderMath(el, raw) {
    el.innerHTML = '';
    const s = String(raw || '');
    if (!s.trim()) return;
    const limpio = s.replace(/^\$+|\$+$/g, '');
    if (/[\\$]/.test(s) && window.katex) {
      try { window.katex.render(limpio, el, { throwOnError: false }); }
      catch (_) { el.textContent = s; }
    } else { el.textContent = s; }
  }
  function mathDiv(raw) { return '<span class="formula" data-math="' + esc(raw) + '"></span>'; }
  function mountMath(scope) {
    (scope || document).querySelectorAll('[data-math]').forEach((el) => renderMath(el, el.dataset.math));
  }
  function stopPoll() { loopTok++; }

  // ---------- navegacion ------------------------------------------------
  function goto(vista) {
    stopPoll();
    S.vista = vista;
    render();
  }
  window.goto = goto;

  function volver() {
    const v = S.vista;
    if (v === 'teoria-tema') return goto('teoria');
    if (v === 'teoria') return goto('inicio');
    if (v === 'quizzes') return goto('inicio');
    if (v === 'practica') return goto('practica-temas');
    if (v === 'practica-temas') return goto('quizzes');
    if (v === 'alumno-unirse') return goto('quizzes');
    if (v === 'alumno-sala') return goto('alumno-unirse');
    if (S.rol === 'profe') return goto('profe-config');
    goto('inicio');
  }
  window.volver = volver;

  function render() {
    if (!App.tg && !App.dev) {
      document.getElementById('app').innerHTML =
        '<main><div class="card"><h2>Abre la Mini App desde Telegram</h2>' +
        '<p>Esta app funciona dentro de la app de Telegram. <a href="?dev=1">Probar en modo dev</a></p></div></main>';
      return;
    }
    AppRoot();
    switch (S.vista) {
      case 'teoria': return vTeoria();
      case 'teoria-tema': return vTeoriaTema();
      case 'quizzes': return vQuizzes();
      case 'practica-temas': return vPracticaTemas();
      case 'practica': return vPractica();
      case 'alumno-unirse': return vAlumnoUnirse();
      case 'alumno-sala': return vAlumnoSala();
      case 'profe-config': return vProfeConfig();
      case 'profe-sala': return vProfeSala();
      case 'profe-reporte': return vProfeReporte();
      default: return vInicio();
    }
  }
  function AppRoot() { return $id('app'); }
  function shellHtml(titulo, conBack) {
    return '<header class="top">' +
      (conBack ? '<button class="back" onclick="volver()">←</button>' : '') +
      '<div class="logo">' + esc(titulo) + '</div></header><main id="wrap"></main>';
  }
  function renderShell(titulo, conBack) {
    AppRoot().innerHTML = shellHtml(titulo, conBack);
    return $id('wrap');
  }

  // ---------- inicio -----------------------------------------------------
  function vInicio() {
    const wrap = renderShell('Analisis Numerico UNAM', false);
    wrap.innerHTML =
      '<div class="hero"><h1>📚 Repaso interactivo</h1>' +
      '<p>Elije un area para empezar</p></div><div class="grid2">' +
      '<a class="menu-card" data-go="teoria"><span class="ico">📖</span>' +
      '<span><div class="tt">Area de Teoria</div>' +
      '<div class="ds">Apuntes y formulas de los temas del curso</div></span></a>' +
      '<a class="menu-card" data-go="quizzes">' +
      '<span class="ico">📝</span><span><div class="tt">Area de Quizzes</div>' +
      '<div class="ds">Examenes en vivo tipo Kahoot</div></span></a></div>';
    wrap.querySelectorAll('[data-go]').forEach((el) => el.addEventListener('click', () => goto(el.dataset.go)));
  }

  // ---------- teoria -----------------------------------------------------
  const TOPICOS = Object.keys(window.TEORIA || {});
  function vTeoria() {
    const wrap = renderShell('Area de Teoria', true);
    wrap.innerHTML = TOPICOS.map((id) => {
      const t = window.TEORIA[id];
      return '<a class="menu-card" data-tema="' + id + '"><span class="ico">' + t.icono + '</span>' +
        '<span><div class="tt">' + esc(t.titulo) + '</div><div class="ds">' + esc(t.resumen) + '</div></span></a>';
    }).join('') + '<p class="muted center">Mas temas pronto...</p>';
    wrap.querySelectorAll('[data-tema]').forEach((el) =>
      el.addEventListener('click', () => { S.tema = el.dataset.tema; goto('teoria-tema'); }));
  }
  function vTeoriaTema() {
    const t = window.TEORIA[S.tema];
    const wrap = renderShell(t.titulo, true);
    const bloques = (t.bloques || []).map((b) => {
      if (b.tipo === 'f') return mathDiv(b.tex);
      if (b.tipo === 'li') return '<ul style="margin:6px 0"><li>' + b.items.map(esc).join('</li><li>') + '</li></ul>';
      return '<p>' + tBlocoP(b.texto) + '</p>';
    }).join('');
    wrap.innerHTML = '<div class="card">' + bloques + '</div><button class=\"btn secondary\" onclick=\"volver()\">Volver a temas</button>';
    mountMath(wrap);
  }
  function tBlocoP(texto) {
    // texto puede llevar $...$ : lo separamos en fragmentos
    const partes = String(texto).split(/(\$[^$]+\$)/g);
    return partes.map((px) => /^\$[^$]+\$$/.test(px)
      ? '<span class="formula" data-math="' + esc(px.replace(/^\$+|\$+$/g, '')) + '"></span>'
      : esc(px)).join('');
  }

  // ---------- quizzes ----------------------------------------------------
function vQuizzes() {
    const wrap = renderShell('Area de Quizzes', true);
    wrap.innerHTML =
      '<p class="center muted">Puedes practicar solo o entrar a un examen en vivo.</p>' +
      '<a class="menu-card" data-go="practica-temas"><span class="ico">🎯</span>' +
      '<span><div class="tt">Practicar individual</div>' +
      '<div class="ds">Elige un tema y responde a tu ritmo, con retroalimentacion</div></span></a>' +
      '<hr style="border:none;border-top:1px solid var(--tg-theme-hint-color, #ddd);margin:6px 0 12px">' +
      '<a class="menu-card" data-go="profe-config"><span class="ico">👩‍🏫</span>' +
      '<span><div class="tt">Soy profesor(a)</div><div class="ds">Crear examen en vivo y ver resultados</div></span></a>' +
      '<a class="menu-card" data-go="alumno-unirse"><span class="ico">🎓</span>' +
      '<span><div class="tt">Soy alumno</div><div class="ds">Entro con el codigo del examen en vivo</div></span></a>';
    wrap.querySelectorAll('[data-go]').forEach((el) => el.addEventListener('click', () => goto(el.dataset.go)));
  }

  // ---------- practica individual ----------------------------------------
  function tituloTema(tema) {
    return (typeof TEORIA !== 'undefined' && TEORIA[tema] && TEORIA[tema].titulo) || tema;
  }
  function agruparQuizzes(exs, renderExamen) {
    const grupos = {};
    exs.forEach((e) => (grupos[e.tema] = grupos[e.tema] || []).push(e));
    return Object.keys(grupos).sort().map((tema) =>
      '<h3 class="tema-titulo">📌 ' + esc(tituloTema(tema)) + '</h3>' +
      grupos[tema].map(renderExamen).join('')).join('');
  }
  function vPracticaTemas() {
    const wrap = renderShell('Practicar individual', true);
    wrap.innerHTML = '<div class="card center"><span class="spin">⏳</span> Cargando quizzes...</div>';
    api.get('/api/examenes').then((j) => {
      if (!j.ok) { wrap.innerHTML = '<p class="mal">' + esc(j.error || 'error') + '</p>'; return; }
      const body = agruparQuizzes(j.examenes || [], (e) => {
        const mejor = window.localStorage ? window.localStorage.getItem('pbest_' + e.id) : null;
        return '<button class="opt" onclick="practicar(\'' + e.id + '\')">' +
          '<span style="flex:1"><b>' + esc(e.titulo) + '</b><br><span class="muted">' +
          esc(e.descripcion) + ' · ' + e.total + ' preguntas</span></span>' +
          (mejor ? '<span class="pill ok">mejor ' + esc(mejor) + '</span>' : '') + '</button>';
      });
      wrap.innerHTML = body
        ? '<div class="card">' + body + '</div>'
        : '<p class="muted center">Aun no hay quizzes disponibles.</p>';
    });
  }
  window.practicar = function (id) {
    S.practica = { id: id, idx: 0, resp: {}, fin: false, examen: null };
    goto('practica');
    api.get('/api/practica/' + id).then((j) => {
      if (j.ok && j.examen) {
        S.practica.examen = j.examen;
        vPractica();
      } else {
        pintarPracticaError(j.error || 'No se pudo cargar el quiz.');
      }
    });
  };
  function pintarPracticaError(err) {
    const z = $id('zonaPractica');
    if (z) z.innerHTML = '<div class="card center"><p class="mal">' + esc(err) + '</p>' +
      '<button class="btn" onclick="volver()">Volver a temas</button></div>';
  }
  function vPractica() {
    const wrap = renderShell('Practica individual', true);
    if (!S.practica || !S.practica.examen) {
      wrap.innerHTML = '<div class="card center"><span class="spin">⏳</span> Cargando quiz...</div>';
      return;
    }
    wrap.innerHTML = '<div id="zonaPractica"></div>';
    pintarPractica();
  }
  function pintarPractica() {
    const P = S.practica;
    const zona = $id('zonaPractica');
    if (!zona) return;
    if (P.fin) { zona.innerHTML = practicaFinalHtml(P); mountMath(zona); return; }
    const q = P.examen.preguntas[P.idx];
    const respondida = (P.resp[P.idx] != null);
    const elegida = P.resp[P.idx];
    const opts = q.opciones.map((o, i) => {
      let extra = 'onclick="practicaElegir(' + i + ')"';
      let cls = '';
      if (respondida) {
        extra = '';
        cls = i === q.correcta ? ' correct' : (i === elegida ? ' wrong' : '');
      }
      return '<button class="opt' + cls + '" ' + extra + '>' +
        '<span class="letra l' + i + '">' + LETRAS[i] + '</span>' +
        '<span data-math="' + esc(o) + '"></span>' +
        (respondida && i === q.correcta ? ' <span class="tag">correcta</span>' : '') +
        (respondida && i === elegida && i !== q.correcta ? ' <span class="tag">tu respuesta</span>' : '') + '</button>';
    }).join('');
    const esUltima = P.idx >= P.examen.preguntas.length - 1;
    zona.innerHTML =
      '<div class="card"><div class="q-count">Pregunta <b>' + (P.idx + 1) + '</b> de ' + P.examen.preguntas.length + '</div>' +
      '<h2 data-math="' + esc(q.p) + '"></h2>' + (q.f ? mathDiv(q.f) : '') + '</div>' +
      '<div class="opts">' + opts + '</div>' +
      (respondida
        ? '<button class="btn" onclick="practicaSiguiente()">' + (esUltima ? '🏁 Ver mi resultado' : 'Siguiente →') + '</button>'
        : '<p class="muted center">Toca una respuesta para ver si acertaste.</p>');
    mountMath(zona);
  }
  window.practicaElegir = function (i) {
    const P = S.practica;
    if (!P || P.fin) return;
    if (P.resp[P.idx] != null) return;
    P.resp[P.idx] = i;
    haptic(i === P.examen.preguntas[P.idx].correcta ? 'success' : 'notificationOccurred');
    pintarPractica();
  };
  window.practicaSiguiente = function () {
    const P = S.practica;
    if (P.idx + 1 >= P.examen.preguntas.length) {
      P.fin = true;
      if (window.localStorage) {
        const n = P.examen.preguntas.length;
        const ack = Object.keys(P.resp).reduce((a, k) => a + (P.resp[k] === P.examen.preguntas[+k].correcta ? 1 : 0), 0);
        localStorage.setItem('pbest_' + P.examen.id, ack + '/' + n);
      }
    } else {
      P.idx++;
    }
    pintarPractica();
  };
  window.practicaRepetir = function () {
    S.practica.idx = 0;
    S.practica.resp = {};
    S.practica.fin = false;
    pintarPractica();
  };
  function practicaFinalHtml(P) {
    const preguntas = P.examen.preguntas;
    let aciertos = 0;
    const resumen = preguntas.map((q, i) => {
      const mios = P.resp[i];
      if (mios === q.correcta) aciertos++;
      const opts = q.opciones.map((o, j) => {
        const cls = j === q.correcta ? ' correct' : (j === mios ? ' wrong' : '');
        return '<div class="opt' + cls + '" style="cursor:default"><span class="letra l' + j + '">' + LETRAS[j] + '</span>' +
          '<span data-math="' + esc(o) + '"></span>' +
          (j === q.correcta ? ' <span class="tag">correcta</span>' : '') +
          (j === mios ? ' ✱' : '') + '</div>';
      }).join('');
      return '<div class="card"><div class="q-count">Pregunta ' + (i + 1) + '</div>' +
        '<h2 data-math="' + esc(q.p) + '"></h2>' + (q.f ? mathDiv(q.f) : '') + '<div>' + opts + '</div></div>';
    }).join('<div style="height:10px"></div>');
    const pct = preguntas.length ? Math.round(100 * aciertos / preguntas.length) : 0;
    return '<div class="card center"><h2>🏁 Resultado</h2>' +
      '<p style="font-size:30px;margin:6px 0"><b>' + aciertos + '/' + preguntas.length + '</b></p>' +
      '<p>' + (pct >= 60 ? '🎉 Muy bien (' + pct + '%)' : '📚 Sigue practicando (' + pct + '%)') + '</p>' +
      '<button class="btn" onclick="practicaRepetir()">🔁 Repetir quiz</button>' +
      '<button class="btn secondary" onclick="volver()">Elegir otro tema</button></div>' + resumen;
  }

  // ---------- alumno: unirse --------------------------------------------
  function vAlumnoUnirse() {
    const wrap = renderShell('Alumno', true);
    wrap.innerHTML =
      '<div class="card"><h2>🔑 Codigo de la sesion</h2>' +
      '<input type="text" id="inCodigo" inputmode="numeric" maxlength="4" placeholder="••••" autofocus>' +
      '<button class="btn" onclick="alumnoUnirse()">Entrar al examen</button></div>' +
      '<p class="muted center">El codigo lo indica el profesor en clase.</p>';
  }
  window.alumnoUnirse = async function () {
    const code = ($id('inCodigo').value || '').replace(/\D/g, '').slice(0, 4);
    if (code.length !== 4) { msg('Escribe el codigo de 4 digitos.'); return; }
    const j = await api.post('/api/unirse', { code: code });
    if (!j.ok) { msg(j.error || 'No se pudo unir.'); return; }
    S.code = code;
    S.sesion = j;
    S.resp = {};
    goto('alumno-sala');
    pintarAlumno(j);
    loopAlumno();
  };

  // ---------- alumno: sala ----------------------------------------------
  function vAlumnoSala() {
    const wrap = renderShell('Sala de examen', true);
    wrap.innerHTML = '<div id="zona"><div class="card center"><span class="spin">⏳</span> Conectando...</div></div>';
    if (!S.sesion || S.sesion.code !== S.code) {
      api.get('/api/estado?code=' + encodeURIComponent(S.code)).then((j) => {
        if (j.ok) { S.sesion = j; pintarAlumno(j); loopAlumno(); }
        else mostrarErrorAlumno(j);
      });
      return;
    }
    pintarAlumno(S.sesion);
    loopAlumno();
  }
  function mostrarErrorAlumno(j) {
    const zona = $id('zona');
    if (zona) zona.innerHTML = '<div class="card center"><h2>⚠️</h2><p class="mal">' + esc(j.error || 'error') + '</p>' +
      '<button class="btn" onclick="volver()">Volver</button></div>';
  }
  function loopAlumno() {
    const t = loopTok;
    (async function tick() {
      if (t !== loopTok) return;
      const j = await api.get('/api/estado?code=' + encodeURIComponent(S.code));
      if (t !== loopTok) return;
      if (!j.ok) {
        if (j.error && /cerro/i.test(j.error || '')) { S.sesion = j; pintarAlumno({ ...S.sesion, status: 'cerrada' }); }
        else mostrarErrorAlumno(j);
        setTimeout(tick, 3000);
        return;
      }
      if (j.code === S.code && JSON.stringify(j) !== JSON.stringify(S.sesion)) pintarAlumno(j);
      S.sesion = j;
      setTimeout(tick, 2500);
    })();
  }
  function pintarAlumno(j) {
    S.resp = {};
    for (const r of (j.mis_respuestas || [])) S.resp[r.q] = r.opcion;
    const zona = $id('zona');
    if (!zona) return;
    if (j.status === 'espera') {
      zona.innerHTML =
        '<div class="card center"><h2>🛋️ Esperando al profesor</h2>' +
        '<p class="muted">Te uniste a <b>' + esc(j.titulo) + '</b></p>' +
        '<p><span class="pill wait">' + (j.unidos || 1) + ' alumno(s) en sala</span></p>' +
        '<p class="muted">Cuando empiece, la pregunta aparecera aqui.</p></div>';
    } else if (j.status === 'activa') {
      zona.innerHTML = preguntaHtml(j);
    } else if (j.status === 'final') {
      zona.innerHTML = finalHtml(j);
    } else if (j.status === 'cerrada') {
      zona.innerHTML = '<div class="card center"><h2>✅ Examen cerrado</h2>' +
        '<p class="muted">El profesor cerro la sesion.</p><button class="btn" onclick="volver()">Entendido</button></div>';
    }
    mountMath(zona);
  }
  function preguntaHtml(j) {
    const q = j.preguntas[0];
    if (!q) return '<div class="card center"><span class="spin">⏳</span> Cargando pregunta...</div>';
    const ya = S.resp[q.q];
    const opts = q.opciones.map((o, i) => {
      const sel = ya === i;
      return '<button class="opt' + (sel ? ' sel' : '') + '" id="opt-' + i + '" onclick="alumnoElegir(' + q.q + ',' + i + ')">' +
        '<span class="letra l' + i + '">' + LETRAS[i] + '</span>' +
        '<span data-math="' + esc(o) + '"></span></button>';
    }).join('');
    return '<div class="card">' +
      '<div class="q-count">Pregunta <b>' + (j.current + 1) + '</b> de ' + j.total + '</div>' +
      '<h2 data-math="' + esc(q.p) + '"></h2>' +
      (q.f ? mathDiv(q.f) : '') +
      '</div><div class="opts">' + opts + '</div>' +
      '<p class="muted center" id="estadoResp">' +
      (ya != null ? '✅ Respuesta guardada (puedes cambiarla). Espera a la siguiente...' : 'Toca tu respuesta') + '</p>';
  }
  window.alumnoElegir = async function (q, i) {
    const btns = document.querySelectorAll('#zona .opt');
    btns.forEach((b) => b.classList.remove('sel'));
    const b = $id('opt-' + i);
    if (b) b.classList.add('sel');
    const ed = $id('estadoResp');
    if (ed) ed.textContent = 'Guardando...';
    const j = await api.post('/api/responder', { code: S.code, pregunta: q, opcion: i });
    if (j.ok) {
      S.resp[q] = i;
      haptic('success');
      if (ed) ed.textContent = '✅ Respuesta guardada. Espera a la siguiente...';
    } else {
      if (ed) ed.textContent = '';
      msg(j.error || 'No se pudo guardar.');
      if (S.sesion) pintarAlumno(S.sesion);
    }
  };
  function finalHtml(j) {
    let aciertos = 0;
    const bloques = j.preguntas.map((q) => {
      const correcta = q.correcta;
      const mios = S.resp[q.q];
      if (mios === correcta) aciertos++;
      const opts = q.opciones.map((o, i) => {
        const cls = i === correcta ? ' correct' : (i === mios ? ' wrong' : '');
        const marca = i === mios ? ' ✱' : '';
        return '<div class="opt' + cls + '" style="cursor:default">' +
          '<span class="letra l' + i + '">' + LETRAS[i] + '</span>' +
          '<span data-math="' + esc(o) + '"></span>' + (i === correcta ? ' <span class="tag">correcta</span>' : '') + marca + '</div>';
      }).join('');
      return '<div class="card"><div class="q-count">Pregunta ' + (q.q + 1) + '</div>' +
        '<h2 data-math="' + esc(q.p) + '"></h2>' + (q.f ? mathDiv(q.f) : '') +
        '<div>' + opts + '</div></div>';
    }).join('');
    const pct = j.total ? Math.round(100 * aciertos / j.total) : 0;
    return '<div class="card center"><h2>🏁 Resultado final</h2>' +
      '<p style="font-size:30px;margin:4px 0"><b>' + aciertos + '/' + j.total + '</b></p>' +
      '<p>' + (pct >= 60 ? '🎉 ' : '📚 ') + 'Aciertos: ' + aciertos + ' (' + pct + '%)</p></div>' + bloques;
  }

  // ---------- profesor: configurar --------------------------------------
  function vProfeConfig() {
    const wrap = renderShell('Soy profesor(a)', true);
    wrap.innerHTML = '<div id="zona" class="card center"><span class="spin">⏳</span> Cargando examenes...</div>';
    Promise.all([api.get('/api/config'), api.get('/api/examenes')]).then(([cfg, exRes]) => {
      S.pinReq = !!(cfg && cfg.pin);
      const zona = $id('zona');
      if (!zona) return;
      if (!exRes.ok) { zona.innerHTML = '<p class="mal">Error: ' + esc(exRes.error) + '</p>'; return; }
      const exs = exRes.examenes;
      zona.outerHTML = '<div id="zona">' +
        (S.pinReq
          ? '<div class="card"><h2>🔒 PIN de profesor</h2><input type="text" id="inPin" inputmode="numeric" maxlength="6" placeholder="PIN"></div>'
          : '') +
        '<div class="card"><h2>📋 Elige el examen</h2>' +
        agruparQuizzes(exs, (e) =>
          '<button class="opt ex-card" id="ex-' + e.id + '" onclick="profeElegirExamen(\'' + e.id + '\')">' +
          '<span class="letra l0">📝</span><span><b>' + esc(e.titulo) + '</b><br><span class="muted">' +
          esc(e.descripcion) + ' · ' + e.total + ' preguntas</span></span></button>') +
        '</div>' +
        '<button class="btn" id="btnCrear" disabled onclick="profeIniciar()">🚀 Iniciar sesion de examen</button>' +
        '</div>';
    });
  }
  window.profeElegirExamen = function (id) {
    S.examen = id;
    document.querySelectorAll('.ex-card').forEach((b) => b.classList.remove('sel'));
    const sel = $id('ex-' + id);
    if (sel) sel.classList.add('sel');
    const crear = $id('btnCrear');
    if (crear) crear.disabled = false;
  };
  window.profeIniciar = async function () {
    if (!S.examen) { msg('Elige un examen primero.'); return; }
    const pin = S.pinReq ? (($id('inPin') || {}).value || '').trim() : '';
    if (S.pinReq && !pin) { msg('Escribe el PIN de profesor.'); return; }
    const j = await api.post('/api/crear', { examen_id: S.examen, pin: pin });
    if (!j.ok) { msg(j.error || 'No se pudo crear la sesion.'); return; }
    S.code = j.code;
    S.sesion = null;
    goto('profe-sala');
    pintarProfe(null);
    loopProfe();
  };

  // ---------- profesor: sala en vivo ------------------------------------
  function vProfeSala() {
    const wrap = renderShell('Sala del profesor', true);
    wrap.innerHTML = '<div class="card center"><div class="big-code" id="codigoGrande">' + esc(S.code) + '</div>' +
      '<p class="muted">Comparte este codigo con tus alumnos</p></div><div id="zona">' +
      '<div class="card center"><span class="spin">⏳</span> Conectando...</div></div>';
    if (!S.sesion) {
      api.get('/api/profesor/estado?code=' + encodeURIComponent(S.code)).then((j) => {
        if (j.ok) { S.sesion = j; pintarProfe(j); loopProfe(); }
        else pintarProfe(j, true);
      });
      return;
    }
    pintarProfe(S.sesion);
    loopProfe();
  }
  function loopProfe() {
    const t = loopTok;
    (async function tick() {
      if (t !== loopTok) return;
      const j = await api.get('/api/profesor/estado?code=' + encodeURIComponent(S.code));
      if (t !== loopTok) return;
      if (!j.ok) { pintarProfe(j, true); setTimeout(tick, 3000); return; }
      if (j.code === S.code && JSON.stringify(j) !== JSON.stringify(S.sesion)) pintarProfe(j);
      S.sesion = j;
      setTimeout(tick, 2000);
    })();
  }
  function pintarProfe(j, esError) {
    const zona = $id('zona');
    if (!zona) return;
    if (esError) {
      zona.innerHTML = '<div class="card center"><p class="mal">' + esc(j.error || 'error') + '</p>' +
        '<button class="btn" onclick="volver()">Volver</button></div>';
      return;
    }
    if (j.status === 'espera') {
      zona.innerHTML =
        '<div class="card"><h2>👥 Alumnos en sala: <b>' + (j.unidos || []).length + '</b></h2>' +
        '<p class="scroll-y muted">' + (j.unidos.length ? j.unidos.map((a) => '• ' + esc(a.nombre)).join('<br>') : 'Aun nadie. Espera a que entren con el codigo.') + '</p></div>' +
        '<button class="btn" onclick="profeAccion(\'empezar\')">🚀 Empezar examen</button>';
    } else if (j.status === 'activa') {
      const q = j.preguntas[j.current];
      const conteo = j.conteo || {};
      const totalResp = j.avance ? Object.keys(j.avance).filter((u) => (j.avance[u] || 0) >= j.current + 1).length : 0;
      const maxC = Math.max(1, ...Object.values(conteo));
      const esUltima = j.current >= j.total - 1;
      const barras = Object.keys(q.opciones).map((i) => {
        const n = conteo[i] || 0;
        const ancho = Math.round(100 * n / maxC);
        const ok = j.correcta === Number(i);
        return '<div class="barra"><span class="name l' + i + '">' + LETRAS[i] + '</span>' +
          '<div class="track"><div class="fill l' + i + '" style="width:' + ancho + '%"></div></div>' +
          '<span class="cnt">' + n + '</span>' + (ok ? '<span class="tag">✔ correcta</span>' : '') + '</div>';
      }).join('');
      zona.innerHTML =
        '<div class="card"><div class="q-count">Pregunta <b>' + (j.current + 1) + '</b> de ' + j.total +
        ' · respondidas <b>' + totalResp + '</b>/' + (j.unidos || []).length + '</div>' +
        '<h2 data-math="' + esc(q.p) + '"></h2>' + (q.f ? mathDiv(q.f) : '') +
        '<div class="center">' + barras + '</div></div>' +
        '<div class="grid2">' +
        '<button class="btn" onclick="profeAccion(\'' + (esUltima ? 'ver_resultados' : 'siguiente') + '\')">' +
        (esUltima ? '🏁 Ver resultados finales' : 'Siguiente pregunta →') + '</button>' +
        '<button class="btn secondary" onclick="profeAccion(\'cerrar\')">✖ Cerrar examen</button></div>';
    } else if (j.status === 'final') {
      const n = (j.unidos || []).length;
      zona.innerHTML =
        '<div class="card center"><h2>🏁 Examen terminado</h2><p class="muted">' + n +
        ' alumno(s) participaron en ' + j.total + ' preguntas.</p></div>' +
        '<button class="btn" onclick="irReporte()">📊 Ver reporte de resultados</button>' +
        '<button class="btn secondary" onclick="profeAccion(\'cerrar\')">✖ Cerrar examen y guardar reporte</button>';
    } else if (j.status === 'cerrada') {
      zona.innerHTML = '<div class="card center"><h2>✅ Examen cerrado</h2>' +
        '<p class="muted">El reporte se guardo en el servidor.</p>' +
        '<button class="btn" onclick="irReporte()">📊 Ver reporte</button>' +
        '<button class="btn secondary" onclick="volver()">Crear otra sesion</button></div>';
    }
    mountMath(zona);
  }
  window.profeAccion = async function (accion) {
    const j = await api.post('/api/siguiente', { code: S.code, accion: accion });
    if (!j.ok) { msg(j.error || 'accion fallida'); return; }
    S.sesion = null;
    const est = await api.get('/api/profesor/estado?code=' + encodeURIComponent(S.code));
    if (est.ok && est.code === S.code) {
      S.sesion = est;
      pintarProfe(est);
    }
  };
  window.irReporte = function () { goto('profe-reporte'); };

  // ---------- profesor: reporte -----------------------------------------
  function vProfeReporte() {
    const wrap = renderShell('Reporte', true);
    wrap.innerHTML = '<div id="zona" class="card center"><span class="spin">⏳</span> Generando reporte...</div>';
    api.get('/api/reporte?code=' + encodeURIComponent(S.code)).then((j) => {
      if (!j.ok) {
        const z = $id('zona');
        if (z) z.innerHTML = '<p class="mal">' + esc(j.error || 'error') + '</p>';
        return;
      }
      S.reporte = j.reporte;
      pintarReporte();
    });
  }
  function pintarReporte() {
    const r = S.reporte;
    const zona = $id('zona');
    if (!zona) return;
    const proms = r.n_alumnos ? (r.filas.reduce((a, f) => a + f.pct, 0) / r.n_alumnos) : 0;
    // tabla por alumno
    const cab = r.por_pregunta.map((_, i) => '<th>T' + (i + 1) + '</th>').join('');
    const filas = r.filas.map((f) =>
      '<tr><td class="a">' + esc(f.nombre) + '</td><td><b>' + f.aciertos + '/' + f.total + '</b></td><td>' + f.pct + '%</td>' +
      f.detalle.map((d) => {
        if (d.opcion == null) return '<td>—</td>';
        const cls = d.ok ? 'ok' : 'mal';
        return '<td class="' + cls + '">' + LETRAS[d.opcion] + '</td>';
      }).join('') + '</tr>').join('');
    // por pregunta
    const porPreg = r.por_pregunta.map((pp) => {
      const maxC = Math.max(1, ...Object.values(pp.cuenta));
      const barras = pp.opciones.map((o, i) => {
        const n = pp.cuenta[i] || 0;
        return '<div class="barra"><span class="name l' + i + '">' + LETRAS[i] + '</span>' +
          '<div class="track"><div class="fill l' + i + '" style="width:' + Math.round(100 * n / maxC) + '%"></div></div>' +
          '<span class="cnt">' + n + '</span>' + (i === pp.correcta ? '<span class="tag">✔</span>' : '') + '</div>';
      }).join('');
      return '<div class="card"><div class="q-count">Pregunta ' + (pp.q + 1) + ' · aciertos ' + pp.aciertos + '/' + pp.respondidas + '</div>' +
        '<h2 data-math="' + esc(pp.p) + '"></h2>' + (pp.f ? mathDiv(pp.f) : '') +
        '<div>' + barras + '</div></div>';
    }).join('');
    zona.outerHTML = '<div id="zona">' +
      '<div class="card center"><h2>📊 Reporte: ' + esc(r.titulo) + '</h2>' +
      '<p class="muted">Codigo <b>' + r.code + '</b> · ' + r.n_alumnos + ' alumno(s) · promedio ' + Math.round(proms) + '%</p>' +
      '<button class="btn" onclick="exportarCSV()" style="display:inline-block;width:auto;padding:10px 16px">📥 Exportar CSV</button>' +
      '<button class="btn secondary" style="display:inline-block;width:auto;padding:10px 16px" onclick="exportarHTML()">🖨️ Version imprimible</button></div>' +
      '<div class="card scroll-x"><h2>Por alumno</h2><table class="tabla"><tr><th>Nombre</th><th>Puntaje</th><th>%</th>' + cab + '</tr>' + filas + '</table></div>' +
      porPreg +
      '<button class="btn" onclick="profeAccion(\'cerrar\')">✖ Cerrar examen y guardar</button>' +
      '</div>';
    mountMath($id('zona'));
  }
  function csvTexto() {
    const r = S.reporte;
    const cab = ['Nombre', 'Aciertos', 'Total', 'Pct'].concat(r.por_pregunta.map((_, i) => 'P' + (i + 1)));
    const filas = r.filas.map((f) => {
      const det = f.detalle.map((d) => d.opcion == null ? '' : LETRAS[d.opcion] + (d.ok ? '*' : ''));
      return [f.nombre, f.aciertos, f.total, f.pct].concat(det);
    });
    return [cab].concat(filas).map((f) => f.map((v) => /[",\n]/.test(String(v)) ? '"' + String(v).replace(/"/g, '""') + '"' : v).join(',')).join('\n');
  }
  window.exportarCSV = function () {
    if (!S.reporte) return;
    const txt = csvTexto();
    try {
      const blob = new Blob(['\ufeff' + txt], { type: 'text/csv;charset=utf-8' });
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'reporte_' + S.code + '.csv';
      document.body.appendChild(a);
      a.click();
      setTimeout(() => a.remove(), 0);
    } catch (_) {}
    try { navigator.clipboard.writeText(txt); } catch (_) {}
    msg('CSV generado (descargado y copiado al portapapeles).');
  };
  window.exportarHTML = function () {
    window.open('/api/reporte.html?code=' + encodeURIComponent(S.code) + '&uid=' + encodeURIComponent(App.uid), '_blank');
  };

  // ---------- arranque ---------------------------------------------------
  function devBanner() {
    const bar = $id('devbar');
    if (!App.dev || !bar) return;
    bar.style.display = 'flex';
    bar.innerHTML = '<b>DEV</b><span>' + esc(App.nombre) + '</span>' +
      '<button onclick="cambiarIdentidad()" style="margin-left:auto;padding:4px 8px;border-radius:6px;border:none">Cambiar alumno</button>';
    document.querySelectorAll('#devbar button').forEach((b) => b.addEventListener('click', cambiarIdentidad));
    document.body.style.paddingBottom = '44px';
  }
  window.cambiarIdentidad = function () {
    const n = newIdentidad();
    if (n) {
      const luego = { 'alumno-sala': S.sesion ? S.vista : 'alumno-unirse' }[S.vista] || S.vista;
      S.sesion = null;
      goto(luego);
      devBanner();
    }
  };
  (function init() {
    initApp();
    if (App.dev) devBanner();
    const area = App.area === 'teoria' ? 'teoria' : (App.area === 'quizzes' ? 'quizzes' : 'inicio');
    goto(area);
  })();
})();