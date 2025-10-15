import { CvetyInput } from './ui/cvety-input';
import { DeliveryMethod } from './DeliveryMethodSelector';
import { useOrderForm } from '../contexts/OrderFormContext';
import svgPaths from '../imports/svg-y2x5poxegy';

interface AddressSelectorProps {
  deliveryMethod: DeliveryMethod;
  onAddressSelect?: () => void;
}

interface PickupLocation {
  id: string;
  name: string;
  address: string;
  hours: string;
}

const pickupLocations: PickupLocation[] = [
  {
    id: '1',
    name: 'Магазин Cvety.kz',
    address: 'ул. Достык, 9',
    hours: '9:00-21:00'
  },
  {
    id: '2', 
    name: 'Магазин Cvety.kz',
    address: 'ул. Абая, 156',
    hours: '9:00-21:00'
  },
  {
    id: '3',
    name: 'Магазин Cvety.kz', 
    address: 'мкр. Самал-2, д. 58',
    hours: '9:00-21:00'
  }
];

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

function PickupLocationOption({ 
  location, 
  selected, 
  onClick 
}: { 
  location: PickupLocation; 
  selected: boolean; 
  onClick: () => void; 
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`
        w-full bg-white rounded-[8px] border border-solid p-0 text-left transition-all
        ${selected 
          ? 'border-black' 
          : 'border-[#8f8f8f] hover:border-[var(--brand-primary)]'
        }
      `}
    >
      <div className="box-border flex items-center justify-between px-[8px] py-[12px] w-full">
        <div className="flex flex-col">
          <p className="font-semibold text-black text-sm leading-normal">
            {location.address}
          </p>
          <p className="font-normal text-[var(--text-secondary)] text-xs leading-normal">
            {location.hours}
          </p>
        </div>
        <CheckboxRounder checked={selected} />
      </div>
    </button>
  );
}

function DeliveryAddressForm() {
  const { deliveryAddress, setDeliveryAddress } = useOrderForm();

  const handleFieldChange = (field: keyof typeof deliveryAddress, value: string | boolean) => {
    setDeliveryAddress({ ...deliveryAddress, [field]: value });
  };

  return (
    <div className="space-y-[var(--spacing-3)]">
      <div className="flex items-center gap-[var(--spacing-2)]">
        <button
          type="button"
          onClick={() => handleFieldChange('askRecipient', !deliveryAddress.askRecipient)}
          className={`relative bg-white border border-solid rounded-[4px] w-4 h-4 shrink-0 flex items-center justify-center transition-all duration-200 ${
            deliveryAddress.askRecipient
              ? 'border-[var(--brand-primary)] bg-[var(--brand-primary)]'
              : 'border-black hover:border-[var(--brand-primary)]'
          }`}
        >
          {deliveryAddress.askRecipient && (
            <svg className="w-3 h-3 text-white" viewBox="0 0 12 12" fill="none">
              <path
                d="M10 3L4.5 8.5L2 6"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          )}
        </button>
        <label
          onClick={() => handleFieldChange('askRecipient', !deliveryAddress.askRecipient)}
          className="text-sm text-[var(--text-primary)] font-medium leading-[22px] cursor-pointer select-none"
        >
          Узнать у получателя
        </label>
      </div>

      {!deliveryAddress.askRecipient && (
        <div className="space-y-[var(--spacing-3)]">
          <CvetyInput
            label="Адрес доставки"
            placeholder="Введите адрес доставки"
            value={deliveryAddress.address}
            onChange={(e) => handleFieldChange('address', e.target.value)}
          />

          <div className="grid grid-cols-2 gap-[var(--spacing-2)]">
            <CvetyInput
              label="Этаж"
              placeholder="Этаж"
              value={deliveryAddress.floor}
              onChange={(e) => handleFieldChange('floor', e.target.value)}
            />
            <CvetyInput
              label="Кв/Офис"
              placeholder="№ кв/офиса"
              value={deliveryAddress.apartment}
              onChange={(e) => handleFieldChange('apartment', e.target.value)}
            />
          </div>

          <CvetyInput
            label="Примечания"
            placeholder="Домофон, особые указания"
            value={deliveryAddress.additionalInfo}
            onChange={(e) => handleFieldChange('additionalInfo', e.target.value)}
          />
        </div>
      )}
    </div>
  );
}

function PickupAddressSelector() {
  const { pickupLocation, setPickupLocation } = useOrderForm();

  const handleLocationSelect = (location: PickupLocation) => {
    setPickupLocation({
      locationId: location.id,
      address: location.address
    });
  };

  return (
    <div className="space-y-[var(--spacing-2)]">
      {pickupLocations.map((location) => (
        <PickupLocationOption
          key={location.id}
          location={location}
          selected={pickupLocation.locationId === location.id}
          onClick={() => handleLocationSelect(location)}
        />
      ))}
    </div>
  );
}

export function AddressSelector({ deliveryMethod, onAddressSelect }: AddressSelectorProps) {
  const isDelivery = deliveryMethod === 'delivery';
  
  return (
    <div className="flex flex-col gap-[var(--spacing-4)] w-full">
      <p className="text-base text-[var(--text-primary)] font-normal leading-[1.1]">
        {isDelivery ? 'Адрес доставки' : 'Адрес самовывоза'}
      </p>
      
      {isDelivery ? (
        <DeliveryAddressForm />
      ) : (
        <PickupAddressSelector />
      )}
    </div>
  );
}