<template>
    <v-app>
        <v-toolbar color="grey-darken-3" dark fixed app>
            <v-toolbar-title>Application</v-toolbar-title>
        </v-toolbar>
        <v-container fluid fill-height>
            <RouterView/>
        </v-container>
        <v-footer color="grey-darken-3" app>
            <span class="white--text">&copy; 2017</span>
        </v-footer>
    </v-app>
</template> 