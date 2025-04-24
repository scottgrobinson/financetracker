<script>
import { doApiCall } from "@/helpers/doApiCall";
import { readonly } from "vue";

export default {
  props: {
    tag: { type: String, required: true },
    transaction: { type: Object },
    readonly: { type: Boolean, default: false },
  },
  data() {
    return {
      isRemoving: false,
    };
  },
  emits: ["removeTag"],
  methods: {
    async removeTag(transaction, tag) {
      this.isRemoving = true;
      try {
        await doApiCall(
          `/api/account/${transaction.account}/${transaction.id}/tag/${tag}`,
          "DELETE",
          false,
          null,
          "removing tag"
        );
        this.$emit("removeTag", transaction, tag);
      } catch (err) {
        console.error(err);
      } finally {
        this.isRemoving = false;
      }
    },
  },
};
</script>

<template>
  <v-chip>
    {{ tag }}<template v-if="!readonly">&nbsp;</template>
    <v-icon
      v-if="!readonly"
      right
      x-small
      @click.stop="removeTag(transaction, tag)"
      :class="{ 'icon-rotating': isRemoving }"
    >
      {{ isRemoving ? "mdi-loading" : "mdi-close" }}
    </v-icon>
  </v-chip>
</template>

<style>
.icon-rotating {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
