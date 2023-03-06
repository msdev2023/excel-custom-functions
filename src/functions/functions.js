/* global clearInterval, console, setInterval */

/**
  * Gets the stock price at the end of month.
  * @customfunction
  * @param {string} symbol Xueqiu stock symbol
  * @param {number} year Year
  * @param {number} month Month
  * @return {number} The stock price at the end of month
  */
async function getStockPrice(symbol, year, month) {
  try {
    const begin = (new Date()).getTime() + 86400000;
    const headers = {
      'Accept': 'application/json, text/plain, */*',
      'Accept-Encoding': 'gzip, deflate, br',
      'Accept-Language': 'en-US,en;q=0.9',
      'Host': 'stock.xueqiu.com',
      'Cookie': 'Hm_lpvt_1db88642e346389874251b5a1eded6e3=1677315002; Hm_lvt_1db88642e346389874251b5a1eded6e3=1677315002; device_id=5cd089ac3a9e2e69b1297cd9fd157f70; is_overseas=0; u=751677315000770; xq_a_token=72dea7021454f100bc72154931cdd6e0a6eecd76; xq_id_token=eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJ1aWQiOi0xLCJpc3MiOiJ1YyIsImV4cCI6MTY3ODY2Njg3MCwiY3RtIjoxNjc3MzE0OTU4NTk2LCJjaWQiOiJkOWQwbjRBWnVwIn0.I1oy0HiqO2WARJqN9rTu25qq452b41K3P360FpGaLa_QTU3aqE_B3dUtXJwDgnwKKo8Nyv56MMoGQQr9LZcgditWzkjLJgL72cX6Zc3konctH8JZEs_n65GkUrXJF9z0Q9_R-mkynAuLj-xaF4vvxZITrTSQt6tXbVJVC1bZBsF6_UOPgP98KGFtUcPPGlKRZaNsXx0XubFv3lDrTtpclXaUIKg52PlOFsq4eNSTQg_ynZD0TOncmJWMfxmsrDt46uHfeLJpF3Tt8NeBbtkCMO9yeaWkay2ynpBR7mpgbw-WpzeV0b86RAflRfw4By3p1RF8HPy8_7fMH3T74lwQzQ; xq_r_token=ad070cd3d55cc70f02f135fb52765cfbe11fa994; xqat=72dea7021454f100bc72154931cdd6e0a6eecd76',
      'Origin': 'https://xueqiu.com',
      'Referer': 'https://xueqiu.com/S/'+symbol,
      'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15',
      'sec-ch-ua': '"Chromium";v="110", "Not A(Brand";v="24", "Google Chrome";v="110"',
      'sec-ch-ua-mobile': '?0',
      'sec-ch-ua-platform': '"macOS"',
      'sec-fetch-dest': 'empty',
      'sec-fetch-mode': 'cors',
      'sec-fetch-site': 'same-site'
    };
    const url = "https://stock.xueqiu.com/v5/stock/chart/kline.json?symbol="+symbol+"&begin="+begin+"&period=month&type=before&count=-284&indicator=kline,pe,pb,ps,pcf,market_capital,agt,ggt,balance"
    const response = await fetch(url, {headers: headers});
    if (!response.ok) {
      throw new Error(response.statusText)
    }
    const json = await response.json();
    const items = json["data"]["item"];
    for (let index = items.length - 1; index >= 0; index--){
      let date = new Date(items[index][0]);
      if (date.getFullYear() === year && date.getMonth() === month - 1) {
        return items[index][5];
      }
    }
  }
  catch (error) {
    return error;
  }
}
