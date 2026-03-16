document.addEventListener("DOMContentLoaded", () => {
  const TELEGRAM_USERNAME = "@Zoloto_Ha_shee";
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

  // Модальное окно подарочного сертификата
  const openCertificateModal = () => {
    const modal = document.getElementById("certificate-modal");
    if (modal) {
      modal.classList.add("is-open");
      modal.setAttribute("aria-hidden", "false");
      document.body.style.overflow = "hidden";
    }
  };
  const closeCertificateModal = () => {
    const modal = document.getElementById("certificate-modal");
    if (modal) {
      modal.classList.remove("is-open");
      modal.setAttribute("aria-hidden", "true");
      document.body.style.overflow = "";
    }
  };
  document.querySelectorAll("[data-open=\"certificate-modal\"]").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.preventDefault();
      openCertificateModal();
    });
  });
  document.querySelectorAll("[data-close=\"certificate-modal\"]").forEach((el) => {
    el.addEventListener("click", closeCertificateModal);
  });
  document.getElementById("certificate-modal")?.addEventListener("click", (e) => {
    if (e.target.id === "certificate-modal" || e.target.classList.contains("modal-backdrop")) {
      closeCertificateModal();
    }
  });
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      const modal = document.getElementById("certificate-modal");
      if (modal?.classList.contains("is-open")) closeCertificateModal();
    }
  });

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
        alert(`Не удалось отправить заявку автоматически.\n\nСкопируйте текст ниже и отправьте нам в Telegram (${TELEGRAM_USERNAME}) или по телефону:\n\n` + message);
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = originalText || "Отправить заявку";
        }
      }
    });
  }

  const certificateForm = document.getElementById("certificate-form");
  if (certificateForm) {
    certificateForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const formData = new FormData(certificateForm);
      const nominal = formData.get("nominal") || "";
      const recipient = formData.get("recipient") || "";
      const wish = formData.get("wish") || "";
      const comment = formData.get("comment") || "";
      const parts = [];
      if (nominal) parts.push("Номинал: " + (nominal === "other" ? "другая сумма" : nominal + " ₽"));
      if (recipient) parts.push("Получатель: " + recipient);
      if (wish) parts.push("Пожелание: " + wish);
      if (comment) parts.push("Комментарий: " + comment);
      const body = {
        name: formData.get("name") || "",
        phone: formData.get("phone") || "",
        interest: "certificate",
        date: "",
        people: "",
        comment: parts.join("\n") || "Заявка на подарочный сертификат",
      };

      const submitBtn = certificateForm.querySelector('button[type="submit"]');
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
          alert("Спасибо! Заявка на сертификат отправлена. Мы свяжемся с вами для оформления и оплаты.");
          certificateForm.reset();
          closeCertificateModal();
        } else {
          throw new Error(data.error || "Ошибка отправки");
        }
      } catch (err) {
        const message =
          "Здравствуйте! Хочу оформить подарочный сертификат Русское Ранчо.\n" +
          "Имя: " + (body.name || "—") + "\n" +
          "Телефон: " + (body.phone || "—") + "\n" + (body.comment ? body.comment : "");
        alert(`Не удалось отправить заявку автоматически.\n\nСкопируйте текст ниже и отправьте нам в Telegram (${TELEGRAM_USERNAME}) или по телефону:\n\n` + message);
      } finally {
        if (submitBtn) {
          submitBtn.disabled = false;
          submitBtn.textContent = originalText || "Отправить заявку на сертификат";
        }
      }
    });
  }
});

