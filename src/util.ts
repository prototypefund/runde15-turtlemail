/**
 * An async generator that behaves similar to Promise.allSettled but
 * yields settled promises as soon as they are available instead of waiting
 * for all of them to settle.
 */
export async function* iterSettled<T>(
  promises: Promise<T>[],
): AsyncGenerator<{ status: 'fulfilled', value: T } | { status: 'rejected', reason: unknown }> {
  if (promises.length === 0)
    return

  // We need to be able to reliably remove settled promises, so we don’t
  // await them over and over again. We can do this, by indexing them in a Map.
  const iterMap = new Map<number, Promise<{ index: number } & ({ data: T } | { error: unknown })>>(
    promises.map((promise, index) => {
      return [
        index,
        new Promise((resolve) => {
          promise
            .then((data) => {
              resolve({ index, data })
            })
            .catch((error) => {
              resolve({ index, error })
            })
        }),
      ]
    }),
  )

  while (iterMap.size > 0) {
    // Find the next settled promise in our map of promises
    // and remove it from the map, so that we don’t await it again.
    const resolved = await Promise.race(iterMap.values())
    iterMap.delete(resolved.index)
    // AsyncGenerator semantics dictate that `yield` behaves as `yield await`.
    // This means that we cannot yield rejected promises, without the generator
    // aborting wherever it encounters the first rejected promise.
    // So we wrap the payload in a Promise.allSettled-like object.
    if ('data' in resolved)
      yield { status: 'fulfilled', value: resolved.data }
    else
      yield { status: 'rejected', reason: resolved.error }
  }
}
