// api.js — helper de la Mini App (Telegram WebApp + modo dev para probar en navegador)
(function () {
  window.App = {
    dev: /[?&](dev|test)=1/.test(location.search),
    tg: null,
    uid: '',
    nombre: 'Estudiante',
    area: new URLSearchParams(location.search).get('area') || '',
  };

  function shim() {
    if (window.Telegram && window.Telegram.WebApp && window.Telegram.WebApp.ready) return;
    window.Telegram = {
      WebApp: {
        initData: '',
        initDataUnsafe: {},
        colorScheme: 'light',
        platform: 'dev',
        version: '8.0',
        isExpanded: true,
        viewportStableHeight: window.innerHeight || 480,
        ready() {}, expand() {}, close() {},
        showAlert: (m) => window.alert(m),
        HapticFeedback: {
          impactOccurred() {}, notificationOccurred() {}, selectionChanged() {},
        },
        MainButton: {
          setText() {}, setParams() {}, onClick() {}, show() {}, hide() {},
          enable() {}, disable() {}, destroy() {},
        },
        onEvent() {}, offEvent() {}, sendData() {},
        openLink: (u) => window.open(u, '_blank'),
      },
    };
  }

  window.initApp = function () {
    if (App.dev) shim();
    const tg = (window.Telegram && window.Telegram.WebApp) || null;
    if (!tg) return;
    App.tg = tg;
    try { tg.ready(); tg.expand(); } catch (_) {}
    const init = tg.initDataUnsafe || {};
    const user = init.user;
    if (user && user.id != null) {
      App.uid = String(user.id);
      App.nombre = [user.first_name, user.last_name].filter(Boolean).join(' ') || 'Estudiante';
    } else if (App.dev) {
      const guardado = JSON.parse(localStorage.getItem('dev_identidad') || 'null');
      if (guardado && guardado.uid) { App.uid = guardado.uid; App.nombre = guardado.nombre; }
      else newIdentidad();
    }
  };

  window.newIdentidad = function () {
    if (!App.dev) return null;
    const n = Math.floor(Math.random() * 9000) + 1000;
    App.uid = 'dev' + n;
    App.nombre = 'Alumno ' + n;
    localStorage.setItem('dev_identidad', JSON.stringify({ uid: App.uid, nombre: App.nombre }));
    return App.nombre;
  };

  async function apiPost(path, body) {
    const payload = Object.assign({}, body || {}, {
      initData: App.tg ? App.tg.initData : '',
    });
    if (App.dev) payload.dev = { uid: App.uid, nombre: App.nombre };
    const res = await fetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    let json;
    try { json = await res.json(); } catch (_) {
      json = { ok: false, error: 'respuesta no JSON (HTTP ' + res.status + ')' };
    }
    return json;
  }

  async function apiGet(path) {
    const sep = path.indexOf('?') === -1 ? '?' : '&';
    const res = await fetch(path + sep + 'uid=' + encodeURIComponent(App.uid));
    let json;
    try { json = await res.json(); } catch (_) {
      json = { ok: false, error: 'respuesta no JSON (HTTP ' + res.status + ')' };
    }
    return json;
  }

  window.api = { post: apiPost, get: apiGet };
})();