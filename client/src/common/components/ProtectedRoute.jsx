import { useState, useEffect } from 'react'
import { useLocation } from 'react-router-dom'

function ProtectedRoute({ children }) {
  // This component is now just a wrapper since authentication is checked at the route level
  // We keep it for consistency and potential future use
  
  return children
}

export default ProtectedRoute
