<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  let email = '';
  let password = '';
  let error = '';
  let loading = false;
  let emailError = '';
  let passwordError = '';

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

    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, password }),
      });

      if (response.ok) {
       
        goto('/login');
      } else {
        const data = await response.json();
        error = data.detail || 'Registration failed';
        if(Array.isArray(data.detail)){
            error = data.detail[0].msg;
        }
      }
    } catch (err) {
      error = 'An error occurred';
    } finally {
      loading = false;
    }
  }


</script>

<div class="container">
  <h1>Register</h1>
  {#if error}<div class="error">{error}</div>{/if}
  <form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
        <label for="email">Email:</label>
        <input type="email" id="email" bind:value={email} required />
        {#if emailError}<div class="error">{emailError}</div>{/if}
    </div>
    <div class="form-group">
      <label for="password">Password:</label>
      <input type="password" id="password" bind:value={password} required />
      {#if passwordError}<div class="error">{passwordError}</div>{/if}
    </div>
    <button type="submit" disabled={loading}>Register</button>
  </form>
</div>

<style>

</style>
