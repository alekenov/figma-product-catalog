const imgRectangle = "https://s3-alpha-sig.figma.com/img/d1e4/a43d/fd35275968d7a4b44aa8a93a79982faa?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=SPPIYh0mkf07TwQtKsrJKG5PqzePnSqC9juNWynWV7Uj6w2dbm-eoXlUKI1~~qk3VlJVm57xBdmATi-LNVTDc8TYaX3anbySkHz~QoDapmYYiBwQjIk4sbFD-YSL7-BXPy7KEcAnphjTvhceLQi~qQBXZIyrVZgslz9C4L8Fi-h-dpwh7ZJdLLGswwh~AqlCePl7zGdiWFlJQwYmwCuhnGaykwvE3s0LgTIfneb~gh-H1ZXRIa-WaPks5djM2INychR2QnGTNRMwz2ejlVW1TycpIDhJku6MUJxMfpkw-grqHzcAyD8JZV8rbXZWwHz7V96JPDVmrl1YnFGUxj06Hg__";
const imgRectangle1 = "https://s3-alpha-sig.figma.com/img/4383/50a0/f5172f1ab210cb733df6869e0b9f8ef5?Expires=1759708800&Key-Pair-Id=APKAQ4GOSFWCW27IBOMQ&Signature=lYC3Fr7o-thSASyeM83OzIwund7RFXV-k5X5qA1keits0702vrJ4EfErOmZQ1z7Mbf6oX6VuQa4nAlcXrWn81FqAqbXpohBnEmEhuFopGVI1y0dzUNTtPwE62pRuJil6ULoafDUXtySbkVROlqfuPlXaETav7vrywawSrzf92V7dKIWB-5WNdoHe-KPu~kUu3eiQmL6YcR7FGWgtbUBivnZnYuR~KaY1HLyeKkidbbveYQBI4865fL8~MjybzAwpdLmuMi0RQX-m5c74Wa3bR170y0yP8VAWSURPoAd2BCLwehRlCr6pg9YzIaaX1zxrxLT38MDjSBGDIaTSjmJCHg__";
const imgIcon = "data:image/svg+xml,%3Csvg width='30' height='30' viewBox='0 0 30 30' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='30' height='30' rx='6' fill='%238A49F3'/%3E%3Cpath d='M15 9V21M9 15H21' stroke='white' stroke-width='2' stroke-linecap='round'/%3E%3C/svg%3E";
const imgRectangle352 = "data:image/svg+xml,%3Csvg width='288' height='46' viewBox='0 0 288 46' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='288' height='46' rx='8' fill='%23F2F2F2'/%3E%3C/svg%3E";
const imgSearch21 = "data:image/svg+xml,%3Csvg width='16' height='16' viewBox='0 0 16 16' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M7.33333 12.6667C10.2789 12.6667 12.6667 10.2789 12.6667 7.33333C12.6667 4.38781 10.2789 2 7.33333 2C4.38781 2 2 4.38781 2 7.33333C2 10.2789 4.38781 12.6667 7.33333 12.6667Z' stroke='%23828282' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3Cpath d='M14 14L11.1 11.1' stroke='%23828282' stroke-width='1.5' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E";
const imgGroup81 = "data:image/svg+xml,%3Csvg width='44' height='24' viewBox='0 0 44 24' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='44' height='24' rx='12' fill='%2334C759'/%3E%3Ccircle cx='32' cy='12' r='10' fill='white'/%3E%3C/svg%3E";
const imgGroup = "data:image/svg+xml,%3Csvg width='15' height='14' viewBox='0 0 15 14' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M13.5 13H1.5V5.5C1.5 4.39543 2.39543 3.5 3.5 3.5H11.5C12.6046 3.5 13.5 4.39543 13.5 5.5V13Z' stroke='black' stroke-width='1.5'/%3E%3Cpath d='M5.5 3.5V1.5C5.5 1.22386 5.72386 1 6 1H9C9.27614 1 9.5 1.22386 9.5 1.5V3.5' stroke='black' stroke-width='1.5'/%3E%3C/svg%3E";
const imgGroup5 = "data:image/svg+xml,%3Csvg width='16' height='15' viewBox='0 0 16 15' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M3 1H13L11 6H5L3 1Z' stroke='black' stroke-width='1.5' stroke-linejoin='round'/%3E%3Cpath d='M5 6V14' stroke='black' stroke-width='1.5'/%3E%3Cpath d='M11 6V14' stroke='black' stroke-width='1.5'/%3E%3Cpath d='M8 6V10' stroke='black' stroke-width='1.5'/%3E%3C/svg%3E";
const imgContainer = "data:image/svg+xml,%3Csvg width='288' height='34' viewBox='0 0 288 34' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Crect x='0.5' y='0.5' width='287' height='33' rx='5.5' stroke='%23E0E0E0'/%3E%3C/svg%3E";
const imgSegment = "data:image/svg+xml,%3Csvg width='144' height='34' viewBox='0 0 144 34' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='144' height='34' rx='6' fill='%238A49F3'/%3E%3C/svg%3E";
const imgLine5 = "data:image/svg+xml,%3Csvg width='288' height='1' viewBox='0 0 288 1' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cline y1='0.5' x2='288' y2='0.5' stroke='%23E0E0E0'/%3E%3C/svg%3E";
const imgGroup132 = "data:image/svg+xml,%3Csvg width='44' height='24' viewBox='0 0 44 24' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Crect width='44' height='24' rx='12' fill='%23C4C4C4'/%3E%3Ccircle cx='12' cy='12' r='10' fill='white'/%3E%3C/svg%3E";

import './App.css';

export default function Component() {
  return (
    <div className="figma-container">
    <div className="bg-white relative size-full min-h-[1100px]" data-name="Лента товаров" data-node-id="263:1711">
      <div className="absolute font-['Open_Sans:Regular',_sans-serif] font-normal leading-[0] left-[16px] text-[24px] text-black top-[70px] whitespace-nowrap" data-node-id="263:1712" style={{ right: "calc(66.667% + 1.667px)", fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[normal]">Товары</p>
      </div>
      <a className="absolute block cursor-pointer h-[24px] left-[87.5%] right-[5%] top-[74px]" data-name="Icon" data-node-id="263:1713">
        <img alt="" className="block max-w-none size-full" src={imgIcon} />
      </a>
      <div className="absolute contents left-[16px] top-[115px]" data-node-id="263:1716">
        <div className="absolute h-[46px] left-[16px] top-[115px] w-[288px]" data-name="Rectangle 3.52" data-node-id="263:1717">
          <img alt="" className="block max-w-none size-full" src={imgRectangle352} />
        </div>
        <div className="absolute font-['Open_Sans:Regular',_sans-serif] font-normal leading-[0] text-[#828282] text-[16px] top-[127px] translate-x-[100%] whitespace-nowrap" data-node-id="263:1718" style={{ fontVariationSettings: "'wdth' 100", right: "calc(66.667% + 78.667px)" }}>
          <p className="leading-[normal]">Найти</p>
        </div>
        <div className="absolute contents top-[130px]" data-node-id="263:1719" style={{ left: "calc(83.333% + 9.333px)" }}>
          <div className="absolute size-[16px] top-[130px]" data-name="search (2) 1" data-node-id="263:1720" style={{ left: "calc(83.333% + 9.333px)" }}>
            <img alt="" className="block max-w-none size-full" src={imgSearch21} />
          </div>
        </div>
      </div>
      <div className="absolute font-['Open_Sans:Bold',_sans-serif] font-bold leading-[0] text-[14px] text-black top-[229px] translate-x-[100%] w-[132px]" data-node-id="263:1722" style={{ right: "calc(16.667% + 150.667px)", fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[normal] whitespace-pre-wrap">Красный букет</p>
      </div>
      <div className="absolute font-['Open_Sans:Regular',_'Noto_Sans:Regular',_sans-serif] font-normal leading-[0] text-[14px] text-black top-[253px] translate-x-[100%] whitespace-nowrap" data-node-id="263:1723" style={{ fontVariationSettings: "'wdth' 100", right: "calc(33.333% + 97.333px)" }}>
        <p className="leading-[normal]">12 000 ₸</p>
      </div>
      <div className="absolute h-[88px] left-[16px] top-[229px]" data-name="Rectangle" data-node-id="263:1724" style={{ right: "calc(66.667% + 2.667px)" }}>
        <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none size-full" src={imgRectangle} />
      </div>
      <div className="absolute h-[24px] top-[229px] w-[44px]" data-node-id="263:1725" style={{ left: "calc(83.333% - 6.667px)" }}>
        <img alt="" className="block max-w-none size-full" src={imgGroup81} />
      </div>
      <div className="absolute contents left-[16px] top-[181px]" data-node-id="263:1728">
        <div className="absolute font-['Open_Sans:Regular',_sans-serif] font-normal leading-[0] text-[14px] text-black top-[181px] translate-x-[100%] w-[169px]" data-node-id="263:1729" style={{ fontVariationSettings: "'wdth' 100", right: "calc(33.333% + 177.333px)" }}>
          <p className="leading-[normal] whitespace-pre-wrap">Магазин Cvety.kz</p>
        </div>
        <div className="absolute left-[16px] overflow-clip size-[16px] top-[183px]" data-name="shop 1" data-node-id="263:1730">
          <div className="absolute contents inset-[6.25%_6.25%_6.44%_6.25%]" data-name="Group" data-node-id="263:1731">
            <div className="absolute contents inset-[6.25%_6.25%_6.44%_6.25%]" data-node-id="263:1732">
              <div className="absolute inset-[6.25%_6.25%_6.44%_6.25%]" data-name="Group" data-node-id="263:1733">
                <img alt="" className="block max-w-none size-full" src={imgGroup} />
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="absolute contents top-[181px]" data-node-id="263:1744" style={{ left: "calc(66.667% + 7.667px)" }}>
        <div className="absolute font-['Open_Sans:Regular',_sans-serif] font-normal leading-[0] right-[16px] text-[14px] text-black text-right top-[181px] whitespace-nowrap" data-node-id="263:1745" style={{ fontVariationSettings: "'wdth' 100" }}>
          <p className="leading-[normal]">Фильтры</p>
        </div>
        <div className="absolute contents top-[183px]" data-node-id="263:1746" style={{ left: "calc(66.667% + 7.667px)" }}>
          <div className="absolute overflow-clip size-[16px] top-[183px]" data-name="filter (4) 1" data-node-id="263:1747" style={{ left: "calc(66.667% + 7.667px)" }}>
            <div className="absolute bottom-[6.25%] left-0 right-0 top-[6.25%]" data-name="Group" data-node-id="263:1748">
              <img alt="" className="block max-w-none size-full" src={imgGroup5} />
            </div>
          </div>
        </div>
      </div>
      <div className="absolute contents left-[16px] top-[16px]" data-node-id="263:1752">
        <div className="absolute h-[34px] left-[16px] top-[16px] w-[288px]" data-name="Container" data-node-id="263:1753">
          <img alt="" className="block max-w-none size-full" src={imgContainer} />
        </div>
        <div className="absolute h-[34px] left-[16px] top-[16px] w-[144px]" data-name="Segment" data-node-id="263:1754">
          <img alt="" className="block max-w-none size-full" src={imgSegment} />
        </div>
        <div className="absolute flex flex-col font-['Open_Sans:Regular',_sans-serif] font-normal h-[18px] justify-center leading-[0] left-[88px] text-[14px] text-center text-white top-[33px] translate-x-[-50%] translate-y-[-50%] w-[144px]" data-node-id="263:1755" style={{ fontVariationSettings: "'wdth' 100" }}>
          <p className="leading-[normal] whitespace-pre-wrap">Товары</p>
        </div>
        <div className="absolute flex flex-col font-['Open_Sans:Regular',_sans-serif] font-normal h-[18px] justify-center leading-[0] text-[#8a49f3] text-[14px] text-center top-[33px] translate-x-[-50%] translate-y-[-50%] w-[144px]" data-node-id="263:1756" style={{ left: "calc(50% + 72px)", fontVariationSettings: "'wdth' 100" }}>
          <p className="leading-[normal] whitespace-pre-wrap">Готовые товары</p>
        </div>
      </div>
      <div className="absolute h-0 left-[16px] top-[325px] w-[288px]" data-node-id="263:1757">
        <div className="absolute bottom-0 left-0 right-0 top-[-1px]">
          <img alt="" className="block max-w-none size-full" src={imgLine5} />
        </div>
      </div>
      <div className="absolute font-['Open_Sans:Bold',_sans-serif] font-bold leading-[0] text-[14px] text-black top-[333px] translate-x-[100%] w-[132px]" data-node-id="263:1758" style={{ fontVariationSettings: "'wdth' 100", right: "calc(16.667% + 150.667px)" }}>
        <p className="leading-[normal] whitespace-pre-wrap">Сердечное признание в любви</p>
      </div>
      <div className="absolute font-['Open_Sans:Regular',_'Noto_Sans:Regular',_sans-serif] font-normal leading-[0] text-[14px] text-black top-[395px] translate-x-[100%] whitespace-nowrap" data-node-id="263:1759" style={{ fontVariationSettings: "'wdth' 100", right: "calc(33.333% + 97.333px)" }}>
        <p className="leading-[normal]">12 000 ₸</p>
      </div>
      <div className="absolute h-[24px] top-[333px] w-[44px]" data-node-id="263:1760" style={{ left: "calc(83.333% - 6.667px)" }}>
        <img alt="" className="block max-w-none size-full" src={imgGroup81} />
      </div>
      <div className="absolute h-0 left-[16px] top-[429px] w-[288px]" data-node-id="263:1763">
        <div className="absolute bottom-0 left-0 right-0 top-[-1px]">
          <img alt="" className="block max-w-none size-full" src={imgLine5} />
        </div>
      </div>
      <div className="absolute h-0 left-[16px] top-[221px] w-[288px]" data-node-id="263:1764">
        <div className="absolute bottom-0 left-0 right-0 top-[-1px]">
          <img alt="" className="block max-w-none size-full" src={imgLine5} />
        </div>
      </div>
      <div className="absolute h-[88px] left-[16px] top-[333px]" data-name="Rectangle" data-node-id="263:1765" style={{ right: "calc(66.667% + 2.667px)" }}>
        <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none size-full" src={imgRectangle1} />
      </div>
      <div className="absolute font-['Open_Sans:Bold',_sans-serif] font-bold leading-[0] text-[14px] text-black top-[437px] translate-x-[100%] w-[132px]" data-node-id="263:1766" style={{ fontVariationSettings: "'wdth' 100", right: "calc(16.667% + 150.667px)" }}>
        <p className="leading-[normal] whitespace-pre-wrap">Красный букет</p>
      </div>
      <div className="absolute font-['Open_Sans:Regular',_'Noto_Sans:Regular',_sans-serif] font-normal leading-[0] text-[14px] text-black top-[461px] translate-x-[100%] whitespace-nowrap" data-node-id="263:1767" style={{ fontVariationSettings: "'wdth' 100", right: "calc(33.333% + 97.333px)" }}>
        <p className="leading-[normal]">12 000 ₸</p>
      </div>
      <div className="absolute h-[88px] left-[16px] top-[437px]" data-name="Rectangle" data-node-id="263:1768" style={{ right: "calc(66.667% + 2.667px)" }}>
        <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none size-full" src={imgRectangle} />
      </div>
      <div className="absolute h-[24px] top-[437px] w-[44px]" data-node-id="263:1769" style={{ left: "calc(83.333% - 6.667px)" }}>
        <img alt="" className="block max-w-none size-full" src={imgGroup81} />
      </div>
      <div className="absolute h-0 left-[16px] top-[533px] w-[288px]" data-node-id="263:1772">
        <div className="absolute bottom-0 left-0 right-0 top-[-1px]">
          <img alt="" className="block max-w-none size-full" src={imgLine5} />
        </div>
      </div>
      <div className="absolute font-['Open_Sans:Bold',_sans-serif] font-bold leading-[0] text-[14px] text-black top-[541px] translate-x-[100%] w-[132px]" data-node-id="263:1773" style={{ fontVariationSettings: "'wdth' 100", right: "calc(16.667% + 150.667px)" }}>
        <p className="leading-[normal] whitespace-pre-wrap">Сердечное признание в любви</p>
      </div>
      <div className="absolute font-['Open_Sans:Regular',_'Noto_Sans:Regular',_sans-serif] font-normal leading-[0] text-[14px] text-black top-[603px] translate-x-[100%] whitespace-nowrap" data-node-id="263:1774" style={{ fontVariationSettings: "'wdth' 100", right: "calc(33.333% + 97.333px)" }}>
        <p className="leading-[normal]">12 000 ₸</p>
      </div>
      <div className="absolute h-[24px] top-[541px] w-[44px]" data-node-id="263:1775" style={{ left: "calc(83.333% - 6.667px)" }}>
        <img alt="" className="block max-w-none size-full" src={imgGroup81} />
      </div>
      <div className="absolute h-0 left-[16px] top-[637px] w-[288px]" data-node-id="263:1778">
        <div className="absolute bottom-0 left-0 right-0 top-[-1px]">
          <img alt="" className="block max-w-none size-full" src={imgLine5} />
        </div>
      </div>
      <div className="absolute h-[88px] left-[16px] top-[541px]" data-name="Rectangle" data-node-id="263:1779" style={{ right: "calc(66.667% + 2.667px)" }}>
        <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none size-full" src={imgRectangle1} />
      </div>
      <div className="absolute font-['Open_Sans:Bold',_sans-serif] font-bold leading-[0] text-[#6b6773] text-[14px] top-[645px] translate-x-[100%] w-[132px]" data-node-id="263:1780" style={{ right: "calc(16.667% + 150.667px)", fontVariationSettings: "'wdth' 100" }}>
        <p className="leading-[normal] whitespace-pre-wrap">Красный букет</p>
      </div>
      <div className="absolute font-['Open_Sans:Regular',_'Noto_Sans:Regular',_sans-serif] font-normal leading-[0] text-[#6b6773] text-[14px] top-[669px] translate-x-[100%] whitespace-nowrap" data-node-id="263:1781" style={{ fontVariationSettings: "'wdth' 100", right: "calc(33.333% + 97.333px)" }}>
        <p className="leading-[normal]">12 000 ₸</p>
      </div>
      <div className="absolute h-[88px] left-[16px] top-[645px]" data-name="Rectangle" data-node-id="263:1782" style={{ right: "calc(66.667% + 2.667px)" }}>
        <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none size-full" src={imgRectangle} />
      </div>
      <div className="absolute h-0 left-[16px] top-[741px] w-[288px]" data-node-id="263:1783">
        <div className="absolute bottom-0 left-0 right-0 top-[-1px]">
          <img alt="" className="block max-w-none size-full" src={imgLine5} />
        </div>
      </div>
      <div className="absolute font-['Open_Sans:Bold',_sans-serif] font-bold leading-[0] text-[#6b6773] text-[14px] top-[749px] translate-x-[100%] w-[132px]" data-node-id="263:1784" style={{ fontVariationSettings: "'wdth' 100", right: "calc(16.667% + 150.667px)" }}>
        <p className="leading-[normal] whitespace-pre-wrap">Сердечное признание в любви</p>
      </div>
      <div className="absolute font-['Open_Sans:Regular',_'Noto_Sans:Regular',_sans-serif] font-normal leading-[0] text-[#6b6773] text-[14px] top-[811px] translate-x-[100%] whitespace-nowrap" data-node-id="263:1785" style={{ fontVariationSettings: "'wdth' 100", right: "calc(33.333% + 97.333px)" }}>
        <p className="leading-[normal]">12 000 ₸</p>
      </div>
      <div className="absolute h-0 left-[16px] top-[845px] w-[288px]" data-node-id="263:1786">
        <div className="absolute bottom-0 left-0 right-0 top-[-1px]">
          <img alt="" className="block max-w-none size-full" src={imgLine5} />
        </div>
      </div>
      <div className="absolute h-[88px] left-[16px] top-[749px]" data-name="Rectangle" data-node-id="263:1787" style={{ right: "calc(66.667% + 2.667px)" }}>
        <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none size-full" src={imgRectangle1} />
      </div>
      <div className="absolute bg-[rgba(255,255,255,0.6)] h-[88px] left-[16px] top-[645px]" data-name="Rectangle" data-node-id="263:1788" style={{ right: "calc(66.667% + 2.667px)" }} />
      <div className="absolute bg-[rgba(255,255,255,0.6)] h-[88px] left-[16px] top-[749px]" data-name="Rectangle" data-node-id="263:1789" style={{ right: "calc(66.667% + 2.667px)" }} />
      <div className="absolute h-[24px] top-[645px] w-[44px]" data-node-id="263:1790" style={{ left: "calc(83.333% - 6.667px)" }}>
        <img alt="" className="block max-w-none size-full" src={imgGroup132} />
      </div>
      <div className="absolute h-[24px] top-[749px] w-[44px]" data-node-id="263:1793" style={{ left: "calc(83.333% - 6.667px)" }}>
        <img alt="" className="block max-w-none size-full" src={imgGroup132} />
      </div>
      <div className="absolute font-['Open_Sans:Bold',_sans-serif] font-bold leading-[0] text-[#6b6773] text-[14px] top-[853px] translate-x-[100%] w-[132px]" data-node-id="263:1796" style={{ fontVariationSettings: "'wdth' 100", right: "calc(16.667% + 150.667px)" }}>
        <p className="leading-[normal] whitespace-pre-wrap">Красный букет</p>
      </div>
      <div className="absolute font-['Open_Sans:Regular',_'Noto_Sans:Regular',_sans-serif] font-normal leading-[0] text-[#6b6773] text-[14px] top-[877px] translate-x-[100%] whitespace-nowrap" data-node-id="263:1797" style={{ fontVariationSettings: "'wdth' 100", right: "calc(33.333% + 97.333px)" }}>
        <p className="leading-[normal]">12 000 ₸</p>
      </div>
      <div className="absolute h-[88px] left-[16px] top-[853px]" data-name="Rectangle" data-node-id="263:1798" style={{ right: "calc(66.667% + 2.667px)" }}>
        <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none size-full" src={imgRectangle} />
      </div>
      <div className="absolute h-0 left-[16px] top-[949px] w-[288px]" data-node-id="263:1799">
        <div className="absolute bottom-0 left-0 right-0 top-[-1px]">
          <img alt="" className="block max-w-none size-full" src={imgLine5} />
        </div>
      </div>
      <div className="absolute font-['Open_Sans:Bold',_sans-serif] font-bold leading-[0] text-[#6b6773] text-[14px] top-[957px] translate-x-[100%] w-[132px]" data-node-id="263:1800" style={{ fontVariationSettings: "'wdth' 100", right: "calc(16.667% + 150.667px)" }}>
        <p className="leading-[normal] whitespace-pre-wrap">Сердечное признание в любви</p>
      </div>
      <div className="absolute font-['Open_Sans:Regular',_'Noto_Sans:Regular',_sans-serif] font-normal leading-[0] text-[#6b6773] text-[14px] top-[1019px] translate-x-[100%] whitespace-nowrap" data-node-id="263:1801" style={{ fontVariationSettings: "'wdth' 100", right: "calc(33.333% + 97.333px)" }}>
        <p className="leading-[normal]">12 000 ₸</p>
      </div>
      <div className="absolute h-0 left-[16px] top-[1053px] w-[288px]" data-node-id="263:1802">
        <div className="absolute bottom-0 left-0 right-0 top-[-1px]">
          <img alt="" className="block max-w-none size-full" src={imgLine5} />
        </div>
      </div>
      <div className="absolute h-[88px] left-[16px] top-[957px]" data-name="Rectangle" data-node-id="263:1803" style={{ right: "calc(66.667% + 2.667px)" }}>
        <img alt="" className="absolute inset-0 max-w-none object-50%-50% object-cover pointer-events-none size-full" src={imgRectangle1} />
      </div>
      <div className="absolute bg-[rgba(255,255,255,0.6)] h-[88px] left-[16px] top-[853px]" data-name="Rectangle" data-node-id="263:1804" style={{ right: "calc(66.667% + 2.667px)" }} />
      <div className="absolute bg-[rgba(255,255,255,0.6)] h-[88px] left-[16px] top-[957px]" data-name="Rectangle" data-node-id="263:1805" style={{ right: "calc(66.667% + 2.667px)" }} />
      <div className="absolute h-[24px] top-[853px] w-[44px]" data-node-id="263:1806" style={{ left: "calc(83.333% - 6.667px)" }}>
        <img alt="" className="block max-w-none size-full" src={imgGroup132} />
      </div>
      <div className="absolute h-[24px] top-[957px] w-[44px]" data-node-id="263:1809" style={{ left: "calc(83.333% - 6.667px)" }}>
        <img alt="" className="block max-w-none size-full" src={imgGroup132} />
      </div>
    </div>
    </div>
  );
}