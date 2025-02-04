<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';
  let password = '';
  let error = '';
  let loading = false;
  let passwordError = '';
  let token = '';


  onMount(() => {
    // Get the token from the query parameters
    const urlParams = new URLSearchParams(window.location.search);
    token = urlParams.get('token') || '';

    if (!token) {
      goto('/password-reset');
    }
  });



  async function handleSubmit() {
    loading = true;
    error = '';
    passwordError = '';

    // Simple form validation
    if (!password) {
        passwordError = 'Password is required';
    }

    if(passwordError){
      loading = false;
      return
    }

    try {

      const response = await fetch(`/api/auth/reset-password?token=${token}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ password }),
      });

      if (response.ok) {
        goto('/login');
      } else {
        const data = await response.json();
        error = data.detail || 'Password reset failed';
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
  <h1>Reset Password</h1>
  {#if error}<div class="error">{error}</div>{/if}
  <form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
      <label for="password">New password:</label>
      <input type="password" id="password" bind:value={password} required />
      {#if passwordError}<div class="error">{passwordError}</div>{/if}
    </div>
    <button type="submit" disabled={loading}>Reset Password</button>
  </form>
</div>

<style>

</style>
