import svgPaths from "../../imports/svg-d37n8swoc1";

// Navigation breadcrumbs component
function Frame9634() {
  return (
    <div className="flex items-center gap-2 text-caption text-[var(--text-secondary)]">
      <span>Главная</span>
      <span>/</span>
      <span>Магазин цветов - Vetka</span>
    </div>
  );
}

function Frame9636() {
  return (
    <div className="mb-[var(--spacing-2)]">
      <Frame9634 />
    </div>
  );
}

// Star rating component
function Component24IconStarRewiev() {
  return (
    <div className="relative shrink-0 size-[16px]" data-name="24 / icon / star_rewiev">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="24 / icon / star_rewiev">
          <path d={svgPaths.p2eaf7900} fill="var(--brand-primary)" id="Star 8" />
        </g>
      </svg>
    </div>
  );
}

function Frame9658() {
  return (
    <div className="flex items-center gap-1">
      <Component24IconStarRewiev />
      <span className="text-body-emphasis text-[var(--text-primary)]">4.6</span>
    </div>
  );
}

// Social media icons
function Component24IconWhatsapp() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="24 / icon / whatsapp">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="24 / icon / whatsapp">
          <circle cx="12" cy="12" fill="var(--fill-0, white)" id="Oval" r="12" />
          <ellipse cx="12" cy="12" fill="url(#paint0_linear_11_4531)" id="Oval Copy" rx="11.2941" ry="11.2941" />
          <path clipRule="evenodd" d={svgPaths.p3eb29780} fill="var(--fill-0, white)" fillRule="evenodd" id="Shape" />
        </g>
        <defs>
          <linearGradient gradientUnits="userSpaceOnUse" id="paint0_linear_11_4531" x1="-0.649413" x2="31.478" y1="-10.0235" y2="-7.74677">
            <stop stopColor="#20C040" />
            <stop offset="1" stopColor="#20A23A" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}

function Component24IconInstagram() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="24 / icon / instagram">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="24 / icon / instagram">
          <g id="Group">
            <path d={svgPaths.p116b400} fill="url(#paint0_linear_11_4566)" id="Vector" />
            <path d={svgPaths.p5a15e00} fill="url(#paint1_linear_11_4566)" id="Vector_2" />
            <path d={svgPaths.p33943c00} fill="var(--fill-0, #BC30A0)" id="Vector_3" />
          </g>
          <path d={svgPaths.p2aacfd80} fill="url(#paint2_linear_11_4566)" id="Vector_4" />
        </g>
        <defs>
          <linearGradient gradientUnits="userSpaceOnUse" id="paint0_linear_11_4566" x1="19.6045" x2="3.69011" y1="2.68299" y2="22.1812">
            <stop stopColor="#AE3DAE" />
            <stop offset="0.0468721" stopColor="#B23BA6" />
            <stop offset="0.1216" stopColor="#BD368E" />
            <stop offset="0.2148" stopColor="#CE2E69" />
            <stop offset="0.3216" stopColor="#E62335" />
            <stop offset="0.418" stopColor="#FF1800" />
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="paint1_linear_11_4566" x1="14.6979" x2="8.91655" y1="7.46547" y2="17.18">
            <stop stopColor="#E12F6A" />
            <stop offset="0.1705" stopColor="#EA3751" />
            <stop offset="0.3563" stopColor="#F13D3E" />
            <stop offset="0.5467" stopColor="#F64133" />
            <stop offset="0.7469" stopColor="#F7422F" />
            <stop offset="0.7946" stopColor="#F74C2F" />
            <stop offset="0.8743" stopColor="#F7652F" />
            <stop offset="0.9757" stopColor="#F78F2E" />
            <stop offset="1" stopColor="#F79A2E" />
          </linearGradient>
          <linearGradient gradientUnits="userSpaceOnUse" id="paint2_linear_11_4566" x1="16.9945" x2="7.25976" y1="0.0943048" y2="23.3125">
            <stop offset="0.2341" stopColor="#9E35A5" stopOpacity="0" />
            <stop offset="0.4512" stopColor="#D42F7F" stopOpacity="0.5" />
            <stop offset="0.7524" stopColor="#F7772E" />
            <stop offset="0.9624" stopColor="#FEF780" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  );
}

// Store info section
function Frame9660() {
  return (
    <div className="flex flex-wrap items-center gap-3">
      <Frame9658 />
      <span className="text-caption text-[var(--text-secondary)]">164 отзыва</span>
      <span className="text-caption text-[var(--text-secondary)]">210 оценок</span>
      <div className="flex items-center gap-2 ml-auto">
        <Component24IconWhatsapp />
        <Component24IconInstagram />
      </div>
    </div>
  );
}

function Frame9659() {
  return (
    <div className="space-y-[var(--spacing-2)]">
      <h2 className="text-title text-[var(--text-primary)]">Vetka - магазин цветов</h2>
      <Frame9660 />
    </div>
  );
}

// Main header component
export function StorePageHeader() {
  return (
    <div className="p-[var(--spacing-4)] bg-white rounded-[var(--radius-md)] space-y-[var(--spacing-3)]">
      <Frame9636 />
      <Frame9659 />
    </div>
  );
}