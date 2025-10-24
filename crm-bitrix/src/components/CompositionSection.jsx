import { Trash2 } from 'lucide-react';

export function CompositionSection({ items = [], onChange, disabled = false }) {
  const addItem = () => {
    onChange([...items, { name: '', quantity: '' }]);
  };

  const updateItem = (index, field, value) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    onChange(newItems);
  };

  const removeItem = (index) => {
    onChange(items.filter((_, i) => i !== index));
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-gray-900">Состав букета</h2>

      {items.length > 0 && (
        <div className="space-y-3">
          {items.map((item, index) => (
            <div key={index} className="flex gap-3">
              <div className="flex-1">
                <input
                  type="text"
                  value={item.name}
                  onChange={(e) => updateItem(index, 'name', e.target.value)}
                  disabled={disabled}
                  placeholder="Название цветка"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                />
              </div>
              <div className="w-24">
                <input
                  type="text"
                  inputMode="numeric"
                  value={item.quantity}
                  onChange={(e) =>
                    updateItem(index, 'quantity', e.target.value.replace(/\D/g, ''))
                  }
                  disabled={disabled}
                  placeholder="Кол-во"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-600"
                />
              </div>
              <button
                type="button"
                onClick={() => removeItem(index)}
                disabled={disabled}
                className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition disabled:opacity-50"
              >
                <Trash2 size={20} />
              </button>
            </div>
          ))}
        </div>
      )}

      <button
        type="button"
        onClick={addItem}
        disabled={disabled}
        className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition disabled:opacity-50 font-medium"
      >
        + Добавить цветок
      </button>
    </div>
  );
}
