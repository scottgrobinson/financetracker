import { defineStore } from "pinia";

export const useSnackbarStore = defineStore("snackbar", {
  state: () => ({
    showSnackbar: false,
    snackbarMessage: "",
  }),
  actions: {
    openSnackbar(message) {
      this.snackbarMessage = message;
      this.showSnackbar = true;
    },
    closeSnackbar() {
      this.showSnackbar = false;
      this.snackbarMessage = "";
    },
  },
});
