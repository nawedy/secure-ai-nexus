<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  
</script>

<main class="min-h-screen bg-gray-50">
    
  <!-- Navigation -->
  <nav class="bg-white shadow-lg fixed w-full z-50">
    <div class="max-w-7xl mx-auto px-4">
      <div class="flex justify-between h-16">
        <div class="flex items-center">
          <img class="h-8 w-auto" src="/images/logo.svg" alt="GetAISecured" />
        </div>
        <div class="flex items-center space-x-4">
          <a href="#features" class="text-gray-700 hover:text-gray-900">Features</a>
          <a href="#pricing" class="text-gray-700 hover:text-gray-900">Pricing</a>
          <a href="/login" class="text-gray-700 hover:text-gray-900">Login</a>
          <a href="/signup" class="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">Get Started</a>
        </div>
      </div>
    </div>
  </nav>

  <!-- Hero Section -->
  <section class="pt-24 bg-white">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <h1 class="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
        <span class="block">Secure Your AI Models</span>
        <span class="block text-blue-600">With Enterprise Protection</span>
      </h1>
      <p class="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
        Protect your AI applications with enterprise-grade security. Prevent data leaks, ensure model integrity, and maintain compliance.
      </p>
      <div class="mt-5 max-w-md mx-auto sm:flex sm:justify-center md:mt-8">
        <a href="/signup" class="w-full flex items-center justify-center px-8 py-3 border border-transparent text-base font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700">
          Start Free Trial
        </a>
      </div>
    </div>
  </section>

  <!-- Continue with additional sections as needed -->
</main>

<style>
</style>
