(function () {
  var year = document.getElementById("year");
  if (year) year.textContent = String(new Date().getFullYear());

  var cosmos = document.querySelector(".cosmos");
  if (!cosmos || window.matchMedia("(prefers-reduced-motion: reduce)").matches) return;

  var layers = cosmos.querySelectorAll("[data-depth]");
  if (!layers.length) return;

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
      requestAnimationFrame(update);
    }
  }

  function update() {
    currentX += (targetX - currentX) * 0.12;
    currentY += (targetY - currentY) * 0.12;

    for (var i = 0; i < layers.length; i++) {
      var depth = parseFloat(layers[i].getAttribute("data-depth") || "0");
      // Much stronger parallax so movement is obvious
      var x = currentX * depth * -220;
      var y = currentY * depth * -140;
      layers[i].style.translate = x.toFixed(2) + "px " + y.toFixed(2) + "px";
    }

    if (Math.abs(targetX - currentX) > 0.001 || Math.abs(targetY - currentY) > 0.001) {
      requestAnimationFrame(update);
    } else {
      ticking = false;
    }
  }

  window.addEventListener("pointermove", onMove, { passive: true });
})();
