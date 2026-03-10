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
    bookingForm.addEventListener("submit", (e) => {
      e.preventDefault();

      const formData = new FormData(bookingForm);
      const name = formData.get("name");
      const phone = formData.get("phone");
      const interest = formData.get("interest");
      const date = formData.get("date");
      const people = formData.get("people");
      const comment = formData.get("comment");

      const lines = [];
      if (interest) {
        lines.push(`Формат: ${interest}`);
      }
      if (date) {
        lines.push(`Дата: ${date}`);
      }
      if (people) {
        lines.push(`Количество человек: ${people}`);
      }
      if (comment) {
        lines.push(`Комментарий: ${comment}`);
      }

      const message =
        `Здравствуйте! Хочу записаться на Русское Ранчо.\n` +
        `Имя: ${name || ""}\n` +
        `Телефон: ${phone || ""}\n` +
        (lines.length ? `\n${lines.join("\n")}` : "");

      const encoded = encodeURIComponent(message);
      const phoneForWhatsApp = ""; // сюда можно подставить номер без +

      if (phoneForWhatsApp) {
        const url = `https://wa.me/${phoneForWhatsApp}?text=${encoded}`;
        window.open(url, "_blank");
      } else {
        alert("Заявка сформирована.\n\n" + message + "\n\nСкопируйте текст и отправьте его нам в удобный мессенджер.");
      }
    });
  }
});

