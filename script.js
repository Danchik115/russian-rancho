document.addEventListener("DOMContentLoaded", () => {
  const header = document.querySelector(".site-header");
  const navToggle = document.querySelector(".nav-toggle");
  const yearEl = document.getElementById("year");

  if (yearEl) {
    yearEl.textContent = new Date().getFullYear().toString();
  }

  if (navToggle && header) {
    navToggle.addEventListener("click", () => {
      header.classList.toggle("nav-open");
    });
  }

  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", (e) => {
      const targetId = anchor.getAttribute("href");
      if (!targetId || targetId === "#") return;

      const el = document.querySelector(targetId);
      if (!el) return;

      e.preventDefault();
      const navHeight = document.querySelector(".site-header")?.offsetHeight || 0;
      const rect = el.getBoundingClientRect();
      const offset = window.scrollY + rect.top - navHeight - 12;

      window.scrollTo({
        top: offset,
        behavior: "smooth",
      });

      header?.classList.remove("nav-open");
    });
  });

  const bookingForm = document.querySelector(".booking-form");
  if (bookingForm) {
    bookingForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const formData = new FormData(bookingForm);
      const body = {
        name: formData.get("name") || "",
        phone: formData.get("phone") || "",
        interest: formData.get("interest") || "",
        date: formData.get("date") || "",
        people: formData.get("people") || "",
        comment: formData.get("comment") || "",
      };

      const submitBtn = bookingForm.querySelector('button[type="submit"]');
      const originalText = submitBtn?.textContent;
      if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.textContent = "Отправка…";
      }

      const apiBase = window.FORM_API_URL || "";
      const apiUrl = apiBase + "/api/telegram";

      try {
        const res = await fetch(apiUrl, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        });
        const data = await res.json().catch(() => ({}));

        if (res.ok && data.ok) {
          alert("Спасибо! Заявка отправлена. Мы свяжемся с вами в ближайшее время.");
          bookingForm.reset();
        } else {
          throw new Error(data.error || "Ошибка отправки");
        }
      } catch (err) {
        const message =
          "Здравствуйте! Хочу записаться на Русское Ранчо.\n" +
          "Имя: " + (body.name || "—") + "\n" +
          "Телефон: " + (body.phone || "—") + "\n" +
          (body.interest ? "Интересует: " + body.interest + "\n" : "") +
          (body.date ? "Дата: " + body.date + "\n" : "") +
          (body.people ? "Человек: " + body.people + "\n" : "") +
          (body.comment ? "Комментарий: " + body.comment : "");
        alert("Не удалось отправить заявку автоматически.\n\nСкопируйте текст ниже и отправьте нам в Telegram (@zoloto_ha_shee) или по телефону:\n\n" + message);
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = originalText || "Отправить заявку";
        }
      }
    });
  }
});

