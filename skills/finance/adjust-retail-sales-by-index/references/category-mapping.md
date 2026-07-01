# NBS Retail Category Mapping

Use these categories when mapping consumer index constituents to China's National Bureau of Statistics social retail sales table.

## Official Categories

Goods categories usually published under `其中：限额以上单位商品零售`:

- `粮油、食品类`
- `饮料类`
- `烟酒类`
- `服装、鞋帽、针纺织品类`
- `化妆品类`
- `金银珠宝类`
- `日用品类`
- `体育、娱乐用品类`
- `家用电器和音像器材类`
- `中西药品类`
- `文化办公用品类`
- `家具类`
- `通讯器材类`
- `石油及制品类`
- `汽车类`
- `建筑及装潢材料类`

Service/food-service line to include only when the user allows restaurant scope:

- `限额以上单位餐饮收入`

## Mapping Heuristics

- Food manufacturers, packaged food, dairy, meat, condiments, snack foods, supermarkets with broad food retail exposure: `粮油、食品类`.
- Bottled water, soft drinks, ready-to-drink beverages, tea drinks, beverage-heavy instant food companies: `饮料类`.
- Beer, liquor, wine, tobacco/vaping products: `烟酒类`.
- Sportswear, apparel brands, textile/garment manufacturers, footwear retailers: `服装、鞋帽、针纺织品类`.
- Cosmetics, skincare, beauty brands, functional skincare sold as consumer products: `化妆品类`.
- Jewelry, gold, watches/jewelry retail: `金银珠宝类`.
- Household paper, hygiene products, bags/luggage, home cleaning, lifestyle variety retailers: `日用品类`.
- Toys, collectibles, hobby goods, sports/outdoor goods, entertainment merchandise: `体育、娱乐用品类`.
- Home appliances, consumer electronics, TV/audio, white goods, small appliances: `家用电器和音像器材类`.
- OTC drugs, pharmacies, pharmaceutical retail: `中西药品类`.
- Stationery, office supplies, books/media retail when published as cultural/office goods: `文化办公用品类`.
- Furniture, sofa, mattress, home furnishing companies: `家具类`.
- Phones, mobile devices, telecom retail equipment: `通讯器材类`.
- Gas stations, fuel distribution/retail: `石油及制品类`.
- Auto OEMs, dealers, auto retail: `汽车类`.
- Building materials and home improvement materials: `建筑及装潢材料类`.
- Restaurants, hotpot chains, QSR, coffee/tea chains and dine-in/food-service operators: `限额以上单位餐饮收入` when restaurant scope is included.

## Exclusion Rules

- Exclude services without an official matching line, such as travel platforms, lodging, education, entertainment venues, online services, or pure internet platforms, unless the user defines a compatible NBS line.
- Exclude companies whose relevant retail business is mostly outside mainland China when the user requests mainland-only adjustment.
- Exclude categories with no included index constituent from the adjusted total and final adjusted table.

## Ambiguity Handling

- Prefer the company's primary consumer-facing revenue source over exchange/index industry labels.
- If a company materially spans two categories, pick the dominant one and note the assumption in the mapping file.
- If a category choice materially changes the retained category set or adjusted total and cannot be inferred from official filings/company profile, ask the user.
