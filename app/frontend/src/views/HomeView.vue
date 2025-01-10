<script>
import { doApiCall } from "@/helpers/doApiCall";
import ButtonWithState from "../components/ButtonWithState.vue";
import TagChip from "../components/TagChip.vue";

export default {
  components: {
    ButtonWithState,
    TagChip,
  },
  data() {
    return {
      // Button states
      btnLoadingStates: {
        updateBalances: false,
        updateTransactions: false,
      },
      btnIconStates: {
        updateBalances: null,
        updateTransactions: null,
      },

      // Accounts & transactions
      accounts: null,
      transactions: null,
      selectedAccount: null,
      tableHeaders: [
        { title: "Date/Time", value: "datetime", sortable: true },
        {
          title: "Description",
          value: "remittance_information",
          sortable: true,
        },
        { title: "Amount", value: "amount", sortable: true },
        { title: "Tags", value: "tags", sortable: true },
      ],

      // Tag handling
      newTag: "",
      dialogVisible: false,
      transactionToTag: null,
      newRuleFormValid: false,
      requiredRule: [
        (value) => {
          if (value) return true;

          return "Field is required";
        },
      ],

      search: "",
    };
  },
  methods: {
    /**
     * Wraps doApiCall in state management for buttons (loading & icon states).
     */
    async doAction(actionKey, url) {
      this.btnLoadingStates[actionKey] = true;
      this.btnIconStates[actionKey] = null;

      try {
        await doApiCall(url, "GET", false, null, "t");
        this.btnIconStates[actionKey] = "success";
      } catch (err) {
        console.error(err);
        this.btnIconStates[actionKey] = "error";
      } finally {
        this.btnLoadingStates[actionKey] = false;
      }
    },

    async handleUpdateBalances() {
      await this.doAction("updateBalances", "/api/account/update");
    },

    async handleUpdateTransactions() {
      await this.doAction("updateTransactions", "/api/transaction/update");
    },

    formatCurrency(value) {
      return value.toLocaleString("en-gb", {
        style: "currency",
        currency: "USD",
      });
    },

    async getAccounts() {
      this.accounts = await doApiCall(
        `/api/account/`,
        "GET",
        true,
        null,
        "fetching accounts"
      );
    },

    async getAccountTransactions() {
      let account = await doApiCall(
        `/api/account/${this.selectedAccount}`,
        "GET",
        true,
        null,
        "fetching account transactions"
      );
      this.transactions = account.transactions;
    },

    /**
     * Opens the Add Tag dialog for a given transaction.
     */
    openAddTagDialog(transaction) {
      this.transactionToTag = transaction;
      this.newTag = "";
      this.dialogVisible = true;
    },

    /**
     * Adds the new tag to the selected transaction once confirmed.
     * Ideally, you'd also update the backend via API here.
     */
    confirmAddTag() {
      if (!this.newTag.trim()) return;

      this.transactionToTag.tags.push(this.newTag.trim());
      this.newTag = "";
      this.dialogVisible = false;
      this.transactionToTag = null;
    },

    removeTag(transaction, tag) {
      const index = transaction.tags.indexOf(tag);
      transaction.tags.splice(index, 1);
    },
  },
  created() {
    this.getAccounts();
    this.selectedAccount = this.$route.params.accountid;
    if (this.selectedAccount) {
      this.getAccountTransactions();
    }
  },
  watch: {
    $route() {
      this.selectedAccount = this.$route.params.accountid;
      this.transactions = null;
      if (this.selectedAccount) {
        this.getAccountTransactions();
      }
    },
  },
};
</script>

<template>
  <div class="d-flex align-center justify-space-between flex-wrap mb-4">
    <!-- Chips for Accounts on the left -->
    <div class="d-flex flex-wrap ga-2">
      <v-chip
        v-for="account in accounts"
        :key="account._id"
        :to="'/account/' + account.id"
        :color="account.id == this.selectedAccount ? 'secondary' : ''"
      >
        {{ account.description }}&nbsp;
        <strong>
          {{
            new Intl.NumberFormat("en-GB", {
              style: "currency",
              currency: "GBP",
            }).format(account.balance)
          }}
        </strong>
      </v-chip>
    </div>

    <!-- Buttons on the right -->
    <div>
      <ButtonWithState
        class="mr-2"
        text="Update Balances"
        :loadingState="btnLoadingStates.updateBalances"
        :iconState="btnIconStates.updateBalances"
        @click="handleUpdateBalances"
      />
      <ButtonWithState
        text="Update Transactions"
        :loadingState="btnLoadingStates.updateTransactions"
        :iconState="btnIconStates.updateTransactions"
        @click="handleUpdateTransactions"
      />
    </div>
  </div>

  <v-text-field
    v-if="transactions"
    v-model="search"
    label="Search"
    prepend-inner-icon="mdi-magnify"
    variant="outlined"
    hide-details
    single-line
  ></v-text-field>

  <!-- Data Table -->
  <v-data-table
    class="mt-4"
    :items="transactions"
    v-if="transactions && transactions.length"
    :headers="tableHeaders"
    :search="search"
    no-data-text="No matching transactions found"
  >
    <template v-slot:item.datetime="{ item }">
      <span>
        {{
          new Date(item.datetime).toLocaleDateString("en-gb", {
            year: "numeric",
            month: "long",
            day: "numeric",
          })
        }}
      </span>
    </template>

    <template v-slot:item.amount="{ item }">
      <span>
        {{
          new Intl.NumberFormat("en-GB", {
            style: "currency",
            currency: "GBP",
          }).format(item.amount)
        }}
      </span>
    </template>

    <!-- Tags -->
    <template v-slot:item.tags="{ item }">
      <div class="d-flex align-center flex-wrap ga-1">
        <!-- Existing Tags -->
        <TagChip
          v-for="(tag, index) in item.tags"
          :key="index"
          :tag="tag"
          :transaction="item"
          @removeTag="removeTag"
        />

        <!-- Chip for adding a new tag -->
        <v-chip
          text-color="white"
          small
          class="cursor-pointer"
          @click="openAddTagDialog(item)"
        >
          <v-icon small>mdi-plus</v-icon>
        </v-chip>
      </div>
    </template>
  </v-data-table>

  <!-- Dialog for adding a new tag -->
  <v-dialog v-model="dialogVisible" max-width="400px">
    <v-card>
      <v-card-title>Add Tag</v-card-title>
      <v-form ref="newRuleForm" v-model="newRuleFormValid" lazy-validation>
        <v-card-text>
          <v-text-field
            label="New Tag"
            :rules="requiredRule"
            v-model="newTag"
            @keyup.enter="confirmAddTag"
            hint="Required field"
            persistent-hint
            required
          />
        </v-card-text>
      </v-form>
      <v-card-actions>
        <v-spacer />
        <v-btn text @click="dialogVisible = false">Cancel</v-btn>
        <v-btn
          color="primary"
          text
          :disabled="!newRuleFormValid"
          @click="confirmAddTag"
          >Add</v-btn
        >
      </v-card-actions>
    </v-card>
  </v-dialog>
</template>
