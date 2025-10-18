export function formatNumber(value: number): string {
  return new Intl.NumberFormat("ru-RU").format(value)
}

export function formatCompactNumber(value: number): string {
  return new Intl.NumberFormat("ru-RU", {
    notation: "compact",
    compactDisplay: "short",
  }).format(value)
}
