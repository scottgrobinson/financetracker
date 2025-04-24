<script>
import { doApiCall } from "@/helpers/doApiCall";
import ButtonWithState from "@/components/ButtonWithState.vue";
import TransactionTable from "@/components/TransactionTable.vue";

export default {
  components: {
    ButtonWithState,
    TransactionTable,
  },
  computed: {
    selectedAccount() {
      if (!this.accounts || !this.selectedAccountId) return null;
      return this.accounts.find((acc) => acc.id === this.selectedAccountId);
    },
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

      // People for dropdown
      personsList: [],

      // Accounts & transactions
      accounts: null,
      transactions: null,
      selectedAccountId: null,

      // Tag handling
      newTag: "",
      tagDialogVisible: false,
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
    async doAction(actionKey, url, errorActionDescription) {
      this.btnLoadingStates[actionKey] = true;
      this.btnIconStates[actionKey] = null;

      try {
        await doApiCall(url, "GET", false, null, errorActionDescription);
        this.btnIconStates[actionKey] = "success";
      } catch (err) {
        console.error(err);
        this.btnIconStates[actionKey] = "error";
      } finally {
        this.btnLoadingStates[actionKey] = false;
      }
    },

    async handleUpdateBalances() {
      await this.doAction(
        "updateBalances",
        "/api/account/update",
        "updating balances"
      );
      await this.getAccounts();
    },

    async handleUpdateTransactions() {
      await this.doAction(
        "updateTransactions",
        "/api/transaction/update",
        "updating transactions"
      );
      await this.getAccountTransactions();
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

    async getSelectedAccountEuaExpiryURL() {
      if (!this.selectedAccount.eua_expiry_url) {
        let account = await doApiCall(
          `/api/account/${this.selectedAccountId}/generatereneweuaurl`,
          "GET",
          true,
          null,
          "fetching account generate rewnew eua url"
        );
        this.selectedAccount.eua_expiry_url = account.eua_expiry_url;
      }
    },

    async getAccountTransactions() {
      let account = await doApiCall(
        `/api/account/${this.selectedAccountId}`,
        "GET",
        true,
        null,
        "fetching account transactions"
      );
      this.transactions = account.transactions;
    },

    /**
     * Fetch list of all people for the assignee dropdown
     */
    async getPersons() {
      this.personsList = await doApiCall(
        "/api/person/",
        "GET",
        true,
        null,
        "fetching persons"
      );
    },

    /**
     * Opens the Add Tag dialog for a given transaction.
     */
    openAddTagDialog(transaction) {
      this.transactionToTag = transaction;
      this.newTag = "";
      this.tagDialogVisible = true;
    },

    /**
     * Adds the new tag to the selected transaction once confirmed.
     * Ideally, you'd also update the backend via API here.
     */
    async confirmAddTag() {
      if (!this.newTag.trim()) return;

      try {
        await doApiCall(
          `/api/account/${this.transactionToTag.account}/${this.transactionToTag.id}/tag/${this.newTag}`,
          "POST",
          false,
          null,
          "adding tag"
        );
        this.transactionToTag.tags.push(this.newTag.trim());
      } finally {
        this.newTag = "";
        this.tagDialogVisible = false;
        this.transactionToTag = null;
        this.newRuleFormValid = false;
      }
    },

    removeTag(transaction, tag) {
      const index = transaction.tags.indexOf(tag);
      transaction.tags.splice(index, 1);
    },

    async updateAssignees(transaction, assignees) {
      try {
        await doApiCall(
          `/api/account/${transaction.account}/${transaction.id}/assignees`,
          "POST",
          false,
          {
            assignees: assignees,
          },
          "updating assignees"
        );
      } catch (err) {
        console.error("Failed to update assignees:", err);
      }
    },
  },
  async created() {
    await this.getPersons();
    await this.getAccounts();
    this.selectedAccountId = this.$route.params.accountid;
    if (this.selectedAccountId) {
      if (this.selectedAccount && this.selectedAccount.eua_expired) {
        await this.getSelectedAccountEuaExpiryURL();
      }
      await this.getAccountTransactions();
    }
  },
  watch: {
    async $route() {
      this.selectedAccountId = this.$route.params.accountid;
      this.transactions = null;
      if (this.selectedAccountId) {
        this.getAccountTransactions();
        if (this.selectedAccount && this.selectedAccount.eua_expired) {
          this.getSelectedAccountEuaExpiryURL();
        }
        await this.getAccountTransactions();
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
        :key="account.id"
        :to="'/account/' + account.id"
        :color="
          account.id == this.selectedAccountId
            ? 'secondary'
            : account.eua_expired
            ? 'red'
            : ''
        "
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

  <v-alert
    density="compact"
    elevation="0"
    v-if="selectedAccount && selectedAccount.eua_expired"
    title="EUA Expired"
    type="error"
    style="margin-bottom: 16px"
    >Your access agreement for “{{ selectedAccount.description }}” has expired.
    <span v-if="selectedAccount.eua_expiry_url"
      >Renew via
      <a :href="selectedAccount.eua_expiry_url" target="_blank">{{
        selectedAccount.eua_expiry_url
      }}</a></span
    ></v-alert
  >

  <v-text-field
    v-if="transactions"
    v-model="search"
    label="Search"
    prepend-inner-icon="mdi-magnify"
    variant="outlined"
    hide-details
    single-line
  ></v-text-field>

  <TransactionTable
    v-if="transactions"
    :transactions="transactions"
    :persons-list="personsList"
    :search="search"
    @update-assignees="updateAssignees"
    @remove-tag="removeTag"
    @open-add-tag-dialog="openAddTagDialog"
  />

  <!-- Dialog for adding a new tag -->
  <v-dialog v-model="tagDialogVisible" max-width="400px">
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
        <v-btn text @click="tagDialogVisible = false">Cancel</v-btn>
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
