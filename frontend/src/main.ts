import { createApp } from 'vue';
import { Quasar, Notify, Loading, Dialog, LocalStorage } from 'quasar';
import { createPinia } from 'pinia';

import App from './App.vue';
import router from './router';

// Import icon libraries
import '@quasar/extras/roboto-font/roboto-font.css';
import '@quasar/extras/material-icons/material-icons.css';
import '@quasar/extras/mdi-v7/mdi-v7.css';
import '@quasar/extras/fontawesome-v6/fontawesome-v6.css';

// Import Quasar css
import 'quasar/dist/quasar.css';

// Import app styles
import './styles/app.scss';

const app = createApp(App);

app.use(Quasar, {
  plugins: {
    Notify,
    Loading,
    Dialog,
    LocalStorage,
  },
  config: {
    notify: {},
    loading: {},
  },
});

app.use(createPinia());
app.use(router);

app.mount('#app');
