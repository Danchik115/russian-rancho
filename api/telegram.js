/**
 * Serverless-функция Vercel: приём заявки с сайта и отправка в Telegram.
 *
 * Настройка:
 * 1. Создайте бота в Telegram: @BotFather → /newbot → получите токен.
 * 2. Узнайте свой chat_id: напишите боту @userinfobot или откройте
 *    https://api.telegram.org/bot<ВАШ_ТОКЕН>/getUpdates после сообщения боту.
 * 3. В Vercel: Project → Settings → Environment Variables:
 *    TELEGRAM_BOT_TOKEN = токен бота
 *    TELEGRAM_CHAT_ID = ваш chat_id (число или строка)
 */

const TELEGRAM_API = "https://api.telegram.org/bot";

const INTEREST_LABELS = {
  family: "Семейные программы",
  kids: "Форматы для детей",
  couples: "Свидания и пикники",
  groups: "Групповые выезды",
  events: "Мероприятия и афиша",
  nedvizhimost: "Тепло и уют для вас (домики, беседки)",
  certificate: "Подарочный сертификат",
  prices: "Цены и условия",
  other: "Другое",
};

function buildMessage(body) {
  const { name, phone, interest, date, people, comment } = body;
  const interestLabel = interest ? INTEREST_LABELS[interest] || interest : "";
  const lines = ["🟢 Новая заявка с сайта Русское Ранчо", "", `👤 Имя: ${name || "—"}`, `📞 Телефон: ${phone || "—"}`];
  if (interestLabel) lines.push(`📋 Интересует: ${interestLabel}`);
  if (date) lines.push(`📅 Дата: ${date}`);
  if (people) lines.push(`👥 Человек: ${people}`);
  if (comment) lines.push("", "💬 Комментарий:", comment);
  return lines.join("\n");
}

export default async function handler(req, res) {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader("Access-Control-Allow-Methods", "POST, OPTIONS");
  res.setHeader("Access-Control-Allow-Headers", "Content-Type");
  if (req.method === "OPTIONS") return res.status(204).end();
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ error: "Method not allowed" });
  }

  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;

  if (!token || !chatId) {
    console.error("TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID not set");
    return res.status(500).json({ error: "Server not configured for Telegram" });
  }

  try {
    const body = typeof req.body === "string" ? JSON.parse(req.body) : req.body;
    const text = buildMessage(body);
    const url = `${TELEGRAM_API}${token}/sendMessage`;
    const response = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        chat_id: chatId,
        text,
        disable_web_page_preview: true,
      }),
    });

    const data = await response.json().catch(() => ({}));
    if (!data.ok) {
      console.error("Telegram API error:", data);
      return res.status(500).json({ error: "Failed to send to Telegram", details: data.description });
    }
    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ error: "Server error" });
  }
}
