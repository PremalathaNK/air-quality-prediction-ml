(function () {
  const form = document.getElementById("pollution-form");
  const globalErrorEl = document.getElementById("global-error");
  const resultsSubtitle = document.getElementById("results-subtitle");
  const resultsContainer = document.getElementById("results-container");
  const resultsBody = document.getElementById("results-body");
  const resultsSummary = document.getElementById("results-summary");
  const summaryAqi = document.getElementById("summary-aqi");
  const summaryCategory = document.getElementById("summary-category");
  const adviceCard = document.getElementById("advice-card");
  const adviceText = document.getElementById("advice-text");

  const ranges = window.PERMITTED_RANGES || {};

  const CATEGORY_CLASS_MAP = {
    Good: "aqi-good",
    Satisfactory: "aqi-satisfactory",
    Moderate: "aqi-moderate",
    Poor: "aqi-poor",
    "Very Poor": "aqi-very-poor",
    Severe: "aqi-severe",
  };

  const AQI_CLASS_NAMES = Object.values(CATEGORY_CLASS_MAP);

  function clearErrors() {
    globalErrorEl.textContent = "";
    globalErrorEl.classList.remove("visible");

    document
      .querySelectorAll(".error-message")
      .forEach((el) => (el.textContent = ""));
  }

  function setFieldError(fieldName, message) {
    const el = document.querySelector(
      `.error-message[data-error-for="${fieldName}"]`
    );
    if (el) {
      el.textContent = message || "";
    }
  }

  function showGlobalError(message) {
    globalErrorEl.textContent = message;
    globalErrorEl.classList.add("visible");
  }

  function clientValidate(formData) {
    const errors = {};

    Object.keys(ranges).forEach((field) => {
      const raw = (formData[field] ?? "").toString().trim();
      const meta = ranges[field];

      if (!raw) {
        errors[field] = "This field is required.";
        return;
      }

      const value = Number(raw);
      if (Number.isNaN(value)) {
        errors[field] = "Value must be a number.";
        return;
      }

      if (value < meta.min || value > meta.max) {
        errors[field] = `Value must be between ${meta.min} and ${meta.max}.`;
      }
    });

    return errors;
  }

  function resetAqiClasses() {
    summaryCategory.classList.remove(...AQI_CLASS_NAMES);
    adviceCard.classList.remove(...AQI_CLASS_NAMES);
  }

  function renderResultsSummary(score, category, advice) {
    resetAqiClasses();

    if (typeof score !== "number" || !Number.isFinite(score)) {
      resultsSummary.hidden = true;
      adviceCard.hidden = true;
      adviceText.textContent = "";
      return;
    }
    summaryAqi.textContent = score.toFixed(2);
    summaryCategory.textContent = category || "—";
    resultsSummary.hidden = false;

    if (category && CATEGORY_CLASS_MAP[category]) {
      const cls = CATEGORY_CLASS_MAP[category];
      summaryCategory.classList.add(cls);
      adviceCard.classList.add(cls);
    }

    if (advice) {
      const iconMap = {
        "Good": "✅",
        "Satisfactory": "ℹ️",
        "Moderate": "⚠️",
        "Poor": "⚠️",
        "Very Poor": "🚫",
        "Severe": "🚨",
      };
      
      adviceText.textContent = `${iconMap[category] || ""} ${advice}`;
      
      adviceCard.hidden = false;
    } else {
      adviceText.textContent = "";
      adviceCard.hidden = true;
    }
  }

  function renderResultsTable(mostPolluted) {
    resultsBody.innerHTML = "";

    if (!mostPolluted || mostPolluted.length === 0) {
      resultsContainer.hidden = true;
      resultsSubtitle.textContent =
        "No polluted cities data could be derived from the dataset.";
      return;
    }

    mostPolluted.forEach((item) => {
      const tr = document.createElement("tr");
      const tdCity = document.createElement("td");
      const tdScore = document.createElement("td");

      tdCity.textContent = item.city;
      tdScore.textContent = item.avgAqi;

      tr.appendChild(tdCity);
      tr.appendChild(tdScore);
      resultsBody.appendChild(tr);
    });

    resultsContainer.hidden = false;
    resultsSubtitle.textContent =
      "Showing the most polluted cities based on average AQI.";
  }

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearErrors();

    const formData = {
      pm25: form.pm25.value,
      pm10: form.pm10.value,
      co: form.co.value,
      no2: form.no2.value,
      so2: form.so2.value,
      o3: form.o3.value,
    };

    const errors = clientValidate(formData);
    if (Object.keys(errors).length > 0) {
      Object.entries(errors).forEach(([field, message]) =>
        setFieldError(field, message)
      );
      showGlobalError("Please fix the highlighted fields.");
      renderResultsSummary(NaN, "", "");
      renderResultsTable([]);
      return;
    }

    try {
      const response = await fetch("/api/pollution", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        if (data.errors) {
          Object.entries(data.errors).forEach(([field, message]) =>
            setFieldError(field, message)
          );
          showGlobalError(data.message || "Validation failed on server.");
        } else {
          showGlobalError(data.message || "Server returned an error.");
        }
        renderResultsSummary(NaN, "", "");
        renderResultsTable([]);
        return;
      }

      renderResultsSummary(
        data.pollutionScore,
        data.category,
        data.advice || ""
      );
      renderResultsTable(data.mostPolluted || []);
    } catch (err) {
      console.error(err);
      showGlobalError(
        "Unable to contact the server. Please check your connection and try again."
      );
      renderResultsSummary(NaN, "", "");
      renderResultsTable([]);
    }
  });
})();

