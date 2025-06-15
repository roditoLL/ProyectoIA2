import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'

import SimilaridadGraph from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <SimilaridadGraph />
  </StrictMode>,
)
