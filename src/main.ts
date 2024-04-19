import htmx from 'htmx.org'
import { register } from './components'

htmx.on('htmx:responseError', (e) => {
  console.error(e)
})

register()
