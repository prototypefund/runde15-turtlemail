import type { MaybeRefOrGetter } from '@vueuse/core'
import { toRef } from '@vueuse/core'
import type { Icon as IconType, LatLngTuple, Marker as MarkerType } from 'leaflet'
import { Icon, Marker } from 'leaflet'
import { shallowRef, watch } from 'vue'

import type { GeoCoordinate, Id, MapConfig, MapLocation, MarkerIconConfig } from './types.ts'
import type { MarkerIcon } from './icon.ts'
import { resolveMarkerIcon } from './icon.ts'
import { iterSettled } from '@/util.ts'

interface UsePointsOfInterestOptions {
  defaultIcon: MarkerIconConfig
  onDelete?: (locationId: MapLocation['id'], marker: MarkerType) => unknown
  onSet?: (location: MapLocation, marker: MarkerType) => unknown
  resolveImage?: ((url: string) => Promise<string | undefined>) | undefined
}

export function useMarkers(
  locations: MaybeRefOrGetter<MapLocation[]>,
  options: UsePointsOfInterestOptions,
) {
  let lastUpdate = new Date()
  const _locations = toRef(locations)
  const markers = shallowRef(new Map<Id, MarkerType>())

  function createIcon(markerIcon: MarkerIcon): IconType {
    return new Icon({
      ...markerIcon,
      iconRetinaUrl: markerIcon.iconUrl,
      className: `cb-map-marker ${markerIcon.className}`,
    })
  }

  async function createMarker(location: MapLocation) {
    const icon = await resolveMarkerIcon(location.icon ?? options.defaultIcon)
    const marker = new Marker(
      { lat: location.lat, lng: location.lng },
      {
        title: location.name,
        icon: createIcon(icon),
      },
    )
    return { marker, location }
  }

  async function updateMarkers() {
    const updateInitiatedAt = new Date()
    lastUpdate = updateInitiatedAt

    // first handle locations no longer in our list
    const newLocationIds = new Set(_locations.value.map(({ id }) => id))
    for (const [locationId, marker] of markers.value.entries()) {
      if (!newLocationIds.has(locationId)) {
        markers.value.delete(locationId)
        options?.onDelete?.(locationId, marker)
      }
    }

    // now handle all new commons in the list
    const newLocations = _locations.value.filter(c => !markers.value.has(c.id))
    const newMarkers = newLocations.map(createMarker)
    for await (const settled of iterSettled(newMarkers)) {
      if (settled.status === 'rejected') {
        console.error('Could not create marker from location', settled.reason)
        continue
      }

      // Using an async function in watchEffect entails that we have to
      // manually check if we should still modify state. If another effect
      // was scheduled lastUpdate will have changed, so we know that we
      // should stop processing here and now.
      if (lastUpdate.getTime() !== updateInitiatedAt.getTime())
        break

      const { location, marker } = settled.value
      markers.value.set(location.id, marker)
      options?.onSet?.(location, marker)
    }
  }

  watch([_locations], updateMarkers, { immediate: true })

  return markers
}

export function coordinateToLatLngTuple(c: GeoCoordinate): LatLngTuple {
  return [c.lat, c.lng]
}

export const defaultConfig: MapConfig = {
  tileServerApi: {
    url: 'https://{s}.tile.openstreetmap.de/{z}/{x}/{y}.png',
    attribution: 'Map data © <a href="https://openstreetmap.org">OpenStreetMap</a> contributors - <a href="https://www.openstreetmap.org/copyright">License</a>',
  },
  zoom: {
    max: 19,
    min: 6,
    start: 8,
  },
  markerIcon: {
    renderers: [
      { type: 'color', color: 'var(--tm-accent-color)' },
    ],
  },
}
