<script>
  import BusinessCard from './BusinessCard.svelte';
  
  export let neighborhood;
  export let businessCount;
  export let activeCount;
  export let types = [];
  export let avgRating = null;
  export let businesses = [];
  
  let expanded = false;
  let showAllBusinesses = false;
  
  function toggleExpanded() {
    expanded = !expanded;
  }
  
  function toggleAllBusinesses() {
    showAllBusinesses = !showAllBusinesses;
  }
  
  $: visibleBusinesses = showAllBusinesses ? businesses : businesses.slice(0, 6);
  $: hasMoreBusinesses = businesses.length > 6;
</script>

<section class="neighborhood-section" class:expanded>
  <header class="neighborhood-header" on:click={toggleExpanded}>
    <div class="neighborhood-info">
      <h2>{neighborhood}</h2>
      <div class="neighborhood-meta">
        <span class="business-count">{businessCount} businesses</span>
        <span class="active-count">{activeCount} active</span>
        {#if avgRating}
          <span class="neighborhood-rating">
            <span class="rating-stars">{'★'.repeat(Math.floor(avgRating))}{'☆'.repeat(5 - Math.floor(avgRating))}</span>
            <span class="rating-value">{avgRating.toFixed(1)}</span>
          </span>
        {/if}
      </div>
      <div class="neighborhood-types">
        {#each types.slice(0, 3) as type}
          <span class="type-badge">{type}</span>
        {/each}
        {#if types.length > 3}
          <span class="type-badge more">+{types.length - 3} more</span>
        {/if}
      </div>
    </div>
    
    <div class="neighborhood-toggle">
      <span class="expand-indicator">
        {#if expanded}
          −
        {:else}
          +
        {/if}
      </span>
    </div>
  </header>
  
  {#if expanded}
    <div class="neighborhood-content">
      <div class="business-list-neighborhood">
        {#each visibleBusinesses as business}
          <BusinessCard {business} className="neighborhood-business" />
        {/each}
      </div>
      
      {#if hasMoreBusinesses}
        <div class="load-more-section">
          <div class="load-more-controls">
            <button 
              class="load-more-btn secondary"
              on:click={toggleAllBusinesses}
            >
              {#if showAllBusinesses}
                Show Less
              {:else}
                Show {businesses.length - 6} More Businesses
              {/if}
            </button>
            <p class="business-summary">
              <small>
                Showing {showAllBusinesses ? businesses.length : Math.min(6, businesses.length)} of {businesses.length} businesses in {neighborhood}
              </small>
            </p>
          </div>
        </div>
      {/if}
    </div>
  {/if}
</section>

<style>
  .neighborhood-section {
    border: 1px solid var(--pico-border-color);
    border-radius: var(--pico-border-radius);
    overflow: hidden;
    transition: all 0.3s ease;
  }
  
  .neighborhood-section:hover {
    border-color: rgba(59, 130, 246, 0.3);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.08);
  }
  
  .neighborhood-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    padding: 1.5rem;
    background: rgba(59, 130, 246, 0.02);
    border-bottom: 1px solid rgba(59, 130, 246, 0.1);
    gap: 1rem;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .neighborhood-header:hover {
    background: rgba(59, 130, 246, 0.05);
  }
  
  .neighborhood-info {
    flex: 1;
  }
  
  .neighborhood-info h2 {
    margin: 0 0 0.5rem 0;
    font-size: 1.5rem;
    font-weight: 700;
    color: var(--pico-primary);
  }
  
  .neighborhood-meta {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 0.75rem;
    flex-wrap: wrap;
  }
  
  .business-count, .active-count {
    font-size: 0.875rem;
    font-weight: 500;
    color: var(--pico-muted-color);
  }
  
  .business-count {
    color: var(--pico-color);
  }
  
  .neighborhood-rating {
    display: flex;
    align-items: center;
    gap: 0.25rem;
  }
  
  .rating-stars {
    color: #fbbf24;
    font-size: 0.875rem;
  }
  
  .rating-value {
    font-size: 0.875rem;
    font-weight: 600;
    color: var(--pico-color);
  }
  
  .neighborhood-types {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .type-badge {
    padding: 0.25rem 0.5rem;
    background: rgba(16, 185, 129, 0.1);
    color: #059669;
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 500;
  }
  
  .type-badge.more {
    background: rgba(139, 92, 246, 0.1);
    color: #7c3aed;
    border-color: rgba(139, 92, 246, 0.2);
  }
  
  .neighborhood-toggle {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    border-radius: 50%;
    background: rgba(59, 130, 246, 0.1);
    transition: all 0.2s ease;
  }
  
  .neighborhood-header:hover .neighborhood-toggle {
    background: rgba(59, 130, 246, 0.2);
  }
  
  .expand-indicator {
    font-size: 1rem;
    color: var(--pico-primary);
    font-weight: 600;
    line-height: 1;
  }
  
  .neighborhood-content {
    padding: 1.5rem;
    background: var(--pico-background-color);
  }
  
  .business-list-neighborhood {
    display: flex;
    flex-direction: column;
    gap: var(--pico-spacing);
  }
  
  .load-more-section {
    margin-top: 1.5rem;
  }
  
  .load-more-controls {
    text-align: center;
    padding: 1.5rem;
    background: rgba(249, 250, 251, 0.5);
    border: 1px solid var(--pico-border-color);
    border-radius: var(--pico-border-radius);
  }
  
  .load-more-btn {
    padding: 0.75rem 1.5rem;
    border-radius: var(--pico-border-radius);
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    border: none;
    background: var(--pico-secondary-background);
    color: var(--pico-secondary-color);
    margin-bottom: 0.5rem;
  }
  
  .load-more-btn:hover {
    background: var(--pico-secondary-hover-background);
    transform: translateY(-1px);
  }
  
  .business-summary {
    margin: 0;
    color: var(--pico-muted-color);
    font-size: 0.875rem;
  }
  
  /* Mobile Responsive */
  @media (max-width: 768px) {
    .neighborhood-header {
      padding: 1rem;
      align-items: center;
    }
    
    .neighborhood-info h2 {
      font-size: 1.25rem;
    }
    
    .neighborhood-meta {
      gap: 0.75rem;
    }
    
    .neighborhood-toggle {
      width: 1.5rem;
      height: 1.5rem;
    }
    
    .expand-indicator {
      font-size: 0.7rem;
    }
    
    .neighborhood-content {
      padding: 1rem;
    }
    
    .business-header {
      flex-direction: column;
      align-items: flex-start;
    }
    
    .business-meta {
      gap: 0.5rem;
    }
  }
</style>