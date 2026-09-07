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

  // 标记脚本已接管：CSS 的入场隐藏态只在 html.js 下生效，
  // 本脚本被拦截或执行失败时，所有屏的内容保持可见
  document.documentElement.classList.add("js");

  var slides = Array.prototype.slice.call(slider.querySelectorAll(".slide"));
  var dots = Array.prototype.slice.call(document.querySelectorAll(".slide-dots .dot"));
  var navLinks = Array.prototype.slice.call(document.querySelectorAll(".nav-links [data-section]"));
  var reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var isAnimating = false;
  var current = 0;
  var wheelAcc = 0;
  var wheelReset = 0;
  var wheelMuted = false;
  var wheelIdle = 0;
  var animTimer = 0;
  var coolUntil = 0;
  var touchStartY = 0;
  var touchStartX = 0;
  var lastPageAt = 0;

  function sectionIndex(id) {
    for (var i = 0; i < slides.length; i++) {
      if (slides[i].id === id) return i;
    }
    return 0;
  }

  function innerEl(index) {
    return slides[index] ? slides[index].querySelector(".slide-inner") : null;
  }

  function innerCanScroll(index, direction, event) {
    var inner = innerEl(index);
    if (event && event.target) {
      var node = event.target;
      inner = null;
      while (node && node !== slider) {
        if (node.classList && node.classList.contains("slide-inner")) {
          inner = node;
          break;
        }
        node = node.parentNode;
      }
    }
    if (!inner) return false;
    if (inner.scrollHeight <= inner.clientHeight + 8) return false;
    if (direction > 0) return inner.scrollTop + inner.clientHeight < inner.scrollHeight - 8;
    return inner.scrollTop > 8;
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
    wheelAcc = 0;
    lastPageAt = Date.now();
    coolUntil = lastPageAt + 420;
    window.clearTimeout(wheelReset);
    wheelReset = window.setTimeout(function () {
      wheelAcc = 0;
    }, 420);
    if (next === current && !instant) return;

    setActive(next);
    paint(current, instant);

    if (instant || reduceMotion) {
      isAnimating = false;
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
  });

  window.addEventListener(
    "wheel",
    function (event) {
      if (event.ctrlKey || event.metaKey) return;

      var delta = event.deltaY;
      if (event.deltaMode === 1) delta *= 16;
      if (event.deltaMode === 2) delta *= slideHeight();
      if (!delta) return;

      // 一段连续的滚轮事件流算同一次手势：事件流安静 220ms 才算结束。
      // 翻页后进入静音，把惯性尾巴整体吞掉，避免冷却一过又翻一页
      window.clearTimeout(wheelIdle);
      wheelIdle = window.setTimeout(function () {
        wheelMuted = false;
        wheelAcc = 0;
      }, 220);

      if (innerCanScroll(current, delta, event)) return;

      event.preventDefault();
      if (Date.now() < coolUntil) return;
      if (wheelMuted) return;

      if (Math.abs(delta) < 10) return;

      if (reduceMotion) {
        wheelMuted = true;
        goTo(current + (delta > 0 ? 1 : -1), true);
        return;
      }

      wheelAcc += delta;
      if (Math.abs(wheelAcc) < 36) return;
      wheelMuted = true;
      goTo(current + (wheelAcc > 0 ? 1 : -1));
    },
    { passive: false, capture: true }
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
      if (innerCanScroll(current, dy, event)) return;
      event.preventDefault();
    },
    { passive: false }
  );

  slider.addEventListener(
    "touchend",
    function (event) {
      var dy = touchStartY - event.changedTouches[0].clientY;
      var dx = Math.abs(event.changedTouches[0].clientX - touchStartX);
      if (dx > Math.abs(dy) || Math.abs(dy) < 48) return;
      if (innerCanScroll(current, dy, event)) return;
      if (Date.now() - lastPageAt < 280) return;
      goTo(current + (dy > 0 ? 1 : -1));
    },
    { passive: true }
  );

  document.addEventListener("keydown", function (event) {
    var tag = event.target && event.target.tagName;
    if (tag === "INPUT" || tag === "TEXTAREA" || event.target.isContentEditable) return;

    if (event.key === "ArrowDown" || event.key === "PageDown" || event.key === " ") {
      event.preventDefault();
      if (Date.now() < coolUntil) return;
      goTo(current + 1);
    } else if (event.key === "ArrowUp" || event.key === "PageUp") {
      event.preventDefault();
      if (Date.now() < coolUntil) return;
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
  // 先让 html.js 的隐藏初始态完成一次样式计算，再落到目标屏：
  // 首屏入场过渡才有「从隐藏到可见」的起点（一切发生在首帧绘制前，不会闪）
  void document.body.offsetHeight;
  goTo(startIndex, true);
})();
