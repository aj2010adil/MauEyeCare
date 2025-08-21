import React, { useState, useRef, useEffect } from 'react'
import { Camera, RotateCcw, Download, Share2, X, ChevronLeft, ChevronRight, ZoomIn, ZoomOut } from 'lucide-react'
import toast from 'react-hot-toast'

interface Spectacle {
  id: number
  name: string
  brand: string
  price: number
  image_url?: string
  frame_material: string
  frame_shape: string
  lens_type: string
  gender: string
  age_group: string
  description?: string
  specifications?: Record<string, any>
  in_stock: boolean
  quantity: number
}

interface TryOn3DViewerProps {
  spectacle: Spectacle
  patientImage?: string
  onClose: () => void
  onCapture: (imageData: string) => void
  onAddToCart: (spectacle: Spectacle) => void
}

export default function TryOn3DViewer({ 
  spectacle, 
  patientImage, 
  onClose, 
  onCapture, 
  onAddToCart 
}: TryOn3DViewerProps) {
  const [isLoading, setIsLoading] = useState(true)
  const [currentView, setCurrentView] = useState<'front' | 'side' | 'angle'>('front')
  const [zoom, setZoom] = useState(1)
  const [rotation, setRotation] = useState(0)
  const [isCapturing, setIsCapturing] = useState(false)
  const [capturedImage, setCapturedImage] = useState<string | null>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const streamRef = useRef<MediaStream | null>(null)

  useEffect(() => {
    initializeCamera()
    return () => {
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop())
      }
    }
  }, [])

  const initializeCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { 
          width: { ideal: 1280 }, 
          height: { ideal: 720 },
          facingMode: 'user'
        } 
      })
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        streamRef.current = stream
        
        videoRef.current.onloadedmetadata = () => {
          setIsLoading(false)
        }
      }
    } catch (error) {
      console.error('Error accessing camera:', error)
      toast.error('Unable to access camera. Please check permissions.')
      setIsLoading(false)
    }
  }

  const captureImage = () => {
    if (!canvasRef.current || !videoRef.current) return

    const canvas = canvasRef.current
    const video = videoRef.current
    const ctx = canvas.getContext('2d')

    if (!ctx) return

    setIsCapturing(true)

    // Set canvas size to match video
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight

    // Draw video frame
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)

    // Add spectacle overlay
    addSpectacleOverlay(ctx, canvas.width, canvas.height)

    // Add branding and info
    addBrandingOverlay(ctx, canvas.width, canvas.height)

    // Convert to data URL
    const imageData = canvas.toDataURL('image/png')
    setCapturedImage(imageData)
    onCapture(imageData)
    
    setIsCapturing(false)
    toast.success('Image captured successfully!')
  }

  const addSpectacleOverlay = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    // Calculate face position (simplified - in real app, use face detection)
    const faceCenterX = width / 2
    const faceCenterY = height / 2 - 50
    const faceWidth = width * 0.3
    const faceHeight = height * 0.4

    // Load spectacle image
    const spectacleImg = new Image()
    spectacleImg.crossOrigin = 'anonymous'
    
    spectacleImg.onload = () => {
      // Calculate spectacle position and size
      const spectacleWidth = faceWidth * 0.8
      const spectacleHeight = (spectacleImg.height / spectacleImg.width) * spectacleWidth
      
      const spectacleX = faceCenterX - spectacleWidth / 2
      const spectacleY = faceCenterY - faceHeight * 0.3

      // Apply transformations
      ctx.save()
      ctx.translate(faceCenterX, faceCenterY)
      ctx.rotate((rotation * Math.PI) / 180)
      ctx.scale(zoom, zoom)
      ctx.translate(-faceCenterX, -faceCenterY)

      // Draw spectacle with transparency
      ctx.globalAlpha = 0.8
      ctx.drawImage(spectacleImg, spectacleX, spectacleY, spectacleWidth, spectacleHeight)
      ctx.restore()
    }

    spectacleImg.src = spectacle.image_url || '/placeholder-spectacle.jpg'
  }

  const addBrandingOverlay = (ctx: CanvasRenderingContext2D, width: number, height: number) => {
    ctx.save()
    
    // Add watermark
    ctx.fillStyle = 'rgba(0, 0, 0, 0.3)'
    ctx.fillRect(10, height - 60, width - 20, 50)
    
    ctx.fillStyle = 'white'
    ctx.font = '16px Arial'
    ctx.textAlign = 'left'
    ctx.fillText(`MAU Eye Care - ${spectacle.name}`, 20, height - 40)
    ctx.fillText(`₹${spectacle.price.toLocaleString()}`, 20, height - 20)
    
    ctx.restore()
  }

  const downloadImage = () => {
    if (!capturedImage) return

    const link = document.createElement('a')
    link.download = `try-on-${spectacle.name.replace(/\s+/g, '-')}.png`
    link.href = capturedImage
    link.click()
  }

  const shareImage = async () => {
    if (!capturedImage) return

    try {
      if (navigator.share) {
        const blob = await fetch(capturedImage).then(r => r.blob())
        const file = new File([blob], `try-on-${spectacle.name}.png`, { type: 'image/png' })
        
        await navigator.share({
          title: `Try-on: ${spectacle.name}`,
          text: `Check out how I look in these ${spectacle.brand} spectacles!`,
          files: [file]
        })
      } else {
        // Fallback: copy to clipboard
        await navigator.clipboard.writeText(capturedImage)
        toast.success('Image URL copied to clipboard')
      }
    } catch (error) {
      console.error('Error sharing image:', error)
      toast.error('Unable to share image')
    }
  }

  const resetView = () => {
    setZoom(1)
    setRotation(0)
    setCurrentView('front')
  }

  const handleAddToCart = () => {
    if (!spectacle.in_stock || spectacle.quantity === 0) {
      toast.error('This spectacle is out of stock')
      return
    }
    onAddToCart(spectacle)
    toast.success(`${spectacle.name} added to cart`)
  }

  if (isLoading) {
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
        <div className="bg-white rounded-lg p-8 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Initializing camera...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-6xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-gray-200">
          <div className="flex items-center gap-4">
            <button
              onClick={onClose}
              className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-full transition-colors"
            >
              <X size={20} />
            </button>
            <div>
              <h2 className="text-xl font-bold text-gray-900">Virtual Try-On</h2>
              <p className="text-sm text-gray-600">{spectacle.name} - {spectacle.brand}</p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            <span className="text-lg font-bold text-blue-600">₹{spectacle.price.toLocaleString()}</span>
            <button
              onClick={handleAddToCart}
              disabled={!spectacle.in_stock || spectacle.quantity === 0}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
            >
              Add to Cart
            </button>
          </div>
        </div>

        <div className="flex h-[calc(90vh-120px)]">
          {/* Camera View */}
          <div className="flex-1 relative bg-black">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
            
            {/* Spectacle Overlay */}
            <div 
              className="absolute inset-0 pointer-events-none"
              style={{
                transform: `scale(${zoom}) rotate(${rotation}deg)`,
                transformOrigin: 'center center'
              }}
            >
              <img
                src={spectacle.image_url || '/placeholder-spectacle.jpg'}
                alt={spectacle.name}
                className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-48 h-32 object-contain opacity-80"
              />
            </div>

            {/* Hidden canvas for capture */}
            <canvas ref={canvasRef} className="hidden" />
          </div>

          {/* Controls Panel */}
          <div className="w-80 bg-gray-50 p-4 overflow-y-auto">
            <div className="space-y-6">
              {/* View Controls */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">View Controls</h3>
                <div className="space-y-3">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setCurrentView('front')}
                      className={`flex-1 py-2 px-3 rounded-lg text-sm transition-colors ${
                        currentView === 'front' 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-white text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      Front
                    </button>
                    <button
                      onClick={() => setCurrentView('side')}
                      className={`flex-1 py-2 px-3 rounded-lg text-sm transition-colors ${
                        currentView === 'side' 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-white text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      Side
                    </button>
                    <button
                      onClick={() => setCurrentView('angle')}
                      className={`flex-1 py-2 px-3 rounded-lg text-sm transition-colors ${
                        currentView === 'angle' 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-white text-gray-700 hover:bg-gray-100'
                      }`}
                    >
                      Angle
                    </button>
                  </div>
                </div>
              </div>

              {/* Zoom Controls */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Zoom</h3>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setZoom(Math.max(0.5, zoom - 0.1))}
                    className="p-2 bg-white rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <ZoomOut size={16} />
                  </button>
                  <div className="flex-1 bg-white rounded-lg px-3 py-2 text-center">
                    {Math.round(zoom * 100)}%
                  </div>
                  <button
                    onClick={() => setZoom(Math.min(2, zoom + 0.1))}
                    className="p-2 bg-white rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <ZoomIn size={16} />
                  </button>
                </div>
              </div>

              {/* Rotation Controls */}
              <div>
                <h3 className="font-semibold text-gray-900 mb-3">Rotation</h3>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setRotation(rotation - 15)}
                    className="p-2 bg-white rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <ChevronLeft size={16} />
                  </button>
                  <div className="flex-1 bg-white rounded-lg px-3 py-2 text-center">
                    {rotation}°
                  </div>
                  <button
                    onClick={() => setRotation(rotation + 15)}
                    className="p-2 bg-white rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <ChevronRight size={16} />
                  </button>
                </div>
              </div>

              {/* Reset Button */}
              <button
                onClick={resetView}
                className="w-full py-2 px-4 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors flex items-center justify-center gap-2"
              >
                <RotateCcw size={16} />
                Reset View
              </button>

              {/* Capture Button */}
              <button
                onClick={captureImage}
                disabled={isCapturing}
                className="w-full py-3 px-4 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Camera size={16} />
                {isCapturing ? 'Capturing...' : 'Capture Image'}
              </button>

              {/* Captured Image Actions */}
              {capturedImage && (
                <div className="space-y-3">
                  <img
                    src={capturedImage}
                    alt="Captured try-on"
                    className="w-full rounded-lg border border-gray-200"
                  />
                  <div className="flex gap-2">
                    <button
                      onClick={downloadImage}
                      className="flex-1 py-2 px-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
                    >
                      <Download size={16} />
                      Download
                    </button>
                    <button
                      onClick={shareImage}
                      className="flex-1 py-2 px-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors flex items-center justify-center gap-2"
                    >
                      <Share2 size={16} />
                      Share
                    </button>
                  </div>
                </div>
              )}

              {/* Spectacle Info */}
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <h3 className="font-semibold text-gray-900 mb-3">Spectacle Details</h3>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Brand:</span>
                    <span className="font-medium">{spectacle.brand}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Frame Shape:</span>
                    <span className="font-medium">{spectacle.frame_shape}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Lens Type:</span>
                    <span className="font-medium">{spectacle.lens_type}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Material:</span>
                    <span className="font-medium">{spectacle.frame_material}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Gender:</span>
                    <span className="font-medium">{spectacle.gender}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Age Group:</span>
                    <span className="font-medium">{spectacle.age_group}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
