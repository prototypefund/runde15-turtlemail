<script lang="ts" setup>
import { computed, ref, watch } from 'vue'
import type { GeoCoordinate, MapLocation } from './types'
import Map from './Map.vue'

const props = defineProps<{
  label?: string
  lat?: number
  lng?: number
  editable?: boolean
}>()
const emit = defineEmits<{
  change: [GeoCoordinate]
}>()
const location = ref<GeoCoordinate | null>(props.lat && props.lng ? { lat: props.lat, lng: props.lng } : null)
const locations = computed<MapLocation[]>(() => {
  const _location = location.value
  if (!_location)
    return []
  const { lat, lng } = _location
  return [{
    id: `selected-location-${lat}-${lng}`,
    name: props.label,
    lat,
    lng,
  }]
})

watch([() => props.lat, () => props.lng], ([lat, lng]) => {
  if (lat && lng)
    location.value = { lat, lng }
})

function updateLocation(newLocation: GeoCoordinate) {
  if (!props.editable)
    return

  location.value = newLocation
  emit('change', { ...newLocation })
}
</script>

<template>
  <Map :locations="locations" @select-coordinate="updateLocation" />
</template>

<style lang="postcss">
/*
 * Unfortunately, we cannot import this in Map.vue,
 * because then we would have to register Map.vue itself as a custom element.
*/
@import "leaflet/dist/leaflet.css";

.leaflet-grab {
  cursor: default;

  .leaflet-drag-target & { cursor: grab; }
}

/* Prevent the map from rendering on top of the navbar which has a z-index of 10 */
.leaflet-container {
  z-index: 0;
}
</style>
