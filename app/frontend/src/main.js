import { createApp } from "vue";

// Vuetify
import "vuetify/styles";
import "@mdi/font/css/materialdesignicons.css"; // Ensure you are using css-loader
import { createVuetify } from "vuetify";
import { aliases, mdi } from "vuetify/iconsets/mdi";
import * as components from "vuetify/components";
import * as directives from "vuetify/directives";

// Components
import App from "./App.vue";
import { createPinia } from "pinia";

import router from "./router";

const vuetify = createVuetify({
  components,
  directives,
  icons: {
    defaultSet: "mdi",
    aliases,
    sets: {
      mdi,
    },
  },
  theme: {
    defaultTheme: "dark",
  },
});

const pinia = createPinia();
const app = createApp(App).use(pinia).use(vuetify).use(router).mount("#app");
