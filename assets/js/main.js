/* ATON+ — interactions */
(function () {
  'use strict';

  var reduced = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ── scroll reveal ─────────────────────────────────────── */
  var reveals = document.querySelectorAll('.reveal');
  if (reduced || !('IntersectionObserver' in window)) {
    reveals.forEach(function (el) { el.classList.add('is-in'); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { e.target.classList.add('is-in'); io.unobserve(e.target); }
      });
    }, { threshold: 0.12, rootMargin: '0px 0px -8% 0px' });
    reveals.forEach(function (el) { io.observe(el); });
  }

  /* ── counting stats ────────────────────────────────────── */
  var nums = document.querySelectorAll('.stat__num[data-count]');
  function countUp(el) {
    var target = parseInt(el.dataset.count, 10);
    var suffix = el.dataset.suffix || '';
    var start = performance.now();
    var dur = 1400;
    (function tick(now) {
      var p = Math.min((now - start) / dur, 1);
      var eased = 1 - Math.pow(1 - p, 3);
      el.textContent = Math.round(target * eased) + suffix;
      if (p < 1) requestAnimationFrame(tick);
    })(start);
  }
  if (!reduced && 'IntersectionObserver' in window) {
    var ioNum = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) { countUp(e.target); ioNum.unobserve(e.target); }
      });
    }, { threshold: 0.6 });
    nums.forEach(function (el) { ioNum.observe(el); });
  }

  /* ── production gallery ────────────────────────────────── */
  var gallery = document.querySelector('[data-gallery="pg"]');
  if (gallery) {
    var main = document.getElementById('pgMain');
    var thumbs = Array.prototype.slice.call(gallery.querySelectorAll('.thumb'));
    var index = 0;

    function show(i) {
      index = (i + thumbs.length) % thumbs.length;
      var t = thumbs[index];
      thumbs.forEach(function (b) { b.classList.toggle('is-active', b === t); });
      main.style.opacity = '0';
      window.setTimeout(function () {
        main.src = t.dataset.src;
        main.style.opacity = '1';
      }, reduced ? 0 : 180);
    }

    main.style.transition = 'opacity .35s cubic-bezier(.22,.61,.36,1)';
    thumbs.forEach(function (b, i) { b.addEventListener('click', function () { show(i); }); });
    gallery.querySelector('.rounder--prev').addEventListener('click', function () { show(index - 1); });
    gallery.querySelector('.rounder--next').addEventListener('click', function () { show(index + 1); });
  }

  /* ── cases rail ────────────────────────────────────────── */
  var track = document.getElementById('casesTrack');
  var next = document.getElementById('casesNext');
  if (track && next) {
    next.addEventListener('click', function () {
      var card = track.querySelector('.case');
      var step = card ? card.offsetWidth + 14 : 280;
      var max = track.scrollWidth - track.clientWidth;
      var to = track.scrollLeft + step;
      track.scrollTo({ left: to > max - 4 ? 0 : to, behavior: reduced ? 'auto' : 'smooth' });
    });
  }

  /* ── mobile menu ───────────────────────────────────────── */
  var burger = document.querySelector('.burger');
  var menu = document.getElementById('mobileMenu');
  if (burger && menu) {
    function setMenu(open) {
      burger.setAttribute('aria-expanded', String(open));
      menu.hidden = !open;
      document.body.style.overflow = open ? 'hidden' : '';
    }
    burger.addEventListener('click', function () {
      setMenu(burger.getAttribute('aria-expanded') !== 'true');
    });
    menu.addEventListener('click', function (e) {
      if (e.target.tagName === 'A') setMenu(false);
    });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && !menu.hidden) setMenu(false);
    });
  }

  /* ── active section in nav ─────────────────────────────── */
  var links = Array.prototype.slice.call(document.querySelectorAll('.nav__links a'));
  // the nav lists sections in a different order than the document does — sort by position
  var sections = links
    .map(function (a) { return document.querySelector(a.getAttribute('href')); })
    .filter(Boolean)
    .sort(function (a, b) { return a.offsetTop - b.offsetTop; });

  if (sections.length) {
    var ticking = false;

    function syncNav() {
      ticking = false;
      var line = window.innerHeight * 0.3;
      var current = null;
      sections.forEach(function (s) {
        if (s.getBoundingClientRect().top <= line) current = s;
      });
      // near the bottom of the page the last section is always the active one
      if (window.innerHeight + window.scrollY >= document.documentElement.scrollHeight - 4) {
        current = sections[sections.length - 1];
      }
      links.forEach(function (a) {
        a.classList.toggle('is-active', !!current && a.getAttribute('href') === '#' + current.id);
      });
    }

    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(syncNav); }
    }, { passive: true });
    window.addEventListener('resize', syncNav);
    syncNav();
  }
})();
