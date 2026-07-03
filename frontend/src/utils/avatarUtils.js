export function generateAvatarUrl(firstName, lastName, email) {
  let firstInitial = ''
  let lastInitial = ''
  if (firstName && firstName.length > 0) {
    firstInitial = firstName[0]
  }
  if (lastName && lastName.length > 0) {
    lastInitial = lastName[0]
  }
  const initials = (firstInitial + lastInitial).toUpperCase()
  const fullName = (firstName + ' ' + lastName).trim()
  const displayName = initials || fullName || email
  return `https://ui-avatars.com/api/?name=${encodeURIComponent(displayName)}&background=random&color=fff&size=128`
}
