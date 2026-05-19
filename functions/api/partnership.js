// Cloudflare Pages Function: /api/partnership
// 제휴·광고 문의 양식 -> 텔레그램 봇 알림 (사장1, 사장2)
//
// 필요한 환경변수 (Cloudflare Pages → Settings → Environment variables)
//   - TELEGRAM_BOT_TOKEN_1   사장1 봇 토큰
//   - TELEGRAM_CHAT_ID_1     사장1 채팅 ID
//   - TELEGRAM_BOT_TOKEN_2   사장2 봇 토큰 (한 봇이면 TOKEN_1과 동일하게 설정)
//   - TELEGRAM_CHAT_ID_2     사장2 채팅 ID
//
// 응답: { ok: true, delivered: N } 또는 { ok: false, error: "..." }

const ALLOWED_TYPES = ["일반 광고", "지역 독점", "배너 광고", "제휴·입점", "관리사 협력", "기타"];

export async function onRequestPost({ request, env }) {
  try {
    const ct = request.headers.get("Content-Type") || "";
    if (!ct.includes("application/json")) {
      return json({ ok: false, error: "Content-Type must be application/json" }, 400);
    }

    let data;
    try { data = await request.json(); }
    catch { return json({ ok: false, error: "Invalid JSON" }, 400); }

    const { inquiryType, name, phone, region, message, hp, ts } = data || {};

    // 허니팟: 봇은 hp 필드를 채울 가능성이 높음
    if (typeof hp === "string" && hp.trim() !== "") {
      return json({ ok: true, delivered: 0, skipped: true });
    }

    // 봇 사용자 차단: 너무 빨리 제출되면 (1초 미만) 거절
    if (ts && typeof ts === "number") {
      const elapsed = Date.now() - ts;
      if (elapsed < 1500) {
        return json({ ok: false, error: "잠시 후 다시 시도해 주세요." }, 429);
      }
    }

    // 필수 입력 검증
    const errors = [];
    if (!inquiryType || !ALLOWED_TYPES.includes(inquiryType)) errors.push("광고문의 유형");
    if (!isStr(name, 1, 50)) errors.push("성명");
    if (!isPhone(phone)) errors.push("전화번호");
    if (!isStr(region, 1, 100)) errors.push("광고 지역");
    if (!isStr(message, 10, 2000)) errors.push("문의사항 (최소 10자)");

    if (errors.length) {
      return json({ ok: false, error: `입력 확인 필요: ${errors.join(", ")}` }, 400);
    }

    const ip = request.headers.get("CF-Connecting-IP") || "unknown";
    const ua = (request.headers.get("User-Agent") || "unknown").slice(0, 80);
    const text = formatTelegramMessage({ inquiryType, name, phone, region, message, ip, ua });

    // 두 수신처로 동시 전송
    const recipients = [
      { token: env.TELEGRAM_BOT_TOKEN_1, chat: env.TELEGRAM_CHAT_ID_1, label: "사장1" },
      { token: env.TELEGRAM_BOT_TOKEN_2, chat: env.TELEGRAM_CHAT_ID_2, label: "사장2" },
    ];

    // 환경변수 누락 사전 점검
    const envStatus = recipients.map(r => ({
      label: r.label,
      hasToken: !!r.token,
      hasChat: !!r.chat,
    }));
    const anyConfigured = envStatus.some(e => e.hasToken && e.hasChat);
    if (!anyConfigured) {
      console.error("Telegram env not configured:", envStatus);
      return json({
        ok: false,
        error: "운영팀 알림 채널이 설정되지 않았습니다. Cloudflare Pages 환경변수(TELEGRAM_BOT_TOKEN_1·TELEGRAM_CHAT_ID_1)를 확인해 주세요.",
        debug: envStatus,
      }, 500);
    }

    const results = await Promise.allSettled(
      recipients.map(r => sendTelegram(r.token, r.chat, text))
    );

    const delivered = results.filter(
      r => r.status === "fulfilled" && r.value && r.value.ok
    ).length;

    if (delivered === 0) {
      const debug = results.map((r, i) => {
        if (r.status === "fulfilled") {
          const v = r.value || {};
          return {
            label: recipients[i].label,
            configured: envStatus[i].hasToken && envStatus[i].hasChat,
            ok: v.ok,
            error_code: v.error_code,
            description: (v.description || "").slice(0, 200),
            skipped: v.skipped,
          };
        }
        return { label: recipients[i].label, rejected: String(r.reason).slice(0, 200) };
      });
      console.error("Telegram delivery failed:", JSON.stringify(debug));
      return json({
        ok: false,
        error: "텔레그램 전송 실패. 토큰·채팅ID·봇 시작(/start) 여부를 확인해 주세요.",
        debug,
      }, 502);
    }

    return json({ ok: true, delivered });
  } catch (e) {
    console.error("partnership handler error:", e && e.message);
    return json({ ok: false, error: "서버 오류" }, 500);
  }
}

export function onRequestOptions() {
  return new Response(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
      "Access-Control-Max-Age": "86400",
    },
  });
}

// 그 외 메서드는 405
export function onRequest({ request }) {
  return json({ ok: false, error: `Method ${request.method} not allowed` }, 405);
}

// ---------- helpers ----------

function isStr(v, min, max) {
  return typeof v === "string" && v.trim().length >= min && v.trim().length <= max;
}

function isPhone(v) {
  if (typeof v !== "string") return false;
  const digits = v.replace(/[^0-9]/g, "");
  return digits.length >= 9 && digits.length <= 15;
}

function escapeHtml(s) {
  return String(s)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function formatTelegramMessage({ inquiryType, name, phone, region, message, ip, ua }) {
  const now = new Date().toLocaleString("ko-KR", {
    timeZone: "Asia/Seoul",
    year: "numeric", month: "2-digit", day: "2-digit",
    hour: "2-digit", minute: "2-digit",
  });
  return [
    "🔔 <b>바로GO · 제휴/광고 문의 접수</b>",
    "",
    `📌 <b>유형</b>      : ${escapeHtml(inquiryType)}`,
    `👤 <b>성명</b>      : ${escapeHtml(name)}`,
    `📞 <b>전화</b>      : ${escapeHtml(phone)}`,
    `📍 <b>광고 지역</b> : ${escapeHtml(region)}`,
    "",
    "📝 <b>문의사항</b>",
    escapeHtml(message),
    "",
    `<i>${now} · IP ${escapeHtml(ip)}</i>`,
  ].join("\n");
}

async function sendTelegram(token, chatId, text) {
  if (!token || !chatId) {
    return { ok: false, skipped: true, reason: "missing env" };
  }
  const url = `https://api.telegram.org/bot${token}/sendMessage`;
  const r = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      chat_id: chatId,
      text,
      parse_mode: "HTML",
      disable_web_page_preview: true,
    }),
  });
  return r.json();
}

function json(body, status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      "Content-Type": "application/json; charset=utf-8",
      "Access-Control-Allow-Origin": "*",
      "Cache-Control": "no-store",
    },
  });
}
