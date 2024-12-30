<script>
export default {
    data() {
        return {
            accounts: null,
            accountTransactions: null,
            selectedAccount: null,
            transactionHeaders: [
                {
                    title: 'Booking Date',
                    value: 'bookingDate'        // field in your data
                },
                {
                    title: 'Description',
                    value: 'remittanceInformationUnstructured' // field in your data
                },
                {
                    title: 'Amount',
                    value: 'transactionAmount.amount'      // field in your data
                },
            ],
        };
    },
    methods: {
        formatCurrency(value) {
            return value.toLocaleString(`en-gb`, {
                style: 'currency',
                currency: `USD`,
            });
        },
        getAccounts() {
            fetch(`/api/accounts`, { method: "GET" })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`Expected HTTP 200, got HTTP ${response.status}`, { cause: response });
                    } else {
                        return response;
                    }
                })
                .then((response) => response.json())
                .then((json) => {
                    this.accounts = json
                })
                .catch((e) => {
                    console.log(e);
                });
        },
        getAccountTransactions() {
            fetch(`/api/transactions/` + this.selectedAccount, { method: "GET" })
                .then((response) => {
                    if (!response.ok) {
                        throw new Error(`Expected HTTP 200, got HTTP ${response.status}`, { cause: response });
                    } else {
                        return response;
                    }
                })
                .then((response) => response.json())
                .then((json) => {
                    this.accountTransactions = json
                })
                .catch((e) => {
                    console.log(e);
                });
        }
    },
    created() {
        this.getAccounts();
        this.selectedAccount = this.$route.params.accountid;
        if (this.selectedAccount) {
            this.getAccountTransactions();
        }
    },
    watch: {
        $route(to, from) {
            this.selectedAccount = this.$route.params.accountid;
            this.getAccountTransactions();
        }
    },
}
</script>

<template>
    <table>
        <thead>
            <tr>
                <th>Description</th>
                <th>Balance</th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="account in accounts">
                <td><router-link :to="'/' + account._id">{{ account.description }}</router-link></td>
                <td>{{ new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP' }).format(account.balance) }}</td>
            </tr>
        </tbody>
    </table>
    <v-data-table :headers="transactionHeaders" :items="accountTransactions" v-if="accountTransactions && accountTransactions.length">
        <template v-slot:item.transactionAmount.amount="{ item }">
            <span>{{ new Intl.NumberFormat('en-GB', { style: 'currency', currency: 'GBP' }).format(item.transactionAmount.amount) }}</span>
        </template>
    </v-data-table>
</template>

