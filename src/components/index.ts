import { defineCustomElement } from 'vue'

import LocationSelector from './geo/LocationSelector.ce.vue'

const tmLocationSelector = defineCustomElement(LocationSelector)

export function register() {
  customElements.define('tm-location-selector', tmLocationSelector)
}

declare global {
  interface HTMLElementTagNameMap {
    'tm-location-selector': typeof tmLocationSelector
  }
}
