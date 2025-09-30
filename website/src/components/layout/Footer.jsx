import React from 'react';
import SocialMediaButton from '../SocialMediaButton';
import PaymentMethodsRow from '../PaymentMethodsRow';
import AppDownloadButtons from '../AppDownloadButtons';

/**
 * Footer Link Component
 * Renders a clickable footer link with hover effect
 */
function FooterLink({ text, href = '#' }) {
  return (
    <a
      href={href}
      className="font-sans font-normal text-body-2 text-text-grey-dark hover:text-pink transition-colors whitespace-nowrap"
    >
      {text}
    </a>
  );
}

/**
 * Footer Section Component
 * Renders a footer section with title and links in two columns
 */
function FooterSection({ title, linksCol1, linksCol2 }) {
  const col1Gap = linksCol1.length > linksCol2.length ? '117px' : '61px';

  return (
    <div className="flex flex-col gap-2 w-full">
      <div className="font-sans font-semibold text-body-1 text-text-black">
        {title}
      </div>
      <div className={`flex gap-[${col1Gap}] w-full`} style={{ gap: col1Gap }}>
        <div className="flex flex-col gap-1">
          {linksCol1.map((link, index) => (
            <FooterLink key={index} text={link.text} href={link.href} />
          ))}
        </div>
        <div className="flex flex-col gap-1">
          {linksCol2.map((link, index) => (
            <FooterLink key={index} text={link.text} href={link.href} />
          ))}
        </div>
      </div>
    </div>
  );
}

/**
 * Footer Component
 * Main footer with navigation links, copyright, social media, payment methods, and app download buttons
 * Based on Figma design (node: 1537:49521) with Kazakhstan market adaptation
 */
export default function Footer() {
  // Link data
  const buyersLinksCol1 = [
    { text: 'Магазины', href: '#' },
    { text: 'Для партнёров', href: '#' },
    { text: 'Фото доставки', href: '#' },
    { text: 'Отзывы', href: '#' }
  ];

  const buyersLinksCol2 = [
    { text: 'Гарантии', href: '#' },
    { text: 'Оплата', href: '#' },
    { text: 'Доставка', href: '#' },
    { text: 'Вакансии', href: '#' }
  ];

  const companyLinksCol1 = [
    { text: 'Контакты', href: '#' },
    { text: 'О нас', href: '#' },
    { text: 'Конфиденциальности', href: '#' }
  ];

  const companyLinksCol2 = [
    { text: 'Документы', href: '#' },
    { text: 'Новости', href: '#' },
    { text: 'Цветы оптом', href: '#' }
  ];

  return (
    <footer className="bg-bg-light box-border flex flex-col gap-6 px-4 py-6 w-full">
      {/* Navigation Links Section */}
      <div className="flex flex-col gap-4 w-full">
        {/* Покупателям */}
        <FooterSection
          title="Покупателям"
          linksCol1={buyersLinksCol1}
          linksCol2={buyersLinksCol2}
        />

        {/* Компания */}
        <FooterSection
          title="Компания"
          linksCol1={companyLinksCol1}
          linksCol2={companyLinksCol2}
        />
      </div>

      {/* Copyright, Social Media, and Payment Methods Section */}
      <div className="flex flex-col gap-4 w-full max-w-[343px]">
        {/* Copyright */}
        <div className="font-sans font-bold text-body-1 text-text-black">
          © Сvety.kz, 2021
        </div>

        {/* Social Media Icons */}
        <div className="flex gap-4 items-center">
          <SocialMediaButton type="facebook" href="#" ariaLabel="Facebook" />
          <SocialMediaButton type="youtube" href="#" ariaLabel="YouTube" />
          <SocialMediaButton type="instagram" href="#" ariaLabel="Instagram" />
          <SocialMediaButton type="vk" href="#" ariaLabel="VKontakte" />
        </div>

        {/* Payment Methods */}
        <PaymentMethodsRow />
      </div>

      {/* App Download Section */}
      <div className="flex flex-col gap-3 w-full max-w-[343px]">
        <div className="font-sans font-semibold text-body-1 text-text-black">
          Приложение
        </div>
        <AppDownloadButtons />
      </div>
    </footer>
  );
}