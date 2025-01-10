<script>
import { doApiCall } from "@/helpers/doApiCall";
import ButtonWithState from "../components/ButtonWithState.vue";

export default {
  components: {
    ButtonWithState,
  },
  data() {
    return {
      // Button states
      btnLoadingStates: {
        runRules: false,
      },
      btnIconStates: {
        runRules: null,
      },

      // Rules data
      rules: null,
      rulesLoading: false,

      // Dialog states
      formDialogVisible: false,
      formDialogIsEditing: false,
      formDialogFormValid: false,
      formDialogData: {
        id: null,
        rule: "",
        action: "",
        action_value_1: "",
        action_value_2: "",
      },
      formDialogRequiredRule: [
        (value) => {
          if (value) return true;

          return "Field is required";
        },
      ],
      deletePromptVisible: false,
      itemToBeDeleted: null,

      // Table headers
      tableHeaders: [
        { title: "Rule", value: "rule" },
        { title: "Action", value: "action" },
        { title: "Action Value 1", value: "action_value_1" },
        { title: "Action Value 2", value: "action_value_2" },
        {
          title: "Actions",
          value: "actions",
          align: "end",
          sortable: false,
        },
      ],
    };
  },

  async created() {
    await this.getRules();
  },

  methods: {
    /**
     * Wraps doApiCall in state management for buttons (loading & icon states).
     */
    async doAction(actionKey, url) {
      this.btnLoadingStates[actionKey] = true;
      this.btnIconStates[actionKey] = null;

      try {
        await doApiCall(url, "GET", false, null);
        this.btnIconStates[actionKey] = "success";
      } catch (err) {
        console.error(err);
        this.btnIconStates[actionKey] = "error";
      } finally {
        this.btnLoadingStates[actionKey] = false;
      }
    },

    /**
     * Fetch existing rules.
     */
    async getRules() {
      this.rulesLoading = true;
      try {
        this.rules = await doApiCall(
          `/api/rule/`,
          "GET",
          true,
          null,
          "fetching rules"
        );
      } catch (err) {
        console.error(err);
      } finally {
        this.rulesLoading = false;
      }
    },

    /**
     * Opens the dialog for adding a new rule.
     */
    openFormDialog(data) {
      if (data) {
        this.formDialogIsEditing = true;
        this.formDialogData = { ...data };
      } else {
        this.formDialogIsEditing = false;
        this.clearForm();
      }
      this.formDialogVisible = true;
    },

    /**
     * Closes the dialog and clears the form.
     */
    closeFormDialog() {
      this.formDialogVisible = false;
      this.clearForm();
    },

    /**
     * Resets the form fields.
     */
    clearForm() {
      this.formDialogData = {
        id: null,
        rule: "",
        action: "",
        action_value_1: "",
        action_value_2: "",
      };
      this.formDialogFormValid = false;
    },

    /**
     * Validate and save the rule (create or update).
     */
    async handleSave() {
      // Trigger form validation
      await this.$refs.ruleForm.validate();
      if (!this.formDialogFormValid) return;

      try {
        if (this.formDialogIsEditing) {
          await this.updateRule();
        } else {
          await this.createRule();
        }
        // Close the dialog on success
        this.closeFormDialog();
      } catch (err) {
        console.error(err);
      }
    },

    /**
     * Creates a new rule.
     */
    async createRule() {
      this.rulesLoading = true;
      try {
        const postData = {
          rule: this.formDialogData.rule,
          action: this.formDialogData.action,
          action_value_1: this.formDialogData.action_value_1,
          action_value_2: this.formDialogData.action_value_2,
        };
        await doApiCall(`/api/rule/`, "POST", false, postData, "creating rule");
        await this.getRules();
      } finally {
        this.rulesLoading = false;
      }
    },

    /**
     * Updates an existing rule.
     */
    async updateRule() {
      if (!this.formDialogData.id) {
        throw new Error("Cannot update rule without an ID");
      }

      this.rulesLoading = true;
      try {
        const postData = {
          rule: this.formDialogData.rule,
          action: this.formDialogData.action,
          action_value_1: this.formDialogData.action_value_1,
          action_value_2: this.formDialogData.action_value_2,
        };
        await doApiCall(
          `/api/rule/${this.formDialogData.id}`,
          "PUT",
          false,
          postData,
          "updating rule"
        );
        await this.getRules();
      } finally {
        this.rulesLoading = false;
      }
    },

    /**
     * Prompt for rule deletion.
     */
    promptDelete(ruleItem) {
      this.itemToBeDeleted = ruleItem;
      this.deletePromptVisible = true;
    },

    /**
     * Confirm delete action and remove from the rules list.
     */
    async confirmDelete() {
      if (!this.itemToBeDeleted) return;

      this.rulesLoading = true;
      try {
        await doApiCall(
          `/api/rule/${this.itemToBeDeleted.id}`,
          "DELETE",
          false,
          null,
          "deleting rule"
        );
        this.rules = this.rules.filter(
          (rule) => rule.id !== this.itemToBeDeleted.id
        );
      } catch (err) {
        console.error(err);
      } finally {
        this.rulesLoading = false;
        this.deletePromptVisible = false;
        this.itemToBeDeleted = null;
      }
    },

    /**
     * Handler for 'Run Rules' button.
     */
    async handleRunRules() {
      await this.doAction("runRules", "/api/rule/run");
    },
  },
};
</script>

<template>
  <!-- Loading Indicator -->
  <div v-if="rulesLoading" class="d-flex justify-center mt-2">
    <v-progress-circular indeterminate />
  </div>

  <!-- Top Actions -->
  <div class="d-flex align-center justify-end flex-wrap mb-4">
    <v-btn class="mr-2" @click="openFormDialog()">Add Rule</v-btn>
    <ButtonWithState
      text="Run Rules"
      :loadingState="btnLoadingStates.runRules"
      :iconState="btnIconStates.runRules"
      @click="handleRunRules"
    />
  </div>

  <!-- Create/Edit Rule Dialog -->
  <v-dialog v-model="formDialogVisible" max-width="600px">
    <v-card>
      <v-card-title>
        {{ formDialogIsEditing ? "Edit Rule " : "Add a New Rule" }}
      </v-card-title>

      <v-card-text>
        <v-form ref="ruleForm" v-model="formDialogFormValid" lazy-validation>
          <v-text-field
            v-model="formDialogData.rule"
            label="Rule"
            :rules="formDialogRequiredRule"
            hint="Required field"
            persistent-hint
            required
            class="mb-2"
          />
          <v-text-field
            v-model="formDialogData.action"
            label="Action"
            :rules="formDialogRequiredRule"
            hint="Required field"
            persistent-hint
            required
            class="mb-2"
          />
          <v-text-field
            v-model="formDialogData.action_value_1"
            label="Action Value 1"
          />
          <v-text-field
            v-model="formDialogData.action_value_2"
            label="Action Value 2"
          />
        </v-form>
      </v-card-text>

      <v-card-actions>
        <v-btn text @click="closeFormDialog">Cancel</v-btn>
        <v-btn
          text
          color="primary"
          :disabled="!formDialogFormValid || rulesLoading"
          @click="handleSave"
        >
          Save
        </v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Delete Confirmation Dialog -->

  <v-dialog v-model="deletePromptVisible" max-width="500px">
    <v-card>
      <v-card-title class="headline">Confirm Delete</v-card-title>
      <v-card-text>
        Are you sure you want to delete the rule:
        <strong>{{ itemToBeDeleted && itemToBeDeleted.rule }}</strong
        >?
      </v-card-text>
      <v-card-actions>
        <v-btn text @click="deletePromptVisible = false">Cancel</v-btn>
        <v-btn text color="error" @click="confirmDelete">Delete</v-btn>
      </v-card-actions>
    </v-card>
  </v-dialog>

  <!-- Rules Table -->
  <v-data-table
    v-if="rules && rules.length"
    class="mt-4"
    :items="rules"
    :headers="tableHeaders"
  >
    <template v-slot:item.actions="{ item }">
      <v-icon small class="mr-2" @click="openFormDialog(item)"
        >mdi-pencil</v-icon
      >
      <v-icon small @click="promptDelete(item)">mdi-delete</v-icon>
    </template>
  </v-data-table>
</template>
