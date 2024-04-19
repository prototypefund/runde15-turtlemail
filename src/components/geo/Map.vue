<script lang="ts" setup>
import { computed, onBeforeUnmount, onMounted, ref, shallowRef, watch } from 'vue'
import type { LatLngTuple, Map as MapType, Marker, TileLayer as TileLayerType } from 'leaflet'
import { Browser, Map as LMap, TileLayer } from 'leaflet'

import { useResizeObserver } from '@vueuse/core'
import type { GeoCoordinate, MapConfig, MapLocation } from './types.ts'
import { coordinateToLatLngTuple, defaultConfig, useMarkers } from './map.ts'
import type { Optional } from '@/types.ts'

const props = withDefaults(
  defineProps<{
    config?: MapConfig
    locations?: MapLocation[]
  }>(),
  {
    config: () => defaultConfig,
    locations: () => [],
  },
)
const emit = defineEmits<{
  selectCoordinate: [GeoCoordinate]
  selectMarker: [MapLocation]
}>()
const forcedCenter = defineModel<Optional<GeoCoordinate>>('center', { required: false })
const center = computed(() => {
  return forcedCenter.value ?? props.locations[0] ?? { lat: 51.1657, lng: 10.4515 }
})

const containerEl = ref<HTMLElement>()
const mapEl = ref<HTMLElement>()
const map = shallowRef<MapType>()
const tileLayer = shallowRef<TileLayerType>()
const points = computed(() => props.locations.map(c => coordinateToLatLngTuple(c)))
const markers = useMarkers(() => props.locations, {
  defaultIcon: props.config.markerIcon,
  onSet(location, marker) {
    marker.on('click', () => {
      emit('selectMarker', location)
    })
    marker.on('keyup', ({ originalEvent: event }: { originalEvent: KeyboardEvent }) => {
      if (event.key === 'Enter')
        emit('selectMarker', location)
    })
    if (map.value)
      marker.addTo(map.value)
  },
  onDelete(_, marker) {
    removeMarker(marker)
  },
})

onMounted(() => {
  const config = props.config
  const maxZoom = config.zoom.max
  const isRetina = Browser.retina
  const _map = new LMap(mapEl.value as HTMLElement, {
    center: coordinateToLatLngTuple(center.value),
    zoom: config.zoom.start,
    minZoom: config.zoom.min,
    maxZoom,
  })
  const _tileLayer = new TileLayer(props.config.tileServerApi.url, {
    attribution: config.tileServerApi.attribution,
    minZoom: config.zoom.min,
    // Leaflet may request higher resolution tiles on retina displays,
    // so we need to increase the maxZoom level for the tile layer.
    maxZoom: isRetina ? maxZoom + 1 : maxZoom,
    detectRetina: true,
  })
  _tileLayer.addTo(_map)

  // Markers may already be computed and onSet couldn’t add them.
  // Do that now.
  for (const marker of markers.value.values())
    marker.addTo(_map)

  _map.on('moveend', () => {
    forcedCenter.value = _map.getCenter()
  })
  _map.on('click', (e) => {
    emit('selectCoordinate', e.latlng)
  })
  map.value = _map
  tileLayer.value = _tileLayer
})

onBeforeUnmount(() => {
  for (const marker of markers.value.values())
    removeMarker(marker)
  tileLayer.value?.clearAllEventListeners()
  tileLayer.value?.remove()
  tileLayer.value = undefined
  map.value?.clearAllEventListeners()
  map.value?.remove()
  map.value = undefined
})

function removeMarker(marker: Marker) {
  marker.clearAllEventListeners()
  marker.remove()
  if (map.value)
    map.value.removeLayer(marker)
}

function setBounds(points: LatLngTuple[]) {
  if (!map.value)
    return

  // We want this to:
  //   * re-focus the map if there are points to focus on
  //   * reset the map to its original center if no points are being displayed
  if (points.length > 0) {
    map.value.fitBounds([...points], {
      maxZoom: map.value.getZoom(),
    })
  }
  else {
    map.value.setView(
      coordinateToLatLngTuple(center.value),
      props.config.zoom.start,
    )
  }
}

useResizeObserver(containerEl, () => {
  requestAnimationFrame(() => {
    const _containerEl = containerEl.value
    const _mapEl = mapEl.value
    const _map = map.value
    if (_containerEl && _mapEl && _map) {
      const { height } = _containerEl.getBoundingClientRect()
      _mapEl.style.height = `${height}px`
      _map.invalidateSize()
      setBounds(points.value)
    }
  })
})

watch([map, points], async ([map, points], [oldMap, _]) => {
  // If we don’t have a map object yet or the map was just initialized
  // we don’t need to do anything.
  if (!map || (map && !oldMap))
    return
  setBounds(points)
})
</script>

<template>
  <div ref="containerEl" class="tm-map">
    <div ref="mapEl" />
  </div>
</template>
