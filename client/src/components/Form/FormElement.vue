<template>
    <div v-show="!hidden" :id="elementId" :class="['ui-form-element section-row', cls]" :tour_id="id">
        <div v-if="hasError" class="ui-form-error">
            <span class="fa fa-exclamation mr-1" />
            <span class="ui-form-error-text" v-html="error" />
        </div>
        <div class="ui-form-title">
            <div v-if="collapsible || connectable">
                <span v-if="collapsible && !connected" class="ui-form-collapsible-icon icon" @click="onCollapse">
                    <span v-if="collapsed" :class="collapsedEnableIcon" :title="collapsedEnableText" />
                    <span v-else :class="collapsedDisableIcon" :title="collapsedDisableText" />
                </span>
                <span v-if="connectable" class="ui-form-connected-icon icon" @click="onConnect">
                    <span v-if="connected" :class="connectedEnableIcon" :title="connectedEnableText" />
                    <span v-else :class="connectedDisableIcon" :title="connectedDisableText" />
                </span>
                <span class="ui-form-title-text ml-1">
                    {{ title }}
                </span>
            </div>
            <span v-else class="ui-form-title-text">{{ title }}</span>
        </div>
        <div v-if="showField" class="ui-form-field" :data-label="title">
            <FormParameter
                v-if="backbonejs"
                v-model="currentValue"
                :id="id"
                :data-label="title"
                :type="type"
                :attributes="attrs"
                ref="params"
            />
            <FormBoolean v-else-if="type == 'boolean'" v-model="currentValue" :id="id" />
            <FormInput v-else v-model="currentValue" :id="id" :area="attrs['area']" />
        </div>
        <div v-if="showPreview" class="ui-form-preview" v-html="previewText" />
        <span v-if="!!helpText" class="ui-form-info form-text text-muted" v-html="helpText" />
    </div>
</template>

<script>
import _ from "underscore";
import { getElementId } from "./utilities";
import FormBoolean from "./Elements/FormBoolean";
import FormInput from "./Elements/FormInput";
import FormParameter from "./Elements/FormParameter";

export default {
    components: {
        FormBoolean,
        FormInput,
        FormParameter,
    },
    props: {
        id: {
            type: String,
            default: "identifer",
        },
        type: {
            type: String,
            default: "text",
        },
        value: {
            default: null,
        },
        title: {
            type: String,
            default: null,
        },
        refreshOnChange: {
            type: Boolean,
            default: false,
        },
        help: {
            type: String,
            default: null,
        },
        error: {
            type: String,
            default: null,
        },
        backbonejs: {
            type: Boolean,
            default: false,
        },
        disabled: {
            type: Boolean,
            default: false,
        },
        attributes: {
            type: Object,
            default: null,
        },
        collapsedEnableText: {
            type: String,
            default: "Enable",
        },
        collapsedDisableText: {
            type: String,
            default: "Disable",
        },
        collapsedEnableIcon: {
            type: String,
            default: "fa fa-caret-square-o-down",
        },
        collapsedDisableIcon: {
            type: String,
            default: "fa fa-caret-square-o-up",
        },
        connectedEnableText: {
            type: String,
            default: "Remove connection from module.",
        },
        connectedDisableText: {
            type: String,
            default: "Add connection to module.",
        },
        connectedEnableIcon: {
            type: String,
            default: "fa fa fa-times",
        },
        connectedDisableIcon: {
            type: String,
            default: "fa fa-arrows-h",
        },
    },
    data() {
        return {
            collapsed: false,
            connected: false,
            connectedValue: { __class__: "ConnectedValue" },
        };
    },
    computed: {
        argument() {
            return this.attrs["argument"];
        },
        attrs() {
            return this.attributes || this.$attrs;
        },
        cls() {
            return this.hasError && "alert alert-info";
        },
        collapsible() {
            return !this.disabled && this.collapsibleValue !== undefined;
        },
        collapsibleValue() {
            return this.attrs["collapsible_value"];
        },
        collapsiblePreview() {
            return this.attrs["collapsible_preview"];
        },
        connectable() {
            return this.collapsible && this.attrs["connectable"];
        },
        currentValue: {
            get() {
                return this.value;
            },
            set(val) {
                this.setValue(val);
            },
        },
        defaultValue() {
            return this.attrs["default_value"];
        },
        elementId() {
            return getElementId(this.id);
        },
        hasError() {
            return !!this.error;
        },
        helpText() {
            const help = this.help;
            const helpArgument = this.argument;
            if (helpArgument && help.indexOf(`(${helpArgument})`) == -1) {
                return `${help} (${helpArgument})`;
            }
            return help;
        },
        hidden() {
            return this.attrs["hidden"];
        },
        previewText() {
            return _.escape(this.textValue).replace(/\n/g, "<br>");
        },
        showField() {
            return !this.collapsed && !this.disabled;
        },
        showPreview() {
            return (this.collapsed && this.collapsiblePreview) || this.disabled;
        },
        textValue() {
            return this.attrs["text_value"];
        },
    },
    created() {
        this.initialState();
    },
    methods: {
        /** Submits a changed value. */
        setValue(value) {
            this.$emit("input", value, this.id);
            this.$emit("change", this.refreshOnChange);
        },
        /**
         * Determines to wether expand or collapse the input.
         */
        initialState() {
            const collapsibleValue = this.collapsibleValue;
            const value = JSON.stringify(this.value);
            this.connected = value == JSON.stringify(this.connectedValue);
            this.collapsed =
                this.connected || (collapsibleValue !== undefined && value == JSON.stringify(collapsibleValue));
        },
        /**
         * Handles collapsible toggle.
         */
        onCollapse() {
            this.collapsed = !this.collapsed;
            this.connected = false;
            if (this.collapsed) {
                this.setValue(this.collapsibleValue);
            } else {
                this.setValue(this.defaultValue);
            }
        },
        /**
         * Handles connected state.
         */
        onConnect() {
            this.connected = !this.connected;
            this.collapsed = this.connected;
            if (this.connected) {
                this.setValue(this.connectedValue);
            } else {
                this.setValue(this.defaultValue);
            }
        },
    },
};
</script>
