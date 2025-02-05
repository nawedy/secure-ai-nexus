svelte
<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount, beforeUpdate } from 'svelte';
  import { authContext } from '../../contexts/AuthContext';
  import { getContext } from 'svelte';

  let code = '';
  let codeError = '';
  let attempts = 3;

  const { user, mfa, loading, error, verifyMFA } = getContext(authContext);

  onMount(() => {
    // Redirect if MFA is not needed
    if (mfa.value === 'verified' || !$user.token) {
      goto('/dashboard');
    }
  });

  beforeUpdate(() => {
    if (error.value){
        attempts--;
    }
  });

  async function handleSubmit() {
    codeError = '';

    if (!code) {
      codeError = 'Code is required';
      return;
    }

    await verifyMFA(code);
    if(mfa.value === 'verified'){
        goto('/dashboard');
    }
  }
</script>

<div class="container">
  <h1>MFA Verification</h1>
  {#if error}<div class="error">{error}</div>{/if}
  {#if attempts <= 0 }
    <div class="error">Too many incorrect attempts. Your account has been temporarily blocked.</div>
  {:else}
    <div class="attempts">Attempts remaining: {attempts}</div>
  {/if}
  <form on:submit|preventDefault={handleSubmit}>
    <div class="form-group">
      <label for="code">Verification Code:</label>
      <input type="text" id="code" bind:value={code} required inputmode="numeric" />
      {#if codeError}<div class="error">{codeError}</div>{/if}
    </div>
    <button type="submit" disabled={$loading}>
      {#if $loading}
        Verifying...
      {:else}
        Verify
      {/if}
    </button>
  </form>
</div>

<style>
  .container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    min-height: 100vh;
    background-color: #f4f4f4;
  }

  h1 {
    color: #333;
    margin-bottom: 20px;
  }

  .form-group {
    margin-bottom: 15px;
  }

  label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
  }

  input[type='text'] {
    padding: 8px;
    border: 1px solid #ddd;
    border-radius: 4px;
    width: 250px;
  }

  .error {
    color: red;
    margin-top: 5px;
  }

  button {
    background-color: #007bff;
    color: white;
    padding: 10px 15px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
  }

  button:disabled {
    background-color: #ccc;
    cursor: default;
  }
  .attempts {
    color: #333;
    margin-bottom: 10px;
    font-weight: bold;
  }


</style>