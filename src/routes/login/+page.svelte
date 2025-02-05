<script lang="ts">
  import { goto } from '$app/navigation';
  import { enhance } from '$app/forms';
  import { auth } from '../../contexts/AuthContext';
  import { invalidate } from '$app/navigation';
  import type { SubmitFunction } from '@sveltejs/kit';

  export let form;

  let email = '';
  let password = '';
  let loading = false;
  let submitting = false;

  const submit: SubmitFunction = () => {
    submitting = true;
    return async ({ update }) => {
        await update();
        submitting = false;
    };
};
  async function handleSubmit() {
    loading = true;
    error = '';
    emailError = '';
    passwordError = '';


    // Simple form validation
    if (!email) {
        emailError = 'Email is required';
    } else if (!/^[w-.]+@([w-]+.)+[w-]{2,4}$/.test(email)) {
        emailError = 'Invalid email format';
    }

    if (!password) {
        passwordError = 'Password is required';
    }

    if(emailError || passwordError){
      loading = false;
      return
    }


    const loginResult = await $auth.login(email, password);
    if (loginResult.success) {
      if ($auth.needsMFA) {
        goto('/mfa');
      } else {
        goto('/dashboard');
      }
    } else {
      error = loginResult.error || 'Login failed';
      if (Array.isArray(loginResult.error)) {
        error = loginResult.error[0].msg;
      }
    }
    loading = false;
    
    if ($auth.error) {
      error = $auth.error;
    }
  }


</script>
<svelte:head>
	<title>Login</title>
	<meta name="description" content="Login" />
</svelte:head>
<main class="flex flex-col items-center justify-center h-screen bg-gray-100">
    <div class="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4 flex flex-col w-80">
        <h1 class="text-2xl font-bold mb-6 text-center">Login</h1>
        {#if form?.error}
            <div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                <strong class="font-bold">Error! </strong>
                <span class="block sm:inline">{form.error}</span>
            </div>
        {/if}
        <form method="POST" use:enhance={submit} on:submit|preventDefault={handleSubmit}>
            <div class="mb-4">
                <label class="block text-gray-700 text-sm font-bold mb-2" for="email">
                    Email
                </label>
                <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline {form?.emailError ? 'border-red-500' : 'border-gray-300'}" id="email" type="email" placeholder="Email" bind:value={email} aria-invalid={form?.emailError ? 'true' : 'false'} aria-describedby="email-error" />
                {#if form?.emailError}
                    <p class="text-red-500 text-xs italic mt-1" id="email-error">{form.emailError}</p>
                {/if}
            </div>
            <div class="mb-6">
                <label class="block text-gray-700 text-sm font-bold mb-2" for="password">
                    Password
                </label>
                <input class="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline {form?.passwordError ? 'border-red-500' : 'border-gray-300'}" id="password" type="password" placeholder="Password" bind:value={password} aria-invalid={form?.passwordError ? 'true' : 'false'} aria-describedby="password-error" />
                {#if form?.passwordError}
                    <p class="text-red-500 text-xs italic mt-1" id="password-error">{form.passwordError}</p>
                {/if}
            </div>
            <div class="flex items-center justify-between">
                <button class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="submit" disabled={loading || submitting}>
                    {#if submitting}
                        Loading...
                    {:else}
                        Login
                    {/if}
                </button>
                <a class="inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800" href="/password-reset">
                    Forgot Password?
                </a>
            </div>
        </form>
        <div class="mt-4 text-center">
            <a class="inline-block text-sm text-blue-500 hover:text-blue-800" href="/signup">
                Don't have an account? Sign up
            </a>
        </div>
    </div>
</main>

<style global>
	/* Apply Tailwind's base styles */
	@tailwind base;
	@tailwind components;
	@tailwind utilities;
  
  .input-error{
    border-color: #dc2626;
  }
  .container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100vh;
        background-color: #f7f7f7;
    }
    .form-group {
        margin-bottom: 1rem;
        width: 100%;
    }
  
</style>
