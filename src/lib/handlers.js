import DownloadHandler from './download'
import SDCardHandler from './sdcard'
import UsbDetectionHandler from './usb-detection'
import VerifyOfficialReleasesHandler from './verify-official-releases'
/**
 * Function to handle when
 * window is started
 *
 * @param win
 * @apram store
 */
function handleWindowStarted (win, store) {
  return function (_event, action) {
    store.set('state', 'running')
    const version = store.get('appVersion')
    const state = store.get('state')
    win.webContents.send('window:log:info', `Krux installer ${version} ${state}`)
    win.webContents.send('window:log:info', 'page: MainPage')
  }
}


/**
 * Function to handle when
 * wants to verify official releases
 *
 * @param win
 * @apram store
 */
function handleVerifyOfficialReleases (win, store) {
  return async function (_event, action) {
    const handler = new VerifyOfficialReleasesHandler(win, store)
    const releases = await handler.fetchReleases()
    let list = store.get('versions')

    // verify for new releases if length of fetch is greater than the local list
    if (list === undefined || list.length === 0 || list.length < (Object.keys(releases)).length) {
      const __list__ = _.map(releases, (r) => {
        const version = r.ref.split('tags/')[1]
        return `selfcustody/krux/releases/tag/${version}`
      })
      __list__.push('odudex/krux_binaries')
      store.set('versions', __list__)
      list = store.get('releases')
    }
    handler.send('window:log:info', `available releases: ${list.join(', ')}`)
    handler.send('official:releases:get', { releases: list })
  }
}

/**
 * Function to handle the setting of many config values
 *
 * @param win
 * @param store
 */
function handleStoreSet (win, store) {
  return function (_event, action) {
    if (
      action.key !== 'appVersion' ||
      action.key !== 'resources' ||
      action.key === 'state' ||
      action.key !== 'versions'
    ) {
      store.set(action.key, action.value)
      win.webContents.send('window:log:info', `store set: ${action.key} = ${action.value}`)
      win.webContents.send('store:set:done', store.get(action.key) ? true : false)
    } else {
      throw new Error(`Forbidden: cannot set '${action.key}'`)
    }
  }
}

/**
 * Function to handle the capture of many config values
 *
 * @param win
 * @param store
 */
function handleStoreGet (win, store) {
  return function (_event, action) {
    const val = store.get(action.key)
    win.webContents.send('window:log:info', `store get: ${action.key} = ${val}`)
    win.webContents.send('store:get:done', val)
  }
}
/**
 * Function to handle usbDetection
 * of implmented devices
 *
 * @param app<ElectronApp>
 */
function handleUsbDetection (app) {
  return function (_event, action) {
    const handler = new UsbDetectionHandler(app)
    if (action === 'detect') {
      handler.send('window:log:info', 'Activating usb detection')
      handler.activate()
      handler.send('window:log:info', 'Starting usb detection')
      handler.detect()
    } else if (action === 'stop') {
      handler.send('window:log:info', 'Starting usb deactvation')
      handler.deactivate()
    } else {
      throw new Error(`UsbDetectionHandler action '${action}' not implemented`)
    }
  }
}


/**
 * Function to handle mount,
 * umount and copy files to SDCard
 *
 * @param app<ElectronApp>
 */
function handleSDCard (app) {
  return async function (_event, args) {
    const handler = new SDCardHandler(app, process.platform)
    handler.send('window:log:info', `Starting sdcard '${args.action}' action`)
    if (args.action === 'detect') {
      await handler.onDetection()
    } else if (args.action === 'mount' || args.action === 'umount') {
      await handler.onAction(args.action)
    } else if (args.action === 'copyto') {
      await handler.onWrite(args.origin, args.destination)
    } else {
      throw new Error(`SDCardHandler ${action} not implemented`)
    }
  }
}

/*
* Function to handle downloads
* when user select to build or flash
* prebuiltin binaries.
*
* @param fileanme: String
*/
function handleDownload (app, store) {
  return async function (_event, options) {
    const handler = new DownloadHandler(app, store, options)

    // Before starting downloading, check if exists
    await handler.setup()

    // check if resource folder not exists
    await handler.download()
  }
}

function handleOSVerify (app) {
  return function () {
    app.webContents.send('window:log:info', `OS detected: using ${process.platform}`)
    app.webContents.send('os:verify', process.platform)
  }
}

export {
  handleWindowStarted,
  handleVerifyOfficialReleases,
  handleStoreSet,
  handleStoreGet,
  handleDownload,
  handleSDCard,
  handleUsbDetection,
  handleOSVerify
}
