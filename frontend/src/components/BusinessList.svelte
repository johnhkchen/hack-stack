<script>
  import { onMount } from 'svelte';
  
  let businesses = [];
  let loading = true;
  let error = null;
  
  onMount(async () => {
    try {
      const response = await fetch('/api/businesses');
      businesses = await response.json();
      loading = false;
    } catch (err) {
      error = err.message;
      loading = false;
    }
  });
</script>

{#if loading}
  <div aria-busy="true">Loading businesses...</div>
{:else if error}
  <div class="error">Error: {error}</div>
{:else}
  <div class="business-list">
    {#each businesses as business}
      <div class="business-card">
        <h3>{business.name}</h3>
        <p class="tagline"><em>{business.tagline}</em></p>
        <p class="story">{business.story}</p>
        
        <div class="business-meta">
          <div class="meta-row">
            <strong>Type:</strong> {business.type} | 
            <strong>Founded:</strong> {business.founded} |
            <strong>Neighborhood:</strong> {business.neighborhood}
          </div>
          
          <div class="features">
            {#each business.features as feature}
              <span class="feature-tag">{feature}</span>
            {/each}
          </div>
          
          <div class="status-container">
            <span class="status-badge {business.status}">{business.status.replace('_', ' ')}</span>
          </div>
        </div>
      </div>
    {/each}
  </div>
{/if}

<style>
  .business-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .business-card {
    border: 1px solid var(--pico-primary-border);
    border-radius: 0.5rem;
    padding: 1.5rem;
    background: var(--pico-card-background-color);
    transition: all 0.2s ease;
  }
  
  .business-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.1);
  }
  
  .tagline {
    color: var(--pico-muted-color);
    font-size: 1.1rem;
    margin-bottom: 1rem;
  }
  
  .story {
    line-height: 1.6;
    margin-bottom: 1rem;
  }
  
  .business-meta {
    border-top: 1px solid var(--pico-border-color);
    padding-top: 1rem;
    margin-top: 1rem;
  }
  
  .meta-row {
    font-size: 0.9rem;
    color: var(--pico-muted-color);
    margin-bottom: 0.5rem;
  }
  
  .features {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }
  
  .feature-tag {
    background: var(--pico-primary-background);
    color: var(--pico-primary-color);
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.8rem;
    font-weight: 500;
  }
  
  .status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.875rem;
    font-weight: 500;
    text-transform: capitalize;
  }
  
  .thriving { 
    background: #d4edda; 
    color: #155724; 
  }
  
  .legendary { 
    background: #fff3cd; 
    color: #856404; 
  }
  
  .cult_following { 
    background: #f8d7da; 
    color: #721c24; 
  }
  
  .error {
    color: var(--pico-del-color);
    background: var(--pico-del-background-color);
    padding: 1rem;
    border-radius: 0.5rem;
  }
</style>