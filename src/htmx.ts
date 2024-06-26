import htmx from 'htmx.org'

export function showHtmxErrors() {
  document.addEventListener('DOMContentLoaded', () => {
    const errorList = document.querySelector('#global_messages')
    const errorTemplate: HTMLTemplateElement
      = document.querySelector('#error_alert')!

    // Sorry for the `any` type, but I couldn't find any good htmx
    // type definitions
    htmx.on('htmx:responseError', (error: any) => {
      const errorEl = errorTemplate.content.cloneNode(true)

      const technicalDetailsEl = (errorEl as HTMLElement).querySelector(
        '.error-alert-technical-details',
      )
      if (technicalDetailsEl !== null)
        technicalDetailsEl.textContent = `${error.detail.requestConfig.verb} ${error.detail.xhr.status} ${error.detail.xhr.responseURL}`

      errorList?.append(errorEl)
    })
  })
}
