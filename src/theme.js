// One place for the look. Fresh green, soft cream background, amber accent.
export const ui = {
  page: 'min-h-screen bg-emerald-50/40 text-stone-800 antialiased',
  container: 'mx-auto w-full max-w-5xl px-4 sm:px-6',
  card: 'rounded-3xl border border-emerald-100 bg-white p-4 shadow-sm transition hover:shadow-md hover:-translate-y-0.5',
  btn: 'rounded-full bg-emerald-600 px-5 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-emerald-700 active:scale-95 disabled:cursor-not-allowed disabled:opacity-60',
  btnGhost: 'rounded-full border border-emerald-200 bg-white px-5 py-2 text-sm font-semibold text-emerald-800 transition hover:bg-emerald-50',
  btnDanger: 'rounded-full border border-red-200 bg-red-50 px-4 py-1.5 text-sm font-semibold text-red-700 transition hover:bg-red-100',
  heading: 'text-lg font-extrabold tracking-tight text-emerald-900',
  muted: 'text-sm text-stone-500',
  hero: 'rounded-3xl bg-gradient-to-br from-emerald-600 to-emerald-500 p-6 text-white shadow-md sm:p-8',
  price: 'text-lg font-extrabold text-emerald-700',
}

export const statusStyle = {
  PLACED: 'bg-amber-100 text-amber-800',
  CONFIRMED: 'bg-sky-100 text-sky-800',
  PACKED: 'bg-indigo-100 text-indigo-800',
  OUT_FOR_DELIVERY: 'bg-purple-100 text-purple-800',
  DELIVERED: 'bg-emerald-100 text-emerald-800',
  CANCELLED: 'bg-stone-200 text-stone-600',
}

// Emoji shown on the product card by category (falls back to a basket)
export const categoryEmoji = {
  Groceries: '🛒',
  Dairy: '🥛',
  Fruits: '🍎',
  Vegetables: '🥦',
  Bakery: '🍞',
  Home: '🧼',
  Snacks: '🍪',
  Beverages: '🥤',
}