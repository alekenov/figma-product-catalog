import svgPaths from "../../imports/svg-it8vuprc7e";

function Component24OutlinedSuggestedCircle2() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="24/ outlined / suggested / circle / +">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="24/ outlined / suggested / circle / +">
          <path d={svgPaths.pace200} id="Vector" stroke="var(--stroke-0, #8F8F8F)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          <path d="M12 8V16" id="Vector_2" stroke="var(--stroke-0, #8F8F8F)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
          <path d="M8 12H16" id="Vector_3" stroke="var(--stroke-0, #8F8F8F)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
        </g>
      </svg>
    </div>
  );
}

function Frame2064() {
  return (
    <div className="content-stretch flex gap-[12px] items-center relative shrink-0">
      <Component24OutlinedSuggestedCircle2 />
      <p className="font-['Open_Sans:Regular',_sans-serif] font-normal leading-[24px] relative shrink-0 text-[#8f8f8f] text-[16px] text-nowrap whitespace-pre" style={{ fontVariationSettings: "'wdth' 100" }}>
        Добавить открытку (бесплатно)
      </p>
    </div>
  );
}

function Frame2066() {
  return (
    <div className="content-stretch flex flex-col gap-[12px] items-start justify-center relative shrink-0">
      <Frame2064 />
    </div>
  );
}

export function CartMobileAddons() {
  return (
    <div className="box-border content-stretch flex flex-col gap-[24px] items-start pl-[16px] pr-0 py-0 relative shrink-0 w-[375px]" data-name="Add a comment">
      <Frame2066 />
    </div>
  );
}