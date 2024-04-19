interface CustomIconAttributes { width: number, height: number, anchor: { x: number, y: number } }
export type CustomIcon = { url: string } & CustomIconAttributes

type IconWrapperTemplate = { source: string } & CustomIconAttributes
export interface IconWrapper {
  template?: IconWrapperTemplate
  fill?: string
  embedFill?: string
  embedLabel?: string
  embedLabelStroke?: string
  scale?: number
}

interface StaticImageRenderer { type: 'image', url: string, wrap?: IconWrapper }
interface ColorIconRenderer { type: 'color', color: string, labelColor?: string, wrap?: IconWrapper }
type IconRenderer = { type: 'icon' } & CustomIcon
interface TraditionalIconRenderer { type: 'traditional-icon' }
export type MarkerIconRenderer =
  | StaticImageRenderer
  | IconRenderer
  | ColorIconRenderer
  | TraditionalIconRenderer

export interface MarkerIconConfig {
  renderers: MarkerIconRenderer[]
  wrapDefaults?: IconWrapper
}

export interface GeoCoordinate {
  lat: number
  lng: number
}

export type Id = number | string
export type MapLocation = GeoCoordinate & {
  id: Id
  name?: string
  icon?: MarkerIconConfig
}

export interface MapConfig {
  tileServerApi: {
    url: string
    attribution: string
  }
  zoom: { min: number, max: number, start: number }
  markerIcon: MarkerIconConfig
}
