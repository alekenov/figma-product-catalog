import svgPaths from '../imports/svg-bdl3k6yajx';
import { imgImage530 } from '../imports/svg-mdqu9';
import imgImage531 from "figma:asset/a7b66a9f71c03462f7b4ffbe86d031aee90babdf.png";

function Frame9659() {
  return (
    <div className="relative shrink-0 size-[16px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
        <g id="Frame 9659">
          <path d={svgPaths.p1484b100} fill="var(--fill-0, #FFB300)" id="Star 13" />
        </g>
      </svg>
    </div>
  );
}

function Frame9658() {
  return (
    <div className="content-stretch flex gap-[4px] items-center relative shrink-0">
      <Frame9659 />
      <p className="font-['Open_Sans:Medium',_sans-serif] leading-[1.3] not-italic relative shrink-0 text-[14px] text-[var(--text-primary)] text-nowrap whitespace-pre">4.6</p>
    </div>
  );
}

function Frame9660() {
  return (
    <div className="content-stretch flex gap-[12px] items-center relative shrink-0">
      <Frame9658 />
      <p className="font-['Open_Sans:Medium',_sans-serif] leading-[1.3] not-italic relative shrink-0 text-[#8f8f8f] text-[14px] text-nowrap whitespace-pre">164 отзыва</p>
      <p className="font-['Open_Sans:Medium',_sans-serif] leading-[1.3] not-italic relative shrink-0 text-[#8f8f8f] text-[14px] text-nowrap whitespace-pre">210 оценок</p>
      <p className="font-['Open_Sans:Medium',_sans-serif] leading-[1.3] not-italic relative shrink-0 text-[#8f8f8f] text-[14px] text-nowrap whitespace-pre">Cvety.kz</p>
    </div>
  );
}

function Frame9661() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative shrink-0">
      <p className="font-['Open_Sans:Medium',_sans-serif] leading-[1.1] not-italic relative shrink-0 text-[20px] text-black w-[341px]">Букет розовых пионов</p>
      <Frame9660 />
    </div>
  );
}

function ProductInfo() {
  return (
    <div className="content-stretch flex flex-col gap-[8px] items-start relative size-full">
      <Frame9661 />

    </div>
  );
}

function MaskGroup() {
  return (
    <div className="basis-0 grid-cols-[max-content] grid-rows-[max-content] grow inline-grid leading-[0] min-h-px min-w-px place-items-start relative shrink-0" data-name="Mask group">
      <div className="[grid-area:1_/_1] h-[499px] mask-alpha mask-intersect mask-no-clip mask-no-repeat mask-position-[26px_2px] mask-size-[343px_492px] ml-[-26px] mt-[-2px] relative rounded-[6px] w-[399px]" data-name="image 530" style={{ maskImage: `url('${imgImage530}')` }}>
        <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none rounded-[6px] size-full" src={imgImage531} />
      </div>
    </div>
  );
}

function Frame9233() {
  return (
    <div className="absolute h-[12px] left-[53.5px] top-[464px] w-[236px]">
      <svg className="block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 236 12">
        <g id="Frame 9233">
          <circle cx="6" cy="6" fill="#FF6666" r="6" id="Ellipse 5" />
          <circle cx="30" cy="6" fill="var(--fill-0, #E0E0E0)" r="6" id="Ellipse 6" />
          <circle cx="54" cy="6" fill="var(--fill-0, #E0E0E0)" r="6" id="Ellipse 7" />
          <circle cx="78" cy="6" fill="var(--fill-0, #E0E0E0)" r="6" id="Ellipse 8" />
          <circle cx="102" cy="6" fill="var(--fill-0, #E0E0E0)" r="6" id="Ellipse 9" />
          <circle cx="126" cy="6" fill="var(--fill-0, #E0E0E0)" r="6" id="Ellipse 10" />
          <circle cx="150" cy="6" fill="var(--fill-0, #E0E0E0)" r="6" id="Ellipse 11" />
          <circle cx="174" cy="6" fill="var(--fill-0, #E0E0E0)" r="6" id="Ellipse 12" />
          <circle cx="198" cy="6" fill="var(--fill-0, #E0E0E0)" r="6" id="Ellipse 13" />
          <circle cx="222" cy="6" fill="var(--fill-0, #E0E0E0)" r="6" id="Ellipse 14" />
        </g>
      </svg>
    </div>
  );
}

export function ProductImageSection() {
  return (
    <div className="content-stretch flex flex-col items-start relative size-full">
      <div className="flex items-start relative shrink-0 w-[375px]">
        <MaskGroup />
        <Frame9233 />
      </div>
      <ProductInfo />
    </div>
  );
}