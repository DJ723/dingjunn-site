(function () {
  var year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());

  var cosmos = document.querySelector(".cosmos");
  if (cosmos && !window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    var layers = cosmos.querySelectorAll("[data-depth]");
    if (layers.length) {
      var targetX = 0;
      var targetY = 0;
      var currentX = 0;
      var currentY = 0;
      var ticking = false;

      function onMove(event) {
        var w = window.innerWidth || 1;
        var h = window.innerHeight || 1;
        targetX = (event.clientX / w - 0.5) * 2;
        targetY = (event.clientY / h - 0.5) * 2;
        if (!ticking) {
          ticking = true;
          requestAnimationFrame(updateParallax);
        }
      }

      function updateParallax() {
        currentX += (targetX - currentX) * 0.12;
        currentY += (targetY - currentY) * 0.12;

        for (var i = 0; i < layers.length; i++) {
          var depth = parseFloat(layers[i].getAttribute("data-depth") || "0");
          var x = currentX * depth * -220;
          var y = currentY * depth * -140;
          layers[i].style.translate = x.toFixed(2) + "px " + y.toFixed(2) + "px";
        }

        if (Math.abs(targetX - currentX) > 0.001 || Math.abs(targetY - currentY) > 0.001) {
          requestAnimationFrame(updateParallax);
        } else {
          ticking = false;
        }
      }

      window.addEventListener("pointermove", onMove, { passive: true });
    }
  }

  var slider = document.getElementById("slider");
  var track = document.getElementById("slider-track");
  if (!slider || !track) return;

  var slides = Array.prototype.slice.call(slider.querySelectorAll(".slide"));
  var dots = Array.prototype.slice.call(document.querySelectorAll(".slide-dots .dot"));
  var navLinks = Array.prototype.slice.call(document.querySelectorAll(".nav-links [data-section]"));
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isAnimating = false;
  var gestureLocked = false;
  var current = 0;
  var wheelAcc = 0;
  var wheelReset = 0;
  var animTimer = 0;
  var touchStartY = 0;
  var touchStartX = 0;

  function sectionIndex(id) {
    for (var i = 0; i < slides.length; i++) {
      if (slides[i].id === id) return i;
    }
    return 0;
  }

  function innerEl(index) {
    return slides[index] ? slides[index].querySelector(".slide-inner") : null;
  }

  function innerCanScroll(index, direction) {
    var inner = innerEl(index);
    if (!inner) return false;
    if (inner.scrollHeight <= inner.clientHeight + 2) return false;
    if (direction > 0) return inner.scrollTop + inner.clientHeight < inner.scrollHeight - 2;
    return inner.scrollTop > 2;
  }

  function setActive(index) {
    current = Math.max(0, Math.min(slides.length - 1, index));
    var id = slides[current].id;

    for (var i = 0; i < slides.length; i++) {
      slides[i].classList.toggle("is-inview", i === current);
    }
    for (var d = 0; d < dots.length; d++) {
      dots[d].classList.toggle("is-active", dots[d].getAttribute("data-target") === id);
    }
    for (var n = 0; n < navLinks.length; n++) {
      navLinks[n].classList.toggle(
        "is-active",
        navLinks[n].getAttribute("data-section") === id
      );
    }

    if (history.replaceState) {
      history.replaceState(null, "", "#" + id);
    }
  }

  function slideHeight() {
    return slider.clientHeight || window.innerHeight;
  }

  function paint(index, instant) {
    var y = -index * slideHeight();
    slider.classList.toggle("is-instant", !!instant || reduceMotion);
    track.style.transform = "translate3d(0," + y + "px,0)";
    if (instant || reduceMotion) {
      void track.offsetHeight;
      slider.classList.remove("is-instant");
    }
  }

  function goTo(index, instant) {
    var next = Math.max(0, Math.min(slides.length - 1, index));
    if (next === current && !instant) return;

    setActive(next);
    wheelAcc = 0;
    gestureLocked = true;
    paint(current, instant);

    if (instant || reduceMotion) {
      isAnimating = false;
      window.setTimeout(function () {
        gestureLocked = false;
      }, 180);
      return;
    }

    isAnimating = true;
    window.clearTimeout(animTimer);
    animTimer = window.setTimeout(function () {
      isAnimating = false;
    }, 720);
  }

  track.addEventListener("transitionend", function (event) {
    if (event.target !== track || event.propertyName !== "transform") return;
    isAnimating = false;
    wheelAcc = 0;
  });

  slider.addEventListener(
    "wheel",
    function (event) {
      var delta = event.deltaY;
      if (event.deltaMode === 1) delta *= 16;
      if (event.deltaMode === 2) delta *= slideHeight();

      if (innerCanScroll(current, delta)) return;

      event.preventDefault();
      window.clearTimeout(wheelReset);
      wheelReset = window.setTimeout(function () {
        wheelAcc = 0;
        if (!isAnimating) gestureLocked = false;
      }, 240);

      if (isAnimating || gestureLocked) return;

      if (reduceMotion) {
        if (Math.abs(delta) > 20) goTo(current + (delta > 0 ? 1 : -1), true);
        return;
      }

      wheelAcc += delta;
      if (Math.abs(wheelAcc) < 42) return;
      goTo(current + (wheelAcc > 0 ? 1 : -1));
    },
    { passive: false }
  );

  slider.addEventListener(
    "touchstart",
    function (event) {
      touchStartY = event.touches[0].clientY;
      touchStartX = event.touches[0].clientX;
    },
    { passive: true }
  );

  slider.addEventListener(
    "touchmove",
    function (event) {
      var dy = touchStartY - event.touches[0].clientY;
      var dx = Math.abs(event.touches[0].clientX - touchStartX);
      if (dx > Math.abs(dy)) return;
      if (innerCanScroll(current, dy)) return;
      event.preventDefault();
    },
    { passive: false }
  );

  slider.addEventListener(
    "touchend",
    function (event) {
      var dy = touchStartY - event.changedTouches[0].clientY;
      var dx = Math.abs(event.changedTouches[0].clientX - touchStartX);
      if (dx > Math.abs(dy) || Math.abs(dy) < 46) return;
      if (innerCanScroll(current, dy)) return;
      goTo(current + (dy > 0 ? 1 : -1));
    },
    { passive: true }
  );

  document.addEventListener("keydown", function (event) {
    var tag = event.target && event.target.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || event.target.isContentEditable) return;

    if (event.key === "ArrowDown" || event.key === "PageDown" || event.key === " ") {
      event.preventDefault();
      goTo(current + 1);
    } else if (event.key === "ArrowUp" || event.key === "PageUp") {
      event.preventDefault();
      goTo(current - 1);
    } else if (event.key === "Home") {
      event.preventDefault();
      goTo(0);
    } else if (event.key === "End") {
      event.preventDefault();
      goTo(slides.length - 1);
    }
  });

  dots.forEach(function (dot) {
    dot.addEventListener("click", function () {
      goTo(sectionIndex(dot.getAttribute("data-target")));
    });
  });

  document.querySelectorAll('a[href^="#"]').forEach(function (link) {
    link.addEventListener("click", function (event) {
      var id = link.getAttribute("href").slice(1);
      if (!id) return;
      var index = sectionIndex(id);
      if (slides[index] && slides[index].id === id) {
        event.preventDefault();
        goTo(index);
      }
    });
  });

  window.addEventListener("resize", function () {
    paint(current, true);
  });

  var startHash = (location.hash || "#home").slice(1);
  var startIndex = sectionIndex(startHash);
  goTo(startIndex, true);
})();
