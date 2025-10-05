import svgPaths from "./svg-y2x5poxegy";

function Frame2188() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0">
      <p className="font-['Open_Sans:Medium',_sans-serif] leading-[1.1] not-italic relative shrink-0 text-[16px] text-black text-nowrap whitespace-pre">Способ доставки</p>
    </div>
  );
}

function Component16OutlinedSuggestedSymbolCheck() {
  return (
    <div className="relative shrink-0 size-[10.667px]" data-name="16/ outlined / suggested / symbol / check">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 11 11">
        <g id="16/ outlined / suggested / symbol / check">
          <path d={svgPaths.p193a5f00} id="Vector" stroke="var(--stroke-0, white)" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.33333" />
        </g>
      </svg>
    </div>
  );
}

function CheckboxRounder() {
  return (
    <div className="bg-[#ff6666] box-border content-stretch flex gap-[6.667px] items-start p-[2.667px] relative rounded-[30px] shrink-0" data-name="Checkbox_rounder">
      <Component16OutlinedSuggestedSymbolCheck />
    </div>
  );
}

function Frame9385() {
  return (
    <div className="content-stretch flex items-center justify-between relative shrink-0 w-full">
      <p className="font-['Open_Sans:SemiBold',_sans-serif] font-semibold leading-[normal] relative shrink-0 text-[16px] text-black text-nowrap whitespace-pre" style={{ fontVariationSettings: "'wdth' 100" }}>
        Доставка
      </p>
      <CheckboxRounder />
    </div>
  );
}

function Frame9384() {
  return (
    <div className="basis-0 bg-white grow min-h-px min-w-px relative rounded-[8px] shrink-0">
      <div aria-hidden="true" className="absolute border border-black border-solid inset-0 pointer-events-none rounded-[8px]" />
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[2px] items-start pl-[8px] pr-[16px] py-[12px] relative w-full">
          <Frame9385 />
          <p className="font-['Open_Sans:Regular',_sans-serif] font-normal leading-[normal] relative shrink-0 text-[14px] text-black text-nowrap whitespace-pre" style={{ fontVariationSettings: "'wdth' 100" }}>
            от 30 мин.
          </p>
        </div>
      </div>
    </div>
  );
}

function CheckboxRounder1() {
  return (
    <div className="relative rounded-[30px] shrink-0 size-[16px]" data-name="Checkbox_rounder">
      <div aria-hidden="true" className="absolute border border-[#8f8f8f] border-solid inset-0 pointer-events-none rounded-[30px]" />
    </div>
  );
}

function Frame9386() {
  return (
    <div className="content-stretch flex items-center justify-between relative shrink-0 w-full">
      <p className="font-['Open_Sans:SemiBold',_sans-serif] font-semibold leading-[normal] relative shrink-0 text-[16px] text-black text-nowrap whitespace-pre" style={{ fontVariationSettings: "'wdth' 100" }}>
        Самовывоз
      </p>
      <CheckboxRounder1 />
    </div>
  );
}

function Frame9387() {
  return (
    <div className="basis-0 bg-white grow h-[67px] min-h-px min-w-px relative rounded-[8px] shrink-0">
      <div aria-hidden="true" className="absolute border border-[#8f8f8f] border-solid inset-0 pointer-events-none rounded-[8px]" />
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[2px] h-[67px] items-start pl-[8px] pr-[16px] py-[12px] relative w-full">
          <Frame9386 />
          <p className="font-['Open_Sans:Regular',_sans-serif] font-normal leading-[normal] relative shrink-0 text-[14px] text-black text-nowrap whitespace-pre" style={{ fontVariationSettings: "'wdth' 100" }}>
            От 30 мин.
          </p>
        </div>
      </div>
    </div>
  );
}

function Frame9432() {
  return (
    <div className="content-stretch flex gap-[8px] items-start relative shrink-0 w-full">
      <Frame9384 />
      <Frame9387 />
    </div>
  );
}

function Frame9570() {
  return (
    <div className="content-stretch flex flex-col gap-[16px] items-start relative shrink-0 w-full">
      <Frame9432 />
    </div>
  );
}

export default function Frame10127() {
  return (
    <div className="relative size-full">
      <div className="size-full">
        <div className="box-border content-stretch flex flex-col gap-[16px] items-start px-[16px] py-0 relative size-full">
          <Frame2188 />
          <Frame9570 />
        </div>
      </div>
    </div>
  );
}