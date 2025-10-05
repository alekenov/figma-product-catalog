import svgPaths from "../../imports/svg-r3kfi35k7m";
import imgImage531 from "figma:asset/a7b66a9f71c03462f7b4ffbe86d031aee90babdf.png";
import imgImage6 from "figma:asset/b8d3f09a1bf647aed7795e7ca80a8c18925e873e.png";
import imgImage7 from "figma:asset/03d2fa89f07ca5c5133236fd963ee88eb0418895.png";
import imgImage8 from "figma:asset/e7d703d0a477201a273d04856de978ed62cb2fe0.png";
import imgComponent1 from "figma:asset/7ed1f1fd36b21e57da96ec69210182925b62b8fd.png";

// Heart icon for favorites
function HeartIcon() {
  return (
    <div className="w-5 h-5">
      <svg className="block size-full" fill="none" viewBox="0 0 9 8">
        <path d={svgPaths.p26ebaac0} fill="white" />
      </svg>
    </div>
  );
}

// Individual product image with favorite button
function ProductImage({ src, alt, hasFavorite = false }: { src: string; alt: string; hasFavorite?: boolean }) {
  return (
    <div className="relative aspect-square bg-[var(--background-secondary)] rounded-[var(--radius-md)] overflow-hidden">
      <img 
        alt={alt} 
        className="w-full h-full object-cover" 
        src={src} 
      />
      
      {hasFavorite && (
        <button className="absolute top-2 right-2 w-8 h-8 bg-black/20 backdrop-blur-sm rounded-full flex items-center justify-center hover:bg-black/30 transition-colors">
          <HeartIcon />
        </button>
      )}
    </div>
  );
}

// Main product image section
function MainProductImage() {
  return (
    <div className="mb-[var(--spacing-4)]">
      <ProductImage 
        src={imgImage531} 
        alt="Основное изображение букета роз" 
        hasFavorite={true}
      />
    </div>
  );
}

// Product image grid
function ProductImageGrid() {
  const images = [
    { src: imgImage6, alt: "Розовые розы вид 1" },
    { src: imgImage7, alt: "Розовые розы вид 2" },
    { src: imgImage8, alt: "Розовые розы вид 3" },
    { src: imgComponent1, alt: "Розовые розы вид 4" },
  ];

  return (
    <div className="grid grid-cols-2 gap-[var(--spacing-3)]">
      {images.map((image, index) => (
        <ProductImage 
          key={index}
          src={image.src} 
          alt={image.alt}
          hasFavorite={index === 1} // Favorite on second image
        />
      ))}
    </div>
  );
}

// Image navigation dots
function ImageDots({ total = 5, active = 0 }: { total?: number; active?: number }) {
  return (
    <div className="flex items-center justify-center gap-2 mt-[var(--spacing-4)]">
      {Array.from({ length: total }).map((_, index) => (
        <button
          key={index}
          className={`w-2 h-2 rounded-full transition-colors ${
            index === active 
              ? 'bg-[var(--brand-primary)]' 
              : 'bg-[var(--neutral-300)] hover:bg-[var(--neutral-400)]'
          }`}
          aria-label={`Перейти к изображению ${index + 1}`}
        />
      ))}
    </div>
  );
}

// Product details section
function ProductBasicInfo() {
  return (
    <div className="mt-[var(--spacing-6)] p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
      <div className="mb-[var(--spacing-4)]">
        <h1 className="font-semibold text-[var(--text-primary)] mb-2">
          Букет "Розовые мечты"
        </h1>
        <p className="text-[var(--text-secondary)] text-sm leading-relaxed">
          Нежный букет из свежих розовых роз, идеально подходящий для романтических моментов и особых случаев.
        </p>
      </div>
      
      <div className="flex items-center justify-between">
        <div className="flex items-baseline gap-2">
          <span className="text-2xl font-bold text-[var(--text-primary)]">7 900 ₸</span>
          <span className="text-sm text-[var(--text-secondary)] line-through">9 900 ₸</span>
        </div>
        
        <div className="flex items-center gap-1 text-sm">
          <div className="w-4 h-4 text-[var(--brand-primary)]">
            <svg className="block size-full" fill="none" viewBox="0 0 16 16">
              <path 
                d="M8 1L9.5 5.5H14L10.5 8.5L12 13L8 10L4 13L5.5 8.5L2 5.5H6.5L8 1Z" 
                fill="currentColor"
              />
            </svg>
          </div>
          <span className="font-medium text-[var(--text-primary)]">4.8</span>
          <span className="text-[var(--text-secondary)]">(24)</span>
        </div>
      </div>
    </div>
  );
}

// Size and quantity selector
function ProductOptions() {
  const sizes = [
    { id: 'small', label: 'Маленький', price: '7 900 ₸', selected: false },
    { id: 'medium', label: 'Средний', price: '9 900 ₸', selected: true },
    { id: 'large', label: 'Большой', price: '12 900 ₸', selected: false },
  ];

  return (
    <div className="mt-[var(--spacing-4)] p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)]">
      <h3 className="font-medium text-[var(--text-primary)] mb-3">Размер букета</h3>
      
      <div className="space-y-2 mb-[var(--spacing-4)]">
        {sizes.map((size) => (
          <button
            key={size.id}
            className={`relative w-full p-3 rounded-2xl border transition-all text-left ${
              size.selected 
                ? 'bg-white border-[var(--border)] text-[var(--text-primary)]'
                : 'bg-white border-[var(--border)] text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
            }`}
          >
            <div className="flex items-center justify-between">
              <span className="font-medium">{size.label}</span>
              <span className="font-semibold">{size.price}</span>
            </div>
            
            {size.selected && (
              <div className="absolute -top-1 -right-1 w-4 h-4 bg-[var(--brand-primary)] rounded-full flex items-center justify-center">
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
            )}
          </button>
        ))}
      </div>

      <div className="flex items-center justify-between">
        <span className="font-medium text-[var(--text-primary)]">Количество</span>
        <div className="flex items-center gap-3">
          <button className="w-8 h-8 rounded-full border border-[var(--border)] flex items-center justify-center hover:bg-[var(--background-secondary)] transition-colors">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M3 6H9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </button>
          <span className="font-medium text-[var(--text-primary)] min-w-[2rem] text-center">1</span>
          <button className="w-8 h-8 rounded-full border border-[var(--border)] flex items-center justify-center hover:bg-[var(--background-secondary)] transition-colors">
            <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
              <path d="M6 3V9M3 6H9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
}

// Main gallery component
export function ProductCardGallery() {
  return (
    <div className="p-[var(--spacing-4)] bg-[var(--background-secondary)]">
      <MainProductImage />
      <ProductImageGrid />
      <ImageDots />
      <ProductBasicInfo />
      <ProductOptions />
    </div>
  );
}