import { useState } from 'react';
import svgPaths from '../imports/svg-y2x5poxegy';

export type DeliveryMethod = 'delivery' | 'pickup';

interface DeliveryMethodSelectorProps {
  selectedMethod: DeliveryMethod;
  onMethodChange: (method: DeliveryMethod) => void;
}

function CheckboxRounder({ checked }: { checked: boolean }) {
  if (checked) {
    return (
      <div className="bg-[var(--brand-primary)] box-border flex items-center justify-center p-[2.667px] rounded-[30px] size-4 shrink-0">
        <div className="size-[10.667px]">
          <svg className="block size-full text-white" fill="none" preserveAspectRatio="none" viewBox="0 0 11 11">
            <path 
              d={svgPaths.p193a5f00} 
              stroke="currentColor" 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth="1.33333" 
            />
          </svg>
        </div>
      </div>
    );
  }

  return (
    <div className="border border-[#8f8f8f] border-solid rounded-[30px] size-4 shrink-0" />
  );
}

function DeliveryOption({ 
  title, 
  subtitle, 
  selected, 
  onClick 
}: { 
  title: string; 
  subtitle: string; 
  selected: boolean; 
  onClick: () => void; 
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`
        flex-1 bg-white rounded-[8px] border border-solid p-0 text-left transition-all
        ${selected 
          ? 'border-black' 
          : 'border-[#8f8f8f] hover:border-[var(--brand-primary)]'
        }
      `}
    >
      <div className="box-border flex flex-col gap-[2px] px-[8px] py-[12px] w-full">
        <div className="flex items-center justify-between w-full">
          <p className="text-body-emphasis text-[var(--text-primary)]">
            {title}
          </p>
          <CheckboxRounder checked={selected} />
        </div>
        <p className="text-caption text-[var(--text-secondary)]">
          {subtitle}
        </p>
      </div>
    </button>
  );
}

export function DeliveryMethodSelector({ selectedMethod, onMethodChange }: DeliveryMethodSelectorProps) {
  return (
    <div className="flex flex-col gap-[var(--spacing-4)] w-full">
      <p className="text-subtitle text-[var(--text-primary)]">
        Способ доставки
      </p>
      
      <div className="flex gap-[8px] w-full">
        <DeliveryOption
          title="Доставка"
          subtitle="от 30 мин."
          selected={selectedMethod === 'delivery'}
          onClick={() => onMethodChange('delivery')}
        />
        
        <DeliveryOption
          title="Самовывоз"
          subtitle="От 30 мин."
          selected={selectedMethod === 'pickup'}
          onClick={() => onMethodChange('pickup')}
        />
      </div>
    </div>
  );
}