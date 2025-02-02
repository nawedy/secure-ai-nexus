import React from 'react'
import Link from 'next/link'

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-lg fixed w-full z-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <img className="h-8 w-auto" src="/images/logo.svg" alt="GetAISecured" />
            </div>
            <div className="flex items-center space-x-4">
              <Link href="#features"><a className="text-gray-700 hover:text-gray-900">Features</a></Link>
              <Link href="#pricing"><a className="text-gray-700 hover:text-gray-900">Pricing</a></Link>
              <Link href="/login"><a className="text-gray-700 hover:text-gray-900">Login</a></Link>
              <Link href="#contact">
                <a className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">Get Started</a>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-24 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
            <span className="block">Secure Your AI Models</span>
            <span className="block text-blue-600">With Enterprise Protection</span>
          </h1>
          <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
            Protect your AI applications with enterprise-grade security. Prevent data leaks, ensure model integrity, and maintain compliance.
          </p>
          <div className="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
            <Link href="#contact">
              <a className="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
                Start Free Trial
              </a>
            </Link>
          </div>
        </div>
      </section>

      {/* Continue with additional sections as needed */}
    </main>
  )
}
