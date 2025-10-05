import svgPaths from "../../imports/svg-it8vuprc7e";
import imgImage7 from "figma:asset/1281c56fca7983de4a0dc2a33d981cd2d80e24ff.png";
import imgImage8 from "figma:asset/7bf2958218ee8599510db937926b1c0f7cd5f07d.png";
import imgImage9 from "figma:asset/91d0f2546f3ddf10b36364d263b479db2b9c09c2.png";

// Store checkbox with checkmark
function StoreCheckbox() {
  return (
    <div className="relative w-4 h-4 bg-[var(--brand-primary)] rounded flex items-center justify-center">
      <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
        <path 
          d="M2 5L4 7L8 3" 
          stroke="white" 
          strokeWidth="1.5" 
          strokeLinecap="round" 
          strokeLinejoin="round"
        />
      </svg>
    </div>
  );
}

// Store header with delivery info
function StoreHeader() {
  return (
    <div className="space-y-2 pb-3 border-b border-[var(--border)]">
      <div className="flex items-center gap-3">
        <StoreCheckbox />
        <h3 className="text-body-emphasis text-[var(--text-primary)]">Магазин Cvety.kz</h3>
      </div>
      <p className="text-caption text-[var(--text-secondary)]">
        Доставит сегодня к 15:00 - 1 500 ₸
      </p>
    </div>
  );
}

// Product quantity controls
function QuantityControls({ quantity = 1 }: { quantity?: number }) {
  return (
    <div className="flex items-center gap-3">
      <button className="w-8 h-8 rounded-full border border-[var(--border)] flex items-center justify-center hover:bg-[var(--background-secondary)] transition-colors">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
          <path d="M3 6H9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
      </button>
      <span className="text-body-emphasis text-[var(--text-primary)] min-w-[2rem] text-center">
        {quantity}
      </span>
      <button className="w-8 h-8 rounded-full border border-[var(--border)] flex items-center justify-center hover:bg-[var(--background-secondary)] transition-colors">
        <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
          <path d="M6 3V9M3 6H9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
        </svg>
      </button>
    </div>
  );
}

// Individual cart item
function CartItem({ 
  image, 
  title, 
  size, 
  price, 
  quantity = 1 
}: { 
  image: string; 
  title: string; 
  size: string; 
  price: string; 
  quantity?: number; 
}) {
  return (
    <div className="flex gap-3 p-4 bg-white rounded-[var(--radius-md)]">
      <div className="w-16 h-16 bg-[var(--background-secondary)] rounded-[var(--radius-md)] overflow-hidden flex-shrink-0">
        <img 
          src={image} 
          alt={title}
          className="w-full h-full object-cover"
        />
      </div>
      
      <div className="flex-1 min-w-0">
        <h4 className="text-body text-[var(--text-primary)] line-clamp-1 mb-1">
          {title}
        </h4>
        <div className="flex items-center gap-1 mb-2">
          <span className="text-caption text-[var(--text-secondary)]">{size}</span>
          <span className="text-caption text-[var(--text-secondary)]">\\</span>
          <span className="text-price text-[var(--brand-primary)]">{price}</span>
        </div>
        <QuantityControls quantity={quantity} />
      </div>
      
      <button className="self-start p-1 hover:bg-[var(--background-secondary)] rounded transition-colors">
        <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
          <path 
            d="M12 4L4 12M4 4L12 12" 
            stroke="var(--text-secondary)" 
            strokeWidth="1.5" 
            strokeLinecap="round"
          />
        </svg>
      </button>
    </div>
  );
}

// Main cart items section
export function CartMobileItemsImproved() {
  const cartItems = [
    {
      id: 1,
      image: imgImage7,
      title: "Аромобукет",
      size: "L",
      price: "170 000 ₸",
      quantity: 1
    },
    {
      id: 2,
      image: imgImage8,
      title: "Букет сухоцветов",
      size: "15 шт",
      price: "16 000 ₸",
      quantity: 1
    },
    {
      id: 3,
      image: imgImage9,
      title: "Букет сухоцветов",
      size: "1 уп",
      price: "7 000 ₸",
      quantity: 1
    }
  ];

  return (
    <div className="space-y-[var(--spacing-4)]">
      <h2 className="text-headline text-[var(--text-primary)]">В корзине</h2>
      
      <div className="space-y-[var(--spacing-4)]">
        <StoreHeader />
        
        <div className="space-y-3">
          {cartItems.map((item) => (
            <CartItem
              key={item.id}
              image={item.image}
              title={item.title}
              size={item.size}
              price={item.price}
              quantity={item.quantity}
            />
          ))}
        </div>
      </div>
    </div>
  );
}