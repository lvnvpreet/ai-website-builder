/**
 * Converts a time string (e.g., '1h', '7d', '15m') into seconds.
 * Supports 's' (seconds), 'm' (minutes), 'h' (hours), 'd' (days).
 * Returns NaN if the format is invalid.
 */
export function timeStringToSeconds(timeString: string): number {
  if (typeof timeString !== 'string') {
    return NaN;
  }
  const match = timeString.match(/^(\d+)([smhd])$/);
  if (!match) {
    return NaN;
  }

  const value = parseInt(match[1], 10);
  const unit = match[2];

  switch (unit) {
    case 's':
      return value;
    case 'm':
      return value * 60;
    case 'h':
      return value * 60 * 60;
    case 'd':
      return value * 60 * 60 * 24;
    default:
      return NaN;
  }
}
