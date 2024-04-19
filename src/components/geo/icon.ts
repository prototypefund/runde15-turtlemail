import type {
  CustomIcon,
  IconWrapper,
  MarkerIconConfig,
} from './types'
import marker from './map-marker.svg'
import MapMarkerTemplate from './map-marker-template.svg?raw'

import { createImageResolver } from './icon-helpers.ts'

export interface MarkerIcon {
  iconUrl: string
  iconSize: [number, number]
  iconAnchor: [number, number]
  className: string
}

const defaultImageResolver = createImageResolver()

const traditionalIcon: MarkerIcon = {
  iconUrl: marker,
  iconSize: [25, 41],
  iconAnchor: [12.5, 41],
  className: 'tm-map-marker--type-icon tm-map-marker--type-traditional-icon',
}

function defaults<T>(...args: (T | undefined)[]) {
  return Object.assign({}, ...args.map(arg => arg ?? {}))
}

function getNodeSelector(node: Element) {
  const classes = String(node.classList)
  const attrs = Array.from(node.attributes)
    .filter(a => a.name !== 'class')
    .map(a => `[${a.name}="${a.value}"]`)
    .join('')
  return `${node.nodeName.toLowerCase()}${attrs}${classes ? `.${classes}` : ''}`
}

function resolveColor(
  color: string | undefined,
  defaultValue: string | undefined = undefined,
  root?: Element,
) {
  const _color = color ?? defaultValue
  if (!_color)
    return _color
  const match = /^var\(\s*(--[^,)]+)(?:,\s*(.+))?\s*\)$/.exec(_color)
  if (match) {
    const _root = root ?? document.querySelector('.tm-map') ?? document.documentElement
    const cssProperty = match[1] as string
    const cssPropertyDefault = match[2] as string
    const resolvedColor = getComputedStyle(_root).getPropertyValue(cssProperty).trim()

    if (resolvedColor) {
      return resolvedColor
    }
    else {
      if (!cssPropertyDefault) {
        console.warn(
          `Could not find CSS property '${cssProperty}' on node ${getNodeSelector(_root)}.`,
        )
        return defaultValue
      }
      return cssPropertyDefault
    }
  }
  else {
    return _color
  }
}

export function makeMapMarkerIcon(
  imageUrl: string | undefined,
  rendererTypes: string[],
  config?: IconWrapper | undefined,
): MarkerIcon {
  const template = config?.template ?? {
    source: MapMarkerTemplate,
    width: 60,
    height: 70,
    anchor: { x: 0.5, y: 1 },
  }
  const scale = config?.scale ?? 1
  const fill = resolveColor(config?.fill) ?? '#fff'
  const embedFill = resolveColor(config?.embedFill) ?? fill
  const labelColor = resolveColor(config?.embedLabelStroke) ?? '#fff'
  const width = template.width * scale
  const height = template.height * scale
  const x = width * template.anchor.x
  const y = height * template.anchor.y
  const svg = template.source
    .replaceAll(/\s*\n\s*/g, ' ')
    .replaceAll('__WIDTH__', width.toString())
    .replaceAll('__HEIGHT__', height.toString())
    .replaceAll('__FILL_COLOR__', fill)
    .replaceAll('__EMBED_FILL_COLOR__', embedFill)
    .replaceAll('__EMBED_URL__', imageUrl ?? '')
    .replaceAll('__EMBED_LABEL_COLOR__', labelColor)
    .replaceAll('__EMBED_LABEL__', config?.embedLabel ?? '')
  return {
    iconUrl: `data:image/svg+xml;utf8,${encodeURIComponent(svg)}`,
    iconSize: [width, height],
    iconAnchor: [x, y],
    className: rendererTypes.map(type => `tm-map-marker--type-${type}`).join(' '),
  }
}

function customIconToMapMarkerIcon(icon: CustomIcon): MarkerIcon {
  const { width, height } = icon
  return {
    iconUrl: icon.url,
    iconSize: [width, height],
    iconAnchor: [width * icon.anchor.x, height * icon.anchor.y],
    className: 'tm-map-marker--type-icon',
  }
}

async function _resolveMarkerIcon(
  config: MarkerIconConfig | undefined,
  defaultValue?: MarkerIcon,
  baseRendererTypes: string[] = [],
  resolveURL: (url: string) => Promise<string | undefined> = defaultImageResolver,
): Promise<MarkerIcon> {
  const renderers = config?.renderers ?? []

  for (const renderer of renderers) {
    if (renderer.type === 'image') {
      const url = await resolveURL(renderer.url)
      if (!url)
        continue
      const wrapConf = defaults(config?.wrapDefaults, renderer?.wrap)
      return makeMapMarkerIcon(url, [...baseRendererTypes, 'image'], wrapConf)
    }

    if (renderer.type === 'color') {
      const color = resolveColor(renderer.color)
      if (!color)
        continue
      const wrapConf = defaults(config?.wrapDefaults, renderer?.wrap, {
        embedFill: color,
      })
      return makeMapMarkerIcon(undefined, [...baseRendererTypes, 'color'], wrapConf)
    }

    if (renderer.type === 'icon')
      return customIconToMapMarkerIcon(renderer)

    if (renderer.type === 'traditional-icon')
      return traditionalIcon
  }

  return (
    defaultValue
    ?? makeMapMarkerIcon(undefined, ['color'], {
      embedFill: 'var(--tm-map-marker-default-embed-fill)',
    })
  )
}

export async function resolveMarkerIcon(
  config: MarkerIconConfig | undefined,
  defaultValue?: MarkerIcon,
  resolveURL: (url: string) => Promise<string | undefined> = defaultImageResolver,
) {
  return _resolveMarkerIcon(config, defaultValue, [], resolveURL)
}
