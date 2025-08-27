// Consolidated site-wide custom JS extracted from inline scripts
(function(){
  try {
    const cart = JSON.parse(localStorage.getItem('cart') || '[]');
    const count = cart.reduce((s,i)=> s + (i.qty||0), 0);
    const badge = document.getElementById('nav-cart-count');
    if (badge) badge.textContent = count ? count : '';
  } catch(e) {}
})();

(function(){
  const form = document.querySelector('.contact-form');
  if(!form) return;
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const btn = document.getElementById('send-btn');
    if(btn) btn.disabled = true;
    const fd = new FormData(form);
    const csrftoken = fd.get('csrfmiddlewaretoken');
    try {
      const res = await fetch(form.action || location.href, {
        method:'POST',
        body: fd,
        headers:{'X-CSRFToken':csrftoken,'X-Requested-With':'XMLHttpRequest'}
      });
      let data, ct = res.headers.get('content-type') || '';
      if(ct.includes('application/json')) data = await res.json();
      flash((data && data.message) || 'The message has been sent successfully');
      form.reset();
    } catch(err){
      flash('Send failed');
    } finally {
      if(btn) btn.disabled = false;
    }
  });
  function flash(msg){
    let el = document.getElementById('flash-message');
    if(!el){
      el = document.createElement('div');
      el.id='flash-message';
      el.className='flash-message';
      document.body.appendChild(el);
      el.addEventListener('animationend', ev => { if(ev.animationName==='flash-out') el.remove(); });
    }
    el.textContent = msg;
    el.classList.remove('flash-hide');
    setTimeout(()=> el.classList.add('flash-hide'), 3000);
  }
})();

// Offcanvas navbar toggle
(function(){
  const rootNav = document.querySelector('.site-nav');
  if(!rootNav) return;
  const toggle = document.getElementById('navToggle');
  const offcanvas = document.getElementById('offcanvasMenu');
  const closeBtn = document.getElementById('navClose');
  if(!toggle || !offcanvas) return;

  // duplicate cart count to mobile badge if present
  function syncCartBadge(){
    const desktop = document.getElementById('nav-cart-count');
    const mobile = document.getElementById('nav-cart-count-mobile');
    if(desktop && mobile) mobile.textContent = desktop.textContent || '';
  }
  syncCartBadge();

  function disableScroll(disable){
    document.body.classList.toggle('no-scroll', !!disable);
  }

  function trapFocus(e){
    if(e.key !== 'Tab') return;
    const focusables = offcanvas.querySelectorAll('a,button,[tabindex]:not([tabindex="-1"])');
    if(!focusables.length) return;
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    if(e.shiftKey && document.activeElement === first){
      e.preventDefault(); last.focus();
    } else if(!e.shiftKey && document.activeElement === last){
      e.preventDefault(); first.focus();
    }
  }

  function openMenu(){
    offcanvas.classList.add('active');
    offcanvas.setAttribute('aria-hidden','false');
    toggle.setAttribute('aria-expanded','true');
    toggle.classList.add('active');
    disableScroll(true);
    // focus first link
    const firstLink = offcanvas.querySelector('.offcanvas__links a, .offcanvas__close');
    if(firstLink) firstLink.focus();
    document.addEventListener('keydown', escHandler);
    document.addEventListener('keydown', trapFocus);
  }

  function closeMenu(){
    offcanvas.classList.remove('active');
    offcanvas.setAttribute('aria-hidden','true');
    toggle.setAttribute('aria-expanded','false');
    toggle.classList.remove('active');
    disableScroll(false);
    document.removeEventListener('keydown', escHandler);
    document.removeEventListener('keydown', trapFocus);
    toggle.focus();
  }

  function escHandler(e){ if(e.key==='Escape') closeMenu(); }

  toggle.addEventListener('click', ()=>{
    const active = offcanvas.classList.contains('active');
    active ? closeMenu() : openMenu();
  });
  if(closeBtn) closeBtn.addEventListener('click', closeMenu);
  // click outside panel closes
  offcanvas.addEventListener('click', e=>{
    if(!e.target.closest('.offcanvas__panel')) closeMenu();
  });
  // link clicks close
  offcanvas.querySelectorAll('.offcanvas__links a').forEach(a=> a.addEventListener('click', closeMenu));
})();
