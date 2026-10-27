export default function Cart({ cart, onCheckout, onBack }) {
  
    const total = cart.reduce((sum, line) => sum + line.price * line.quantity, 0);
  

  if (cart.length === 0) {
  return (
    <div className="p-6">
      <p>Your cart is empty</p>
      <button onClick={onBack}>Back</button>
    </div>
  );
}
  return (
    <div className="p-6">
        {cart.map(line => (
            <div key={line.store_id + '-' + line.product_id}>
                {line.name}: {line.quantity} x {line.price} = {line.price * line.quantity}
            </div>
        ))}
        
        <p>Total: {total.toFixed(2)}</p>
        <button onClick={onCheckout}>Place order</button>
        <button onClick={onBack}>Back</button>

    </div>
  );
}