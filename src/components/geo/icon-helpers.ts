export function createImageResolver(cache?: Map<string, Promise<string | undefined>>) {
  const _cache = cache ?? new Map<string, Promise<string>>()

  return async function resolveURL(url: string): Promise<string | undefined> {
    // We don’t need to resolve data urls. They can be used as-is.
    if (url.startsWith('data:image/'))
      return url

    // First try the cache.
    if (_cache.has(url)) {
      const dataURL = await _cache.get(url)
      if (dataURL)
        return dataURL
    }

    // No cache hit. Fetch the image.
    // eslint-disable-next-line no-async-promise-executor
    const promise = new Promise<string | undefined>(async (resolve) => {
      let res: Response
      let blob: Blob
      try {
        res = await fetch(url, { cache: 'force-cache' })
      }
      catch (e) {
        console.error('Could not initialize server connection while loading image', { url })
        return resolve(undefined)
      }

      if (!res.ok) {
        console.error('Could not load image. Server responded with error code.', { url, res })
        return resolve(undefined)
      }

      try {
        blob = await res.blob()
      }
      catch (e) {
        console.error('Could not transform server response to blob.', { url, res })
        return resolve(undefined)
      }
      const reader = new FileReader()
      reader.onerror = () => {
        console.error('Cannot read data URL from image blob', url)
        resolve(undefined)
      }
      reader.onload = () => {
        resolve(reader.result as string)
      }
      reader.readAsDataURL(blob)
    })
    _cache.set(url, promise)
    return await promise
  }
}
