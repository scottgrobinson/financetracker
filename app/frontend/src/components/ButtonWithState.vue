<script>
export default {
  props: {
    text: { type: String, required: true },
    loadingState: { type: Boolean, required: true },
    iconState: { type: String, required: false },
  },

  data() {
    return {
      timerId: null,
      localIconState: this.iconState,
    };
  },

  watch: {
    iconState(newVal) {
      // Update local copy
      this.localIconState = newVal;

      // If there's no icon state, no need to set a timer
      if (!newVal) {
        return;
      }

      // Clear any existing timer
      if (this.timerId) {
        clearTimeout(this.timerId);
      }

      // Start a new 5-second timer to reset iconState
      this.timerId = setTimeout(() => {
        // We reset our local copy
        this.localIconState = null;
        // If you need to notify the parent, emit an event:
      }, 2500);
    },
  },

  beforeUnmount() {
    // Clear timer on component unmount
    if (this.timerId) {
      clearTimeout(this.timerId);
    }
  },
};
</script>

<template>
  <v-btn :loading="loadingState" :disabled="loadingState">
    <span>{{ text }}</span>
    <template v-if="localIconState === 'success'">
      <v-icon right>mdi-check</v-icon>
    </template>
    <template v-else-if="localIconState === 'error'">
      <v-icon right>mdi-close</v-icon>
    </template>
  </v-btn>
</template>
