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
