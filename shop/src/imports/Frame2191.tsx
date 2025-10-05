import svgPaths from "./svg-sl68wle2yv";

function Checkbox() {
  return (
    <div className="bg-white overflow-clip relative rounded-[4px] shrink-0 size-[16px]" data-name="Checkbox">
      <div className="absolute inset-0 rounded-[4px]" data-name="Checkbox/Default">
        <div aria-hidden="true" className="absolute border border-black border-solid inset-0 pointer-events-none rounded-[4px]" />
      </div>
    </div>
  );
}

function Frame9381() {
  return (
    <div className="content-stretch flex gap-[8px] items-center relative shrink-0">
      <Checkbox />
      <p className="font-['Open_Sans:Medium',_sans-serif] leading-[22px] not-italic relative shrink-0 text-[14px] text-black text-nowrap whitespace-pre">Узнать у получателя</p>
    </div>
  );
}

function Frame9581() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0">
      <p className="font-['Open_Sans:Regular',_sans-serif] font-normal leading-[1.1] relative shrink-0 text-[16px] text-black text-nowrap whitespace-pre" style={{ fontVariationSettings: "'wdth' 100" }}>
        Адрес доставки
      </p>
      <Frame9381 />
    </div>
  );
}

function Component24IconArrowRight() {
  return (
    <div className="relative shrink-0 size-[24px]" data-name="24 / icon / arrow right">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 24 24">
        <g id="24 / icon / arrow right">
          <path d={svgPaths.p206bb600} fill="var(--fill-0, black)" id="Vector" />
        </g>
      </svg>
    </div>
  );
}

function Frame10203() {
  return (
    <div className="basis-0 content-stretch flex grow items-center justify-between min-h-px min-w-px relative shrink-0">
      <p className="font-['Open_Sans:Medium',_sans-serif] leading-[22px] not-italic relative shrink-0 text-[14px] text-black text-nowrap whitespace-pre">Достык, 9</p>
      <Component24IconArrowRight />
    </div>
  );
}

function Frame2095() {
  return (
    <div className="box-border content-stretch flex gap-[10px] items-start pb-[10px] pt-0 px-0 relative shrink-0 w-[343px]">
      <div aria-hidden="true" className="absolute border-[#dfdfdf] border-[0px_0px_1px] border-solid inset-0 pointer-events-none" />
      <Frame10203 />
    </div>
  );
}

function Frame2092() {
  return (
    <div className="content-stretch flex flex-col gap-[16px] items-start relative shrink-0 w-[343px]">
      <Frame2095 />
    </div>
  );
}

function Frame9582() {
  return (
    <div className="content-stretch flex flex-col gap-[16px] items-start relative shrink-0 w-[343px]">
      <Frame2092 />
    </div>
  );
}

export default function Frame2191() {
  return (
    <div className="content-stretch flex flex-col gap-[16px] items-start relative size-full">
      <Frame9581 />
      <Frame9582 />
    </div>
  );
}