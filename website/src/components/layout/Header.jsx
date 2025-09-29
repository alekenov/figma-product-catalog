import React from 'react';

// Asset URLs from Figma
const logoAssets = {
  img: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/963650d0-69f2-407d-8cab-29edba79f5b4/figma%3Aasset/09b61cbf310efc904747a1a14e4f7ddb6a564f83.svg",
  img1: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/963650d0-69f2-407d-8cab-29edba79f5b4/figma%3Aasset/43e94986ab4d490f8a941ce94829a40c40724106.svg",
  img2: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/963650d0-69f2-407d-8cab-29edba79f5b4/figma%3Aasset/00000a9c4130a3387285998af026d6a532b8796f.svg",
  img3: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/963650d0-69f2-407d-8cab-29edba79f5b4/figma%3Aasset/1ec75da914312816a1e68562c2bf076b0abb793c.svg",
  img4: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/963650d0-69f2-407d-8cab-29edba79f5b4/figma%3Aasset/a89a83bb08bd8c4f65d40c9458a163f72e94ea7a.svg",
  img5: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/963650d0-69f2-407d-8cab-29edba79f5b4/figma%3Aasset/f5edd788272bdbba5c1e838b22c620fa53a0f931.svg",
  img6: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/963650d0-69f2-407d-8cab-29edba79f5b4/figma%3Aasset/6152ef1dca279283a755e6aceb482151e2ea9d3d.svg",
  img7: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/963650d0-69f2-407d-8cab-29edba79f5b4/figma%3Aasset/9b42ef274c264733ab711920c6cdce9a2311528d.svg",
  img8: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/963650d0-69f2-407d-8cab-29edba79f5b4/figma%3Aasset/7f1a0ee26ed2a1e1c4b5b68a8942dbe6417dd91c.svg",
  img9: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/963650d0-69f2-407d-8cab-29edba79f5b4/figma%3Aasset/5022742f332fcfe002f81553d94351f6c69bdebd.svg",
  img10: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/963650d0-69f2-407d-8cab-29edba79f5b4/figma%3Aasset/5ee185efd97f0d673b49813c8d295f46a38b9d6a.svg",
  img11: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/963650d0-69f2-407d-8cab-29edba79f5b4/figma%3Aasset/68e5913b93c884743dd358594c3b7482102627ea.svg",
  img12: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/963650d0-69f2-407d-8cab-29edba79f5b4/figma%3Aasset/089a7d7f8c1b4f58d318561a12124646e6fbcc17.svg",
  img13: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/963650d0-69f2-407d-8cab-29edba79f5b4/figma%3Aasset/d28c3fb412d7789dae22e3a18fe9d5595c11efbf.svg",
  imgIconArrow: "https://figma-alpha-api.s3.us-west-2.amazonaws.com/mcp/get_code/assets/963650d0-69f2-407d-8cab-29edba79f5b4/figma%3Aasset/d15a09539b775fd3d1f51f075b59da48d7c6b0b6.svg"
};

function IconsInHeaderMobile({ type = "Contact", state = "Default", notification = "No" }) {
  if (type === "Catalog" && state === "Default" && notification === "No") {
    return (
      <button className="block cursor-pointer relative size-full">
        <div className="absolute inset-0 overflow-clip">
          <div className="absolute bottom-1/4 left-[8.33%] right-[8.33%] top-1/4">
            <img alt="" className="block max-w-none size-full" src={logoAssets.img} />
          </div>
        </div>
      </button>
    );
  }
  return (
    <button className="block cursor-pointer relative size-full">
      <div className="absolute inset-0 overflow-clip">
        <div className="absolute inset-[8.5%_8.71%_8.71%_8.26%]">
          <img alt="" className="block max-w-none size-full" src={logoAssets.img1} />
        </div>
      </div>
    </button>
  );
}

function HeaderMobileNew({ address = "No", location = "Yes" }) {
  return (
    <div className="content-stretch flex flex-col gap-4 items-start relative size-full">
      <div className="box-border content-stretch flex flex-col gap-[2px] items-start pb-0 pt-[14px] px-0 relative shrink-0 w-full">
        <div aria-hidden="true" className="absolute border-border-grey-light border-b border-l-0 border-r-0 border-solid border-t-0 inset-0 pointer-events-none" />
        <div className="content-stretch flex items-center justify-between relative shrink-0 w-full">
          <div className="content-stretch flex flex-col items-start justify-center relative shrink-0">
            <div className="h-[40px] relative shrink-0 w-[108px]">
              <div className="absolute contents left-0 right-0 top-0">
                <div className="absolute contents left-[74.58%] right-[18.91%] top-[2.16px]">
                  <div className="absolute h-[25.603px] left-[74.58%] right-[18.91%] top-[2.16px]">
                    <img alt="" className="block max-w-none size-full" src={logoAssets.img2} />
                  </div>
                </div>
                <div className="absolute contents left-[76.44%] right-[12.35%] top-[14.97px]">
                  <div className="absolute h-[12.676px] left-[76.44%] right-[12.35%] top-[14.97px]">
                    <img alt="" className="block max-w-none size-full" src={logoAssets.img3} />
                  </div>
                </div>
                <div className="absolute contents left-[88.16%] right-0 top-[14.99px]">
                  <div className="absolute h-[12.578px] left-[88.16%] right-0 top-[14.99px]">
                    <img alt="" className="block max-w-none size-full" src={logoAssets.img4} />
                  </div>
                </div>
                <div className="absolute contents left-0 right-[75.16%] top-0">
                  <div className="absolute h-[28.558px] left-0 right-[75.16%] top-0">
                    <img alt="" className="block max-w-none size-full" src={logoAssets.img5} />
                  </div>
                </div>
                <div className="absolute contents left-[22.47%] right-[65.96%] top-[14.82px]">
                  <div className="absolute h-[13.218px] left-[22.47%] right-[65.96%] top-[14.82px]">
                    <img alt="" className="block max-w-none size-full" src={logoAssets.img6} />
                  </div>
                </div>
                <div className="absolute contents left-[33.75%] right-[54.9%] top-[15.12px]">
                  <div className="absolute h-[12.958px] left-[33.75%] right-[54.9%] top-[15.12px]">
                    <img alt="" className="block max-w-none size-full" src={logoAssets.img7} />
                  </div>
                </div>
                <div className="absolute contents left-[48.55%] right-[46.77%] top-[9.73px]">
                  <div className="absolute h-[18.361px] left-[48.55%] right-[46.77%] top-[9.73px]">
                    <img alt="" className="block max-w-none size-full" src={logoAssets.img8} />
                  </div>
                </div>
                <div className="absolute contents left-[46.09%] right-[44.23%] top-[15.07px]">
                  <div className="absolute h-[1.345px] left-[46.09%] right-[44.23%] top-[15.07px]">
                    <img alt="" className="block max-w-none size-full" src={logoAssets.img9} />
                  </div>
                </div>
                <div className="absolute contents left-[50.6%] right-[31.36%] top-[15.15px]">
                  <div className="absolute h-[24.852px] left-[50.6%] right-[31.36%] top-[15.15px]">
                    <img alt="" className="block max-w-none size-full" src={logoAssets.img10} />
                  </div>
                </div>
                <div className="absolute h-[2.745px] left-[69.85%] right-[27.03%] top-[25.34px]">
                  <img alt="" className="block max-w-none size-full" src={logoAssets.img11} />
                </div>
              </div>
            </div>
          </div>
          <div className="content-stretch cursor-pointer flex gap-[16px] items-center relative shrink-0">
            <button className="block overflow-visible relative shrink-0 size-[24px]">
              <div className="absolute inset-0 overflow-clip">
                <div className="absolute inset-[8.5%_8.71%_8.71%_8.26%]">
                  <img alt="" className="block max-w-none size-full" src={logoAssets.img1} />
                </div>
              </div>
            </button>
            <button className="block overflow-visible relative shrink-0 size-[24px]">
              <div className="absolute inset-0 overflow-clip">
                <div className="absolute inset-[8.31%_8.48%_8.31%_8.6%]">
                  <img alt="" className="block max-w-none size-full" src={logoAssets.img12} />
                </div>
              </div>
            </button>
            <button className="block overflow-visible relative shrink-0 size-[24px]">
              <div className="absolute inset-0 overflow-clip">
                <div className="absolute inset-[8.33%_14.57%_8.23%_10.42%]">
                  <img alt="" className="block max-w-none size-full" src={logoAssets.img13} />
                </div>
              </div>
            </button>
            <button className="block overflow-visible relative shrink-0 size-[24px]">
              <IconsInHeaderMobile type="Catalog" />
            </button>
          </div>
        </div>
        <div className="box-border content-stretch flex gap-[2px] items-start justify-center pb-4 pl-0 pr-3 pt-[6px] relative rounded-full shrink-0">
          <div className="relative shrink-0 size-[19px]">
            <img alt="" className="block max-w-none size-full" src={logoAssets.imgIconArrow} />
          </div>
          <div className="font-sans font-normal leading-[0] relative shrink-0 text-[0px] text-text-black whitespace-nowrap">
            <p className="text-body-2">
              <span className="font-semibold leading-[1.2] tracking-[0.1px]">
                Астана
              </span>
              <span className="leading-[normal]">, уточните адрес доставки...</span>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Header() {
  return (
    <div className="content-stretch flex flex-col gap-[16px] items-start relative size-full">
      <HeaderMobileNew />
    </div>
  );
}