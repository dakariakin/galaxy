<template>
    <div>
        <div class="alert alert-secondary" role="alert">
            <div class="float-left">Convert all datasets to new format</div>
            <div class="text-right">
                <button
                    class="run-tool-collection-edit btn btn-primary"
                    @click="clickedConvert"
                    :disabled="selectedConverter == {}"
                >
                    {{ l("Convert Collection") }}
                </button>
            </div>
        </div>
        <b>{{ l("Converter Tool: ") }}</b>
        <multiselect
            v-model="selectedConverter"
            deselect-label="Can't remove this value"
            track-by="name"
            label="name"
            :options="suitableConverters"
            :searchable="true"
            :allow-empty="true"
        >
        </multiselect>
    </div>
</template>

<script>
import Multiselect from "vue-multiselect";
export default {
    components: { Multiselect },
    data: function () {
        return {
            selectedConverter: {},
        };
    },
    props: {
        suitableConverters: {
            type: Array,
            required: true,
        },
    },
    methods: {
        clickedConvert: function () {
            this.$emit("clicked-convert", this.selectedConverter);
            this.selectedConverter = {};
        },
    },
};
</script>
