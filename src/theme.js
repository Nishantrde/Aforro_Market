// One place for the look. Change the colours here and the whole app follows.
export const ui = {
  page: 'min-h-screen bg-stone-50 text-stone-800',
  container: 'mx-auto w-full max-w-5xl px-4 sm:px-6',
  card: 'rounded-2xl border border-stone-200 bg-white p-4 shadow-sm',
  btn: 'rounded-xl bg-green-700 px-4 py-2 text-sm font-semibold text-white transition hover:bg-green-800 active:scale-[0.98]',
  btnGhost: 'rounded-xl border border-stone-300 bg-white px-4 py-2 text-sm font-semibold text-stone-700 transition hover:bg-stone-100',
  btnDanger: 'rounded-xl border border-red-200 bg-red-50 px-3 py-1.5 text-sm font-semibold text-red-700 transition hover:bg-red-100',
  heading: 'text-lg font-bold text-stone-900',
  muted: 'text-sm text-stone-500',
}

export const statusStyle = {
  PLACED: 'bg-amber-100 text-amber-800',
  CONFIRMED: 'bg-blue-100 text-blue-800',
  PACKED: 'bg-indigo-100 text-indigo-800',
  OUT_FOR_DELIVERY: 'bg-purple-100 text-purple-800',
  DELIVERED: 'bg-green-100 text-green-800',
  CANCELLED: 'bg-stone-200 text-stone-600',
}