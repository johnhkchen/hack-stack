<script>
  let query = '';
  let isLoading = false;
  let results = null;
  let error = null;
  let showResults = false;

  function scrollToBusinessCard(businessId, businessName) {
    // Try multiple possible ID formats to find the business card
    const possibleIds = [
      `business-card-${businessId}`,
      `business-card-${businessName.toLowerCase().replace(/\s+/g, '-')}`,
      `business-card-${businessName.toLowerCase().replace(/[^a-z0-9]/g, '-')}`,
      `business-card-${businessName.toLowerCase().replace(/\s+/g, '').replace(/[^a-z0-9]/g, '')}`
    ];

    let targetElement = null;
    
    for (const id of possibleIds) {
      targetElement = document.getElementById(id);
      if (targetElement) break;
    }
    
    if (targetElement) {
      targetElement.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      });
      
      // Add a brief highlight effect
      targetElement.style.transition = 'all 0.3s ease';
      targetElement.style.boxShadow = '0 0 20px rgba(59, 130, 246, 0.3)';
      targetElement.style.borderColor = 'rgba(59, 130, 246, 0.5)';
      
      setTimeout(() => {
        targetElement.style.boxShadow = '';
        targetElement.style.borderColor = '';
      }, 2000);
    } else {
      // Fallback: scroll to business showcase section
      const businessShowcase = document.querySelector('.business-showcase');
      if (businessShowcase) {
        businessShowcase.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start' 
        });
      }
    }
  }

  async function searchBusinesses(searchQuery = null) {
    const searchText = searchQuery || query.trim();
    
    if (!searchText) return;
    
    if (searchQuery) {
      query = searchQuery;
    }
    
    isLoading = true;
    error = null;
    showResults = true;
    results = null;
    
    try {
      const apiResponse = await fetch(`/api/search?q=${encodeURIComponent(searchText)}&limit=10`);
      
      if (!apiResponse.ok) {
        throw new Error(`HTTP ${apiResponse.status}: ${apiResponse.statusText}`);
      }
      
      const data = await apiResponse.json();
      results = data;
      
    } catch (err) {
      console.error('Search failed:', err);
      error = 'Search failed. Please try again.';
    } finally {
      isLoading = false;
    }
  }

  function handleKeyPress(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      searchBusinesses();
    }
  }
</script>

<section class="search-section">
  <article>
    <header>
      <h3>Search Legacy Businesses</h3>
      <p>Find historic businesses by name, neighborhood, or type</p>
    </header>
    
    <div class="search-interface">
      <form on:submit|preventDefault={() => searchBusinesses()}>
        <div class="search-input-wrapper">
          <input 
            type="text" 
            bind:value={query}
            on:keypress={handleKeyPress}
            placeholder="Search by business name, neighborhood, or type..."
            disabled={isLoading}
          />
          <button 
            type="submit"
            disabled={isLoading || !query.trim()}
          >
            {isLoading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>
      
      {#if showResults}
        <div class="search-results">
          {#if isLoading}
            <p aria-busy="true">Searching businesses...</p>
          {:else if error}
            <p class="error">{error}</p>
          {:else if results}
            {#if results.results && results.results.length > 0}
              <header>
                <h4>Found {results.results.length} businesses</h4>
              </header>
              <div class="results-grid">
                {#each results.results as business}
                  <article class="business-result">
                    <header>
                      <h4>{business.name}</h4>
                      <p><small><strong>{business.type}</strong> • {business.neighborhood} • Est. {business.established}</small></p>
                    </header>
                    <p>{business.story ? business.story.substring(0, 200) + '...' : 'No description available'}</p>
                    <div class="result-actions">
                      <button 
                        type="button"
                        class="scroll-to-card-btn secondary"
                        on:click={() => scrollToBusinessCard(business.id, business.name)}
                        title="Scroll to full business card"
                      >
                        View Full Details ↓
                      </button>
                    </div>
                  </article>
                {/each}
              </div>
            {:else}
              <p>No businesses found matching your search.</p>
            {/if}
          {/if}
        </div>
      {/if}
    </div>
  </article>
</section>

<style>
  .search-section {
    margin: 2rem 0;
  }

  .search-section header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .search-input-wrapper {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }

  .search-results {
    margin-top: 1.5rem;
  }

  .results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }

  .business-result {
    margin-bottom: 0;
  }

  .business-result header {
    margin-bottom: 0.5rem;
  }

  .business-result h4 {
    margin-bottom: 0.25rem;
  }

  .error {
    color: var(--pico-del-color);
    font-weight: 500;
  }

  .result-actions {
    margin-top: 1rem;
    text-align: center;
  }

  .scroll-to-card-btn {
    font-size: 0.875rem;
    padding: 0.5rem 1rem;
    border-radius: var(--pico-border-radius);
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid var(--pico-secondary-border);
    background: var(--pico-secondary-background);
    color: var(--pico-secondary-color);
  }

  .scroll-to-card-btn:hover {
    background: var(--pico-secondary-hover-background);
    transform: translateY(-1px);
  }

  .scroll-to-card-btn:active {
    transform: translateY(0);
  }

  /* Responsive Design */
  @media (min-width: 768px) {
    .search-input-wrapper {
      flex-direction: row;
    }
    
    .search-input-wrapper input {
      flex: 1;
    }
  }

  @media (max-width: 768px) {
    .results-grid {
      grid-template-columns: 1fr;
    }
  }

  @media (max-width: 480px) {
    .search-input-wrapper input {
      padding: 0.5rem;
      font-size: 0.9rem;
    }

    .search-input-wrapper button {
      padding: 0.5rem 0.75rem;
      font-size: 0.9rem;
    }

    .search-results {
      margin-top: 1.5rem;
      border-radius: 0.25rem;
    }

    .results-grid {
      grid-template-columns: 1fr;
      gap: 0.75rem;
      margin-top: 1rem;
    }

    .business-result {
      padding: 0.5rem;
      border-radius: 0.25rem;
    }

    .business-result header {
      margin-bottom: 0.5rem;
    }

    .business-result h4 {
      font-size: 1rem;
      margin-bottom: 0.25rem;
      line-height: 1.3;
    }

    .business-result p {
      font-size: 0.8rem;
      margin-bottom: 0.5rem;
      line-height: 1.4;
    }
  }
</style>