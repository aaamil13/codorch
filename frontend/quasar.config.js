import { configure } from 'quasar/wrappers';

export default configure((ctx) => {
  return {
    eslint: {
      warnings: true,
      errors: true
    },

    boot: [
      'axios',
    ],

    css: [
      'app.scss'
    ],

    extras: [
      'roboto-font',
      'material-icons',
    ],

    build: {
      target: {
        browser: ['es2022', 'firefox115', 'chrome115', 'safari14'],
        node: 'node20'
      },

      vueRouterMode: 'history',
      
      vitePlugins: [
        ['@vitejs/plugin-vue', {
          template: { transformAssetUrls }
        }]
      ]
    },

    devServer: {
      open: true,
      port: ctx.mode.ssr ? 9100 : 9000
    },

    framework: {
      config: {},
      
      plugins: [
        'Notify',
        'Dialog',
        'Loading'
      ]
    },

    animations: [],

    ssr: {
      pwa: false,
      prodPort: 3000,
      middlewares: [
        'render'
      ]
    },

    pwa: {
      workboxMode: 'generateSW',
      injectPwaMetaTags: true,
      swFilename: 'sw.js',
      manifestFilename: 'manifest.json',
      useCredentialsForManifestTag: false,
    },

    cordova: {},
    capacitor: {
      hideSplashscreen: true
    },
    electron: {
      inspectPort: 5858,
      bundler: 'packager',
      builder: {
        appId: 'codorch-frontend'
      }
    },

    bex: {
      contentScripts: [
        'my-content-script'
      ],
    }
  }
});

const transformAssetUrls = {
  base: null,
  includeAbsolute: false,
  tags: {
    video: ['src', 'poster'],
    source: ['src'],
    img: ['src'],
    image: ['xlink:href', 'href'],
    use: ['xlink:href', 'href']
  }
};