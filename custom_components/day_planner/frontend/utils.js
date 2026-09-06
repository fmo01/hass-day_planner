export function formatDate(date) {
  const year = date.getFullYear();

  const month = String(
    date.getMonth() + 1
  ).padStart(2, "0");

  const day = String(
    date.getDate()
  ).padStart(2, "0");

  return `${year}-${month}-${day}`;
}


export function formatTime(value) {
  if (!value) {
    return "";
  }

  return value.slice(0, 5);
}


export function timeToPercent(value) {
  if (!value) {
    return 0;
  }

  const [hours, minutes] =
    value.split(":").map(Number);

  const totalMinutes =
    (hours * 60) + minutes;

  return (
    totalMinutes /
    (24 * 60)
  ) * 100;
}

export function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}


export function dayTypeColor(dayType) {
  if (!dayType?.id) {
    return "var(--divider-color)";
  }

  const colors = [
    "#4f8cff",
    "#42a66f",
    "#d28a32",
    "#a06bdd",
    "#d05f73",
    "#3d9ca8",
    "#aa8a42",
    "#6f8299",
  ];

  let hash = 0;

  for (const char of dayType.id) {
    hash =
      ((hash << 5) - hash) +
      char.charCodeAt(0);

    hash |= 0;
  }

  return colors[
    Math.abs(hash) % colors.length
  ];
}
