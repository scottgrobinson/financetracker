<script>
import { doApiCall } from "@/helpers/doApiCall";
import TransactionTable from "@/components/TransactionTable.vue";

export default {
  components: {
    TransactionTable,
  },
  data() {
    return {
      formValid: false,
      form: {
        startDate: "",
        endDate: "",
        accounts: [],
        assignees: [],
        tags: [],
        includeJointTransactions: false,
      },
      accountsList: [],
      personsList: [],
      tagList: [],
      transactions: null,
      requiredRule: (v) => !!v || "Required",
    };
  },
  methods: {
    async getAccounts() {
      this.accountsList = await doApiCall(
        "/api/account/",
        "GET",
        true,
        null,
        "fetching accounts"
      );
    },
    async getPersons() {
      this.personsList = await doApiCall(
        "/api/person/",
        "GET",
        true,
        null,
        "fetching persons"
      );
    },
    async getTags() {
      this.tagList = await doApiCall(
        "/api/tag/",
        "GET",
        true,
        null,
        "fetching tags"
      );
    },
    async submitForm() {
      const transactions = await doApiCall(
        "/api/report/run",
        "POST",
        true,
        this.form,
        "fetching tags"
      );
      this.transactions = transactions.transactions;
    },
  },
  async created() {
    await this.getPersons();
    await this.getAccounts();
    await this.getTags();
  },
};
</script>

<template>
  <v-form v-model="formValid" @submit.prevent="submitForm">
    <v-row>
      <v-col cols="12" sm="6" md="2">
        <v-text-field
          v-model="form.startDate"
          label="Start Date"
          type="date"
          :rules="[requiredRule]"
        />
      </v-col>
      <v-col cols="12" sm="6" md="2">
        <v-text-field
          v-model="form.endDate"
          label="End Date"
          type="date"
          :rules="[requiredRule]"
        />
      </v-col>
      <v-col cols="12" sm="6" md="2">
        <v-combobox
          v-model="form.accounts"
          :items="accountsList"
          item-title="description"
          item-value="id"
          label="Accounts"
          chips
          multiple
          dense
          hide-details
        />
      </v-col>
      <v-col cols="12" sm="6" md="2">
        <v-combobox
          v-model="form.assignees"
          :items="personsList"
          item-title="name"
          item-value="id"
          label="Assignees"
          chips
          multiple
          dense
          hide-details
        />
      </v-col>
      <!-- NEW: operator select -->
      <v-col cols="12" sm="6" md="2">
        <v-select
          v-model="form.includeJointTransactions"
          :items="[
            { text: 'Yes', value: true },
            { text: 'No', value: false },
          ]"
          item-title="text"
          item-value="value"
          label="Include Joint Transactions"
          dense
          hide-details
        />
      </v-col>

      <v-col cols="12" sm="6" md="2">
        <v-combobox
          v-model="form.tags"
          :items="tagList"
          item-title="name"
          item-value="id"
          label="Tags"
          chips
          multiple
          dense
          hide-details
        />
      </v-col>
    </v-row>
    <v-btn type="submit" color="primary" :disabled="!formValid">Submit</v-btn>
  </v-form>
  <TransactionTable
    v-if="transactions"
    :transactions="transactions"
    readonly
    showtotal
  />
</template>
