<template>
    <b-input-group size="sm">
        <b-form-input
            v-model="search"
            class="mr-1"
            type="search"
            id="filterInput"
            :placeholder="titleSearch"
            @keyup.enter="startSearch()"
        />
    </b-input-group>
</template>

<script>
import _l from "utils/localization";

export default {
    name: "SearchField",
    props: {
        typingDelay: {
            type: Number,
            default: 1000,
            required: false,
        },
    },
    data() {
        return {
            search: "",
            awaitingSearch: false,
            titleSearch: _l("Search"),
        };
    },
    methods: {
        startSearch() {
            this.$emit("updateSearch", this.search);
            this.awaitingSearch = false;
        },
    },
    watch: {
        search: function () {
            if (!this.awaitingSearch) {
                setTimeout(() => {
                    this.startSearch();
                }, this.typingDelay);
            }
            this.awaitingSearch = true;
        },
    },
};
</script>

<style scoped></style>
