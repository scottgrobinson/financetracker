<script>
import TagChip from "@/components/TagChip.vue";
import { readonly } from "vue";

export default {
  name: "TransactionTable",
  components: { TagChip },
  props: {
    transactions: { type: Array, required: true },
    personsList: { type: Array },
    search: { type: String, default: "" },
    readonly: { type: Boolean, default: false },
    showtotal: { type: Boolean, default: false },
  },
  data() {
    return {
      headers: [
        { title: "Date/Time", value: "datetime", sortable: true },
        {
          title: "Description",
          value: "remittance_information",
          sortable: true,
        },
        { title: "Amount", value: "amount", sortable: true },
        { title: "Assignees", value: "assignees", sortable: true },
        { title: "Tags", value: "tags", sortable: true },
      ],
    };
  },
  methods: {
    formatDate(dt) {
      return new Date(dt).toLocaleDateString("en-gb", {
        year: "numeric",
        month: "long",
        day: "numeric",
      });
    },
    formatCurrency(val) {
      return new Intl.NumberFormat("en-GB", {
        style: "currency",
        currency: "GBP",
      }).format(val);
    },
    onUpdateAssignees(item, newList) {
      this.$emit("update-assignees", item, newList);
    },
    onRemoveTag(item, tag) {
      this.$emit("remove-tag", item, tag);
    },
  },
};
</script>

<template>
  <v-data-table
    class="mt-4"
    :items="transactions"
    :headers="headers"
    :search="search"
    no-data-text="No matching transactions found"
  >
    <!-- Date column -->
    <template #item.datetime="{ item }">
      <span>{{ formatDate(item.datetime) }}</span>
    </template>

    <!-- Amount column -->
    <template #item.amount="{ item }">
      <span>{{ formatCurrency(item.amount) }}</span>
    </template>

    <!-- Assignees column -->
    <template #item.assignees="{ item }">
      <v-combobox
        v-if="!readonly"
        v-model="item.assignees"
        :items="personsList"
        item-title="name"
        item-value="id"
        chips
        multiple
        dense
        hide-details
        @update:modelValue="(newList) => onUpdateAssignees(item, newList)"
      />
      <TagChip
        v-else
        v-for="person in item.assignees"
        :key="person.id"
        :tag="person.name"
        readonly
      />
    </template>

    <!-- Tags column -->
    <template #item.tags="{ item }">
      <div class="d-flex align-center flex-wrap ga-1">
        <TagChip
          v-for="tag in item.tags"
          :key="tag"
          :tag="tag"
          :transaction="item"
          @removeTag="(tag) => onRemoveTag(item, tag)"
          :readonly="readonly"
        />
        <v-chip
          v-if="!readonly"
          text-color="white"
          small
          class="cursor-pointer"
          @click="() => $emit('open-add-tag-dialog', item)"
        >
          <v-icon small>mdi-plus</v-icon>
        </v-chip>
      </div>
    </template>

    <!-- Footer total row -->
    <template #body.append="{ items }">
      <tr v-if="(search && items.length) || showtotal">
        <td v-for="header in headers" :key="header.value">
          <div v-if="header.value === 'remittance_information'">
            <strong>Total</strong>
          </div>
          <div v-else-if="header.value === 'amount'">
            {{
              formatCurrency(
                items.reduce((acc, i) => acc + parseFloat(i.amount || 0), 0)
              )
            }}
          </div>
        </td>
      </tr>
    </template>
  </v-data-table>
</template>
