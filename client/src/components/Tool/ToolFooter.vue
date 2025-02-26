<template>
    <b-card class="tool-footer" v-if="hasContent">
        <div v-if="hasCitations" class="mb-1">
            <span class="font-weight-bold">Citations:</span>
            <font-awesome-icon
                v-b-tooltip.hover
                title="Copy all citations as BibTeX"
                icon="copy"
                style="cursor: pointer"
                @click="copyBibtex"
            />
            <Citation
                class="formatted-reference"
                v-for="(citation, index) in citations"
                :key="index"
                :citation="citation"
                output-format="bibliography"
                prefix="-"
            />
        </div>
        <div v-if="hasRequirements" class="mb-1">
            <span class="font-weight-bold"
                >Requirements:
                <a href="https://galaxyproject.org/tools/requirements/" target="_blank">
                    <font-awesome-icon v-b-tooltip.hover title="Learn more about Galaxy Requirements" icon="question" />
                </a>
            </span>
            <div v-for="(requirement, index) in requirements" :key="index">
                - {{ requirement.name }}
                <span v-if="requirement.version"> (Version {{ requirement.version }}) </span>
            </div>
        </div>
        <div class="mb-1" v-if="hasLicense">
            <span class="font-weight-bold">License:</span>
            <License :license-id="license" />
        </div>
        <div v-if="hasReferences" class="mb-1">
            <span class="font-weight-bold">References:</span>
            <div v-for="(xref, index) in xrefs" :key="index">
                - {{ xref.reftype }}:
                <template v-if="xref.reftype == 'bio.tools'">
                    {{ xref.value }}
                    (<a :href="`https://bio.tools/${xref.value}`" target="_blank">
                        bio.tools
                        <font-awesome-icon
                            v-b-tooltip.hover
                            title="Visit bio.tools reference"
                            icon="external-link-alt"
                        /> </a
                    >) (<a :href="`https://openebench.bsc.es/tool/${xref.value}`" target="_blank"
                        >OpenEBench
                        <font-awesome-icon
                            v-b-tooltip.hover
                            title="Visit OpenEBench reference"
                            icon="external-link-alt"
                        /> </a
                    >)
                </template>
                <template v-else>
                    {{ xref.value }}
                </template>
            </div>
        </div>
        <div v-if="hasCreators" class="mb-1">
            <span class="font-weight-bold">Creators:</span>
            <Creators :creators="creators" />
        </div>
    </b-card>
</template>

<script>
import { FontAwesomeIcon } from "@fortawesome/vue-fontawesome";
import { library } from "@fortawesome/fontawesome-svg-core";
import { faQuestion, faCopy, faAngleDoubleDown, faAngleDoubleUp } from "@fortawesome/free-solid-svg-icons";

library.add(faQuestion, faCopy, faAngleDoubleDown, faAngleDoubleUp);

import { getCitations } from "components/Citation/services";
import Citation from "components/Citation/Citation";
import License from "components/License/License";
import Creators from "components/SchemaOrg/Creators";
import { copy } from "utils/clipboard";

export default {
    components: {
        Citation,
        License,
        Creators,
        FontAwesomeIcon,
    },
    props: {
        id: {
            type: String,
        },
        hasCitations: {
            type: Boolean,
            default: true,
        },
        xrefs: {
            type: Array,
        },
        license: {
            type: String,
        },
        creators: {
            type: Array,
        },
        requirements: {
            type: Array,
        },
    },
    computed: {
        hasRequirements() {
            return this.requirements && this.requirements.length > 0;
        },
        hasReferences() {
            return this.xrefs && this.xrefs.length > 0;
        },
        hasCreators() {
            return this.creators && this.creators.length > 0;
        },
        hasLicense() {
            return !!this.license;
        },
        hasContent() {
            return (
                this.hasRequirements || this.hasReferences || this.hasCreators || this.hasCitations || this.hasLicense
            );
        },
    },
    data() {
        return {
            citations: [],
        };
    },
    watch: {
        id() {
            this.loadCitations();
        },
    },
    created() {
        this.loadCitations();
    },
    methods: {
        loadCitations() {
            if (this.hasCitations) {
                getCitations("tools", this.id)
                    .then((citations) => {
                        this.citations = citations;
                    })
                    .catch((e) => {
                        console.error(e);
                    });
            }
        },
        copyBibtex() {
            var text = "";
            this.citations.forEach((citation) => {
                const cite = citation.cite;
                const bibtex = cite.format("bibtex", {});
                text += bibtex;
            });
            copy(text, "Citations copied to your clipboard as BibTeX");
        },
    },
};
</script>
