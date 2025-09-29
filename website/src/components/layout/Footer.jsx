import React from 'react';

// Asset URLs from Figma
const footerAssets = {
  facebook: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/e2f7e4f0-1681-4d9e-94f1-3a64dfd5ed8a/figma%3Aasset/02ae6e43d5c30097e4e21a4c5e73e5f33d7b7758.svg",
  youtube: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/e2f7e4f0-1681-4d9e-94f1-3a64dfd5ed8a/figma%3Aasset/e01b882a9b70113b43d3d0d2cbfab4dbe6ba5bcc.svg",
  instagram: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/e2f7e4f0-1681-4d9e-94f1-3a64dfd5ed8a/figma%3Aasset/ec6da59cba6e33ef7d34a32e2a5f5dd41b5b60a3.svg",
  vk: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/e2f7e4f0-1681-4d9e-94f1-3a64dfd5ed8a/figma%3Aasset/46dc6b09bc5e4a6af0ddcd16e48cbb3d8e2e37e8.svg",
  visa: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/e2f7e4f0-1681-4d9e-94f1-3a64dfd5ed8a/figma%3Aasset/8d2ad86a16e63e0ce5c3f3fcc4e89c4eb5d18b32.svg",
  mastercard: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/e2f7e4f0-1681-4d9e-94f1-3a64dfd5ed8a/figma%3Aasset/03f0a17ba6c43c9edd4d98ff4fbe6e6f6e069e6e.svg",
  maestro: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/e2f7e4f0-1681-4d9e-94f1-3a64dfd5ed8a/figma%3Aasset/e96e6aa39e8c6fa0f012c05a1cde3c1c05b69b2f.svg",
  paypal: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/e2f7e4f0-1681-4d9e-94f1-3a64dfd5ed8a/figma%3Aasset/be94c3b36f3c1e5dfb5937de88b3e2a63a0d5f3b.svg",
  appStore: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/e2f7e4f0-1681-4d9e-94f1-3a64dfd5ed8a/figma%3Aasset/0866be75caa74a3b01734c05e80e41beeef881aa.svg",
  googlePlay: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/e2f7e4f0-1681-4d9e-94f1-3a64dfd5ed8a/figma%3Aasset/fc5f30e6797815b97efe0f7fb4faf77df76fbc7f.svg"
};

function SocialIcon({ icon, alt, state = "Default" }) {
  return (
    <button className="block overflow-visible relative shrink-0 size-[32px] hover:opacity-80 transition-opacity">
      <div className="absolute inset-0 overflow-clip">
        <img alt={alt} className="block max-w-none size-full" src={icon} />
      </div>
    </button>
  );
}

function FooterLink({ text, href = "#" }) {
  return (
    <a
      href={href}
      className="font-sans font-normal leading-[1.4] relative shrink-0 text-body-2 text-text-grey-dark whitespace-nowrap hover:text-pink transition-colors"
    >
      {text}
    </a>
  );
}

function FooterSection({ title, links }) {
  return (
    <div className="content-stretch flex flex-col gap-2 items-start relative shrink-0">
      <div className="font-sans font-semibold leading-[1.4] relative shrink-0 text-body-2 text-text-black whitespace-nowrap">
        {title}
      </div>
      {links.map((link, index) => (
        <FooterLink key={index} text={link.text} href={link.href} />
      ))}
    </div>
  );
}

export default function Footer() {
  const buyersLinksCol1 = [
    { text: "Магазины", href: "#" },
    { text: "Для партнёров", href: "#" },
    { text: "Фото доставки", href: "#" },
    { text: "Отзывы", href: "#" }
  ];

  const buyersLinksCol2 = [
    { text: "Гарантии", href: "#" },
    { text: "Оплата", href: "#" },
    { text: "Доставка", href: "#" },
    { text: "Вакансии", href: "#" }
  ];

  const companyLinksCol1 = [
    { text: "Контакты", href: "#" },
    { text: "О нас", href: "#" },
    { text: "Конфиденциальности", href: "#" }
  ];

  const companyLinksCol2 = [
    { text: "Документы", href: "#" },
    { text: "Новости", href: "#" },
    { text: "Цветы оптом", href: "#" }
  ];

  return (
    <footer className="bg-bg-light box-border content-stretch flex flex-col gap-6 items-start px-4 py-6 relative w-full">
      {/* Секция ссылок */}
      <div className="content-stretch flex flex-col gap-4 items-start relative shrink-0 w-full">
        {/* Покупателям */}
        <div className="content-stretch flex flex-col gap-2 items-start relative shrink-0 w-full">
          <div className="font-sans font-semibold text-body-1 text-text-black">
            Покупателям
          </div>
          <div className="content-stretch flex gap-[117px] items-start relative shrink-0 w-full">
            <div className="content-stretch flex flex-col gap-1 items-start relative shrink-0">
              {buyersLinksCol1.map((link, index) => (
                <FooterLink key={index} text={link.text} href={link.href} />
              ))}
            </div>
            <div className="content-stretch flex flex-col gap-1 items-start relative shrink-0">
              {buyersLinksCol2.map((link, index) => (
                <FooterLink key={index} text={link.text} href={link.href} />
              ))}
            </div>
          </div>
        </div>

        {/* Компания */}
        <div className="content-stretch flex flex-col gap-2 items-start relative shrink-0 w-full">
          <div className="font-sans font-semibold text-body-1 text-text-black">
            Компания
          </div>
          <div className="content-stretch flex gap-[61px] items-start relative shrink-0 w-full">
            <div className="content-stretch flex flex-col gap-1 items-start relative shrink-0">
              {companyLinksCol1.map((link, index) => (
                <FooterLink key={index} text={link.text} href={link.href} />
              ))}
            </div>
            <div className="content-stretch flex flex-col gap-1 items-start relative shrink-0">
              {companyLinksCol2.map((link, index) => (
                <FooterLink key={index} text={link.text} href={link.href} />
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Copyright и социальные сети */}
      <div className="content-stretch flex flex-col gap-4 items-start relative shrink-0 w-full">
        {/* Copyright */}
        <div className="font-sans font-bold text-body-1 text-text-black">
          © Сvety.kz, 2021
        </div>

        {/* Social Media Icons */}
        <div className="content-stretch flex gap-4 items-start relative shrink-0">
          <SocialIcon icon={footerAssets.facebook} alt="Facebook" />
          <SocialIcon icon={footerAssets.youtube} alt="YouTube" />
          <SocialIcon icon={footerAssets.instagram} alt="Instagram" />
          <SocialIcon icon={footerAssets.vk} alt="VK" />
        </div>

        {/* Payment Methods */}
        <div className="content-stretch flex gap-2 items-center relative shrink-0">
          <div className="h-8 relative shrink-0 w-[65px]">
            <img alt="Visa" className="block max-w-none size-full object-contain" src={footerAssets.visa} />
          </div>
          <div className="h-8 relative shrink-0 w-[47px]">
            <img alt="Mastercard" className="block max-w-none size-full object-contain" src={footerAssets.mastercard} />
          </div>
          <div className="h-8 relative shrink-0 w-[69px]">
            <img alt="Maestro" className="block max-w-none size-full object-contain" src={footerAssets.maestro} />
          </div>
          <div className="h-8 relative shrink-0 w-[90px]">
            <img alt="PayPal" className="block max-w-none size-full object-contain" src={footerAssets.paypal} />
          </div>
        </div>
      </div>

      {/* Приложение */}
      <div className="content-stretch flex flex-col gap-3 items-start relative shrink-0 w-full">
        <div className="font-sans font-semibold text-body-1 text-text-black">
          Приложение
        </div>
        <div className="content-stretch flex gap-2 items-start relative shrink-0 w-full">
          <a href="#" className="flex-1 h-8 relative hover:opacity-80 transition-opacity">
            <img alt="App Store" className="block max-w-none size-full object-contain" src={footerAssets.appStore} />
          </a>
          <a href="#" className="flex-1 h-8 relative hover:opacity-80 transition-opacity">
            <img alt="Google Play" className="block max-w-none size-full object-contain" src={footerAssets.googlePlay} />
          </a>
        </div>
      </div>
    </footer>
  );
}