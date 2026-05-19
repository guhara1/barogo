(function () {
  var bar = document.querySelector('.mag-progress-bar');
  if (!bar) return;

  function update() {
    var doc = document.documentElement;
    var scrollTop = window.scrollY || doc.scrollTop;
    var max = (doc.scrollHeight - window.innerHeight) || 1;
    var pct = Math.max(0, Math.min(1, scrollTop / max));
    bar.style.transform = 'scaleX(' + pct + ')';
  }

  // 스티키 TOC — 현재 보이는 섹션 하이라이트
  var tocLinks = document.querySelectorAll('.mag-article-side .mag-toc a[href^="#"]');
  var sections = [];
  tocLinks.forEach(function (a) {
    var id = a.getAttribute('href').slice(1);
    var el = document.getElementById(id);
    if (el) sections.push({ id: id, el: el, link: a });
  });

  function highlight() {
    var y = (window.scrollY || 0) + 140;
    var current = null;
    for (var i = 0; i < sections.length; i++) {
      if (sections[i].el.offsetTop <= y) current = sections[i];
    }
    tocLinks.forEach(function (a) { a.classList.remove('is-active'); });
    if (current) current.link.classList.add('is-active');
  }

  var ticking = false;
  window.addEventListener('scroll', function () {
    if (!ticking) {
      window.requestAnimationFrame(function () {
        update();
        highlight();
        ticking = false;
      });
      ticking = true;
    }
  }, { passive: true });

  update();
  highlight();
})();
