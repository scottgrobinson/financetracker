<script>
import { useSnackbarStore } from "@/stores/SnackbarStore";
import { mapStores } from "pinia";

export default {
  data() {
    return {
      navDrawer: false,
    };
  },
  computed: {
    ...mapStores(useSnackbarStore),
    showSnackbar: {
      get() {
        return this.snackbarStore.showSnackbar;
      },
      set(value) {
        this.snackbarStore.showSnackbar = value;
      },
    },
    snackbarMessage() {
      return this.snackbarStore.snackbarMessage;
    },
  },
  methods: {
    closeSnackbar() {
      this.snackbarStore.closeSnackbar();
    },
  },
};
</script>

<template>
  <v-app>
    <v-app-bar app color="grey-darken-3" dark clipped-left>
      <v-app-bar-nav-icon @click="navDrawer = !navDrawer"></v-app-bar-nav-icon>
      <v-toolbar-title>Finance Tracker</v-toolbar-title>
    </v-app-bar>

    <v-navigation-drawer app v-model="navDrawer" absolute clipped>
      <v-list-item
        link
        title="Accounts"
        to="/"
        @click="navDrawer = false"
      ></v-list-item>
      <v-list-item
        link
        title="Rules"
        to="/rules"
        @click="navDrawer = false"
      ></v-list-item>
      <v-list-item
        link
        title="Reports"
        to="/reports"
        @click="navDrawer = false"
      ></v-list-item>
    </v-navigation-drawer>
    <v-main fluid fill-height>
      <v-container fluid fill-height>
        <RouterView />
        <v-snackbar v-model="showSnackbar">
          {{ snackbarMessage }}

          <template v-slot:actions>
            <v-btn color="red" variant="text" @click="closeSnackbar">
              Close
            </v-btn>
          </template>
        </v-snackbar>
      </v-container>
    </v-main>
  </v-app>
</template>
