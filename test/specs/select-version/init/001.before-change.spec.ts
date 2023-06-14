import { expect as expectWDIO } from '@wdio/globals'
import Main from '../../../pageobjects/main.page'
import SelectVersion from '../../../pageobjects/select-version.page'

// eslint-disable-next-line no-undef
describe('SelectVersionPage: before change', () => {
  
  // eslint-disable-next-line no-undef
  it('should be in MainPage', async () => { 
    await expectWDIO(Main.page).toBeDisplayed()
  })

  // eslint-disable-next-line no-undef
  it('should not be in SelectVersionPage', async () => { 
    await expectWDIO(SelectVersion.page).not.toBeDisplayed()
  })
})
