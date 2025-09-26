import { useState, useEffect } from 'react'

/**
 * Custom hook to calculate the center coordinates of the current viewport
 * Takes into account scroll position to ensure modals appear in the visible area
 */
export function useViewportCenter() {
  const [viewportCenter, setViewportCenter] = useState({
    x: 0,
    y: 0,
    width: 0,
    height: 0
  })

  useEffect(() => {
    const calculateViewportCenter = () => {
      const scrollTop = window.pageYOffset || document.documentElement.scrollTop
      const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft
      const viewportWidth = window.innerWidth
      const viewportHeight = window.innerHeight
      
      setViewportCenter({
        x: scrollLeft + (viewportWidth / 2),
        y: scrollTop + (viewportHeight / 2),
        width: viewportWidth,
        height: viewportHeight
      })
    }

    // Calculate initial position
    calculateViewportCenter()

    // Update position on scroll and resize
    const handleScroll = () => calculateViewportCenter()
    const handleResize = () => calculateViewportCenter()

    window.addEventListener('scroll', handleScroll, { passive: true })
    window.addEventListener('resize', handleResize, { passive: true })

    return () => {
      window.removeEventListener('scroll', handleScroll)
      window.removeEventListener('resize', handleResize)
    }
  }, [])

  return viewportCenter
}

/**
 * Helper function to get modal positioning styles based on viewport center
 * Ensures modal stays fully within viewport bounds
 */
export function getModalPositionStyles(viewportCenter, modalWidth = 400, modalHeight = 300) {
  const padding = 20 // Minimum padding from viewport edges
  
  // Calculate ideal centered position
  let left = viewportCenter.x - (modalWidth / 2)
  let top = viewportCenter.y - (modalHeight / 2)
  
  // Get current scroll position
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop
  const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft
  
  // Calculate viewport boundaries
  const viewportLeft = scrollLeft + padding
  const viewportRight = scrollLeft + viewportCenter.width - modalWidth - padding
  const viewportTop = scrollTop + padding
  const viewportBottom = scrollTop + viewportCenter.height - modalHeight - padding
  
  // Constrain position to viewport bounds
  left = Math.max(viewportLeft, Math.min(left, viewportRight))
  top = Math.max(viewportTop, Math.min(top, viewportBottom))
  
  return {
    position: 'fixed',
    left: `${left}px`,
    top: `${top}px`,
    width: `${modalWidth}px`,
    maxHeight: `${Math.min(modalHeight, viewportCenter.height - (2 * padding))}px`,
    zIndex: 1000,
    transform: 'none' // Override any existing transforms
  }
}