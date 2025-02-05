<script lang="ts">
  import { goto } from '$app/navigation';
  import { onMount, onDestroy, beforeUpdate } from 'svelte';
  import { authStore, type AuthStore } from '../../contexts/AuthContext';
  import { get } from 'svelte/store';
  let error = '';

  let unsubscribe: any;

  onMount(() => {
    unsubscribe = authStore.subscribe((store) => {
      if (!store.user) {
        goto('/login');
      }
    });
  });

  async function logout() {
    const store = get(authStore);
    
    if (store) {
      await store.logout();
      goto('/login');
    } else {
      console.error('AuthStore is not initialized.');
    }
  }
</script>

<div class="container">
  <h1>Dashboard</h1>
  {#if error}<div class="error">{error}</div>{/if}
  <p>Welcome to the dashboard!</p>
  <button on:click={logout} class="logout">Logout</button>
</div>

<style>
  .logout {
    background-color: #f44336;
    color: white;
    padding: 10px 20px;
    border: none;
  }
</style>
