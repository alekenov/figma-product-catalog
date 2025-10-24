import { MessageCircle } from 'lucide-react';

export function WhatsAppIcon({ phone, size = 20 }) {
  const handleWhatsAppClick = (e) => {
    e.preventDefault();
    if (phone) {
      const cleanPhone = phone.replace(/\D/g, '');
      const whatsappUrl = `https://wa.me/${cleanPhone}`;
      window.open(whatsappUrl, '_blank');
    }
  };

  return (
    <button
      onClick={handleWhatsAppClick}
      className="inline-flex items-center justify-center text-green-500 hover:text-green-600 transition flex-shrink-0"
      title="Написать в WhatsApp"
      type="button"
    >
      <MessageCircle size={size} />
    </button>
  );
}

export default WhatsAppIcon;
