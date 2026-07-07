const AVATAR_COLORS = ['#1A5E9D', '#2874A6', '#7D3C98', '#B03A2E', '#1E8449', '#B9770E', '#5D6D7E']

export function generateAvatarUrl(firstName, lastName, email) {
  let firstInitial = ''
  let lastInitial = ''
  if (firstName && firstName.length > 0) {
    firstInitial = firstName[0]
  }
  if (lastName && lastName.length > 0) {
    lastInitial = lastName[0]
  }
  let initials = (firstInitial + lastInitial).toUpperCase()
  if (!initials) {
    initials = (email && email[0] ? email[0] : '?').toUpperCase()
  }

  // Deterministic color: same user always gets the same background
  const seed = `${firstName || ''}${lastName || ''}${email || ''}`
  let hash = 0
  for (let i = 0; i < seed.length; i++) {
    hash = (hash * 31 + seed.charCodeAt(i)) % 100000
  }
  const background = AVATAR_COLORS[hash % AVATAR_COLORS.length]

  const svg =
    `<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128">` +
    `<rect width="128" height="128" fill="${background}"/>` +
    `<text x="64" y="64" fill="#fff" font-family="Arial, sans-serif" font-size="52" ` +
    `font-weight="bold" text-anchor="middle" dominant-baseline="central">${initials}</text>` +
    `</svg>`

  return `data:image/svg+xml,${encodeURIComponent(svg)}`
}
