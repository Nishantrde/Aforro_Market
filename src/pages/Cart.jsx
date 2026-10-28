import { ui } from '../theme';

export default function Cart({ cart, onCheckout, onBack }) {
  const total = cart.reduce((sum, line) => sum + line.price * line.quantity, 0);

  if (cart.length === 0) {
    return (
      <div className={ui.card + ' mx-auto max-w-md space-y-4 text-center'}>
        <p className={ui.heading}>Your cart is empty</p>
        <p className={ui.muted}>Add something fresh from the store.</p>
        <button onClick={onBack} className={ui.btn}>Start shopping</button>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-xl space-y-4">
      <h1 className="text-xl font-bold text-stone-900">Your cart</h1>
      <div className={ui.card + ' divide-y divide-stone-100'}>
        {cart.map(line => (
          <div key={line.store_id + '-' + line.product_id} className="flex items-center justify-between py-3 first:pt-0 last:pb-0">
            <div>
              <p className="font-semibold">{line.name}</p>
              <p className={ui.muted}>{line.quantity} × ₹{line.price}</p>
            </div>
            <p className="font-semibold">₹{(line.price * line.quantity).toFixed(2)}</p>
          </div>
        ))}
      </div>
      <div className={ui.card + ' flex items-center justify-between'}>
        <span className="font-semibold">Total</span>
        <span className="text-xl font-bold text-green-700">₹{total.toFixed(2)}</span>
      </div>
      <div className="flex gap-3">
        <button onClick={onBack} className={ui.btnGhost}>Back</button>
        <button onClick={onCheckout} className={ui.btn + ' flex-1'}>Place order</button>
      </div>
    </div>
  );
}