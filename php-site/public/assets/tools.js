"use strict";
(() => {
  const format = value => "Gs. " + new Intl.NumberFormat("es-PY", {maximumFractionDigits: 0}).format(value);
  document.querySelectorAll("[data-tool]").forEach(tool => {
    const form = tool.querySelector("form");
    form.addEventListener("submit", event => event.preventDefault());
    tool.querySelectorAll("[data-print]").forEach(button => button.addEventListener("click", () => window.print()));
    if (tool.dataset.tool === "budget") {
      const fields = [...tool.querySelectorAll("[data-cost]")];
      const update = () => {
        const sums = {monthly: 0, annual: 0, initial: 0, reserve: 0};
        let missing = 0;
        for (const field of fields) {
          if (field.value === "") { missing++; continue; }
          if (!field.validity.valid || !Number.isFinite(field.valueAsNumber)) {
            tool.querySelector("#budget-status").textContent = "Revisá los importes: usá números enteros entre 0 y 1.000.000.000.000 guaraníes.";
            tool.querySelectorAll("output").forEach(output => {output.textContent = "Revisá los importes";});
            return;
          }
          sums[field.dataset.cost] += field.valueAsNumber;
        }
        const monthly = sums.monthly + sums.annual / 12;
        tool.querySelector("#budget-result-monthly").textContent = format(monthly);
        tool.querySelector("#budget-result-reserve").textContent = format(sums.reserve);
        tool.querySelector("#budget-result-annual").textContent = format(monthly * 12);
        tool.querySelector("#budget-result-year").textContent = format((monthly + sums.reserve) * 12 + sums.initial);
        tool.querySelector("#budget-status").textContent = missing ? `Suma parcial: ${missing} rubros pendientes. Completá las cotizaciones antes de decidir.` : "Suma de los importes cargados. Revisá que cada gasto aparezca una sola vez; los resultados se redondean a guaraníes.";
      };
      form.addEventListener("input", update);
      form.addEventListener("reset", () => setTimeout(update, 0));
      update();
    }
  });
})();
