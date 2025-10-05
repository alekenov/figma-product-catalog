import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useToast } from './components/ToastProvider';
import './App.css';
import { API_BASE_URL, authenticatedFetch } from './services/api';

function WarehouseAddInventory() {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [items, setItems] = useState([{ name: '', quantity: '', cost_price: '' }]);
  const [submitting, setSubmitting] = useState(false);

  const addNewRow = () => {
    setItems([...items, { name: '', quantity: '', cost_price: '' }]);
  };

  const updateItem = (index, field, value) => {
    const newItems = [...items];

    if (field === 'quantity' || field === 'cost_price') {
      // Only allow positive integers
      if (value === '' || (/^\d+$/.test(value) && parseInt(value) > 0)) {
        newItems[index][field] = value;
      }
    } else {
      newItems[index][field] = value;
    }

    setItems(newItems);

    // Auto-add new row if current row is being filled and it's the last row
    if (index === items.length - 1 && newItems[index].name && newItems[index].quantity && newItems[index].cost_price) {
      addNewRow();
    }
  };

  const removeItem = (index) => {
    if (items.length > 1) {
      const newItems = items.filter((_, i) => i !== index);
      setItems(newItems);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);

    try {
      const validItems = items.filter(item =>
        item.name.trim() && item.quantity && item.cost_price
      );

      if (validItems.length === 0) {
        showToast('Необходимо заполнить хотя бы один товар полностью', 'error');
        return;
      }

      const promises = validItems.map(async (item) => {
        const response = await authenticatedFetch(`${API_BASE_URL}/warehouse/`, {
          method: 'POST',
          body: JSON.stringify({
            name: item.name.trim(),
            quantity: parseInt(item.quantity),
            cost_price_tenge: parseInt(item.cost_price), // Price in tenge
            retail_price_tenge: parseInt(item.cost_price) * 2, // Default markup
            min_quantity: 5 // Default minimum quantity
          })
        });

        if (!response.ok) {
          throw new Error(`Ошибка при добавлении товара "${item.name}"`);
        }

        return response.json();
      });

      await Promise.all(promises);

      showToast(`Успешно добавлено ${validItems.length} товар(ов)`, 'success');
      navigate('/warehouse');

    } catch (err) {
      console.error('Error submitting inventory:', err);
      showToast(`Ошибка при добавлении товаров: ${err.message}`, 'error');
    } finally {
      setSubmitting(false);
    }
  };

  const hasValidItems = () => {
    return items.some(item =>
      item.name.trim() && item.quantity && item.cost_price
    );
  };

  return (
    <div className="figma-container bg-white">
      {/* Header */}
      <div className="flex items-center justify-between px-4 mt-5 mb-6">
        <button
          onClick={() => navigate('/warehouse')}
          className="text-purple-primary font-['Open_Sans']"
        >
          ← Назад
        </button>
        <h1 className="text-xl font-['Open_Sans'] font-semibold">Добавить товары</h1>
        <div></div>
      </div>

      <form onSubmit={handleSubmit} className="px-4">
        {/* Header row */}
        <div className="flex gap-2 mb-4 text-sm font-['Open_Sans'] font-medium text-gray-700">
          <div className="w-[50%]">Название товара</div>
          <div className="w-[25%] text-center">Кол-во</div>
          <div className="w-[25%] text-center">Себестоимость</div>
        </div>

        {/* Items rows */}
        <div className="space-y-3 mb-6">
          {items.map((item, index) => (
            <div key={index} className="flex gap-2 items-center">
              {/* Name field - 50% width */}
              <input
                type="text"
                value={item.name}
                onChange={(e) => updateItem(index, 'name', e.target.value)}
                placeholder="Название товара"
                className="w-[50%] px-3 py-2 border border-gray-border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-primary focus:border-transparent text-sm"
              />

              {/* Quantity field - 25% width */}
              <input
                type="text"
                inputMode="numeric"
                value={item.quantity}
                onChange={(e) => updateItem(index, 'quantity', e.target.value)}
                placeholder="0"
                className="w-[25%] px-2 py-2 text-center border border-gray-border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-primary focus:border-transparent text-sm"
              />

              {/* Cost price field - 25% width */}
              <div className="w-[25%] relative">
                <input
                  type="text"
                  inputMode="numeric"
                  value={item.cost_price}
                  onChange={(e) => updateItem(index, 'cost_price', e.target.value)}
                  placeholder="0"
                  className="w-full px-2 py-2 pr-6 text-center border border-gray-border rounded-lg focus:outline-none focus:ring-2 focus:ring-purple-primary focus:border-transparent text-sm"
                />
                <span className="absolute right-2 top-2 text-gray-disabled text-sm">₸</span>
              </div>

              {/* Remove button (only show if more than 1 item) */}
              {items.length > 1 && (
                <button
                  type="button"
                  onClick={() => removeItem(index)}
                  className="w-6 h-6 flex items-center justify-center text-red-500 hover:text-red-700 transition-colors"
                  title="Удалить строку"
                >
                  ×
                </button>
              )}
            </div>
          ))}
        </div>

        {/* Add row button */}
        <div className="mb-6">
          <button
            type="button"
            onClick={addNewRow}
            className="text-purple-primary font-['Open_Sans'] text-sm hover:text-purple-600 transition-colors"
          >
            + Добавить еще товар
          </button>
        </div>

        {/* Submit button */}
        <div className="pb-8">
          <button
            type="submit"
            disabled={submitting || !hasValidItems()}
            className={`w-full py-3 rounded-lg font-['Open_Sans'] font-medium ${
              submitting || !hasValidItems()
                ? 'bg-gray-neutral text-gray-disabled cursor-not-allowed'
                : 'bg-purple-primary text-white hover:bg-purple-600'
            }`}
          >
            {submitting ? 'Добавление...' : 'Принять поставку'}
          </button>

          {hasValidItems() && (
            <div className="mt-2 text-xs text-center text-gray-disabled">
              Новые товары будут добавлены на склад
            </div>
          )}
        </div>
      </form>
    </div>
  );
}

export default WarehouseAddInventory;
