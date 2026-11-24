import {expect,test} from '@playwright/test';

test('Pages landing opens the Neon-backed wardrobe and demo',async({page},testInfo)=>{
  const errors=[];
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto('./');
  await expect(page.getByRole('heading',{level:1})).toContainText('Dress for the');
  const hero=page.locator('.hero-figure img');
  await expect(hero).toBeVisible();
  await expect.poll(()=>hero.evaluate(image=>image.naturalWidth)).toBeGreaterThan(0);
  await page.getByRole('link',{name:'Open my wardrobe',exact:true}).first().click();
  await expect(page.getByRole('heading',{name:'Fitting room',exact:true})).toBeVisible();
  await page.getByLabel('Time (WIB)').fill(new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Jakarta',hour:'2-digit',minute:'2-digit',hourCycle:'h23'}).format(new Date()));
  await page.getByRole('button',{name:'Find outfits'}).click();
  await expect(page.getByRole('heading',{name:'Best match',exact:true})).toBeVisible({timeout:15000});
  await page.getByRole('link',{name:'My wardrobe',exact:true}).click();
  await expect(page.getByRole('heading',{name:'My wardrobe',exact:true})).toBeVisible();
  await expect(page.getByText('Pink oxford shirt',{exact:true}).first()).toBeVisible();
  await page.getByRole('link',{name:'Demo',exact:true}).click();
  await expect(page.getByText('Database neon',{exact:true})).toBeVisible();
  await expect(page.getByLabel('Product').locator('option')).toHaveCount(5);
  await page.screenshot({path:testInfo.outputPath('desktop.png'),fullPage:true});
  expect(errors).toEqual([]);
});

test('mobile landing and wardrobe remain within the viewport',async({page},testInfo)=>{
  await page.setViewportSize({width:390,height:844});
  await page.goto('./');
  await expect(page.getByRole('heading',{level:1})).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  await page.getByRole('link',{name:'Open my wardrobe',exact:true}).first().click();
  await expect(page.getByRole('heading',{name:'Fitting room',exact:true})).toBeVisible();
  await expect(page.getByRole('button',{name:'Find outfits'})).toBeVisible();
  expect(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1)).toBe(true);
  await page.screenshot({path:testInfo.outputPath('mobile.png'),fullPage:true});
});
