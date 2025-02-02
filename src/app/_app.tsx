import React from 'react'
import { AppProps } from 'next/app'
import { AuthProvider } from '../context/AuthContext'
import '../styles/globals.css' // Ensure you have global styles

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <AuthProvider>
      <Component {...pageProps} />
    </AuthProvider>
  )
}

export default MyApp
