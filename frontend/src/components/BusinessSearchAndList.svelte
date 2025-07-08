<script>
  import BusinessCard from './BusinessCard.svelte';
  import NeighborhoodCard from './NeighborhoodCard.svelte';
  import { onMount } from 'svelte';

  // Search functionality
  let searchQuery = '';
  let searchResults = null;
  let isSearching = false;
  let searchError = null;
  let showSearchResults = false;
  
  // Business list functionality
  let businesses = [];
  let businessError = null;
  let isLoading = true;
  let enableNeighborhoodGrouping = true;
  let enableFiltering = true;
  let limit = 15;
  
  // Computed values for business organization
  $: organizedData = organizeBusinesses(businesses);
  $: filteredBusinesses = businesses; // Can be extended with filters later
  
  function organizeBusinesses(businesses) {
    if (!businesses || businesses.length === 0) {
      return { neighborhoods: [], ungroupedBusinesses: [] };
    }
    
    const neighborhoodMap = {};
    const ungroupedBusinesses = [];
    
    businesses.forEach(business => {
      if (business.neighborhood) {
        if (!neighborhoodMap[business.neighborhood]) {
          neighborhoodMap[business.neighborhood] = [];
        }
        neighborhoodMap[business.neighborhood].push(business);
      } else {
        ungroupedBusinesses.push(business);
      }
    });
    
    const neighborhoods = Object.entries(neighborhoodMap)
      .map(([neighborhood, businesses]) => {
        const types = [...new Set(businesses.map(b => b.type))];
        const activeCount = businesses.filter(b => b.status === 'Active').length;
        const avgRating = businesses.reduce((sum, b) => sum + (b.rating || 0), 0) / businesses.length;
        
        return {
          name: neighborhood,
          businesses,
          businessCount: businesses.length,
          activeCount,
          types,
          avgRating: avgRating > 0 ? avgRating : null
        };
      })
      .sort((a, b) => b.businessCount - a.businessCount);
    
    return { neighborhoods, ungroupedBusinesses };
  }
  
  async function loadBusinesses() {
    isLoading = true;
    businessError = null;
    
    try {
      const response = await fetch(`/api/businesses?limit=${limit}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      businesses = Array.isArray(data) ? data : (data.businesses || []);
      
    } catch (err) {
      console.error('Failed to load businesses:', err);
      businessError = `Failed to load businesses: ${err.message}`;
    } finally {
      isLoading = false;
    }
  }
  
  async function searchBusinesses(searchText = null) {
    const query = searchText || searchQuery.trim();
    
    if (!query) return;
    
    isSearching = true;
    searchError = null;
    showSearchResults = true;
    searchResults = null;
    
    try {
      const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&limit=10`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      searchResults = data;
      
    } catch (err) {
      console.error('Search failed:', err);
      searchError = 'Search failed. Please try again.';
    } finally {
      isSearching = false;
    }
  }
  
  function scrollToBusinessCard(businessId, businessName) {
    // Find the business in our data to get its neighborhood
    const business = businesses.find(b => b.id === businessId || b.name === businessName);
    
    console.log('Scrolling to business:', businessName, 'in neighborhood:', business?.neighborhood);
    
    if (business && business.neighborhood) {
      // First, expand the neighborhood
      const expanded = expandNeighborhood(business.neighborhood);
      
      // Wait for the expansion animation to complete, then scroll
      const delay = expanded ? 300 : 100; // More time if we expanded
      setTimeout(() => {
        scrollToSpecificCard(businessId, businessName);
      }, delay);
    } else {
      // If no neighborhood found, try direct scroll
      scrollToSpecificCard(businessId, businessName);
    }
  }
  
  function expandNeighborhood(neighborhoodName) {
    // Find and expand the neighborhood card
    const neighborhoodCards = document.querySelectorAll('.neighborhood-section');
    let expanded = false;
    
    neighborhoodCards.forEach(card => {
      const headerText = card.querySelector('h2')?.textContent;
      if (headerText === neighborhoodName) {
        const header = card.querySelector('.neighborhood-header');
        const isCurrentlyExpanded = card.classList.contains('expanded');
        
        console.log('Found neighborhood card:', neighborhoodName, 'expanded:', isCurrentlyExpanded);
        
        if (header && !isCurrentlyExpanded) {
          header.click(); // Trigger the toggle
          expanded = true;
          console.log('Expanded neighborhood:', neighborhoodName);
        }
      }
    });
    
    return expanded;
  }
  
  function scrollToSpecificCard(businessId, businessName) {
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
      if (targetElement) {
        console.log('Found target element with ID:', id);
        break;
      }
    }
    
    if (targetElement) {
      targetElement.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'center' 
      });
      
      // Add a brief highlight effect
      // The targetElement should be the article with class business-card
      const businessCard = targetElement.classList.contains('business-card') ? targetElement : targetElement.querySelector('.business-card');
      
      if (businessCard) {
        console.log('Applying highlight to:', businessCard);
        
        // Store original styles
        const originalBoxShadow = businessCard.style.boxShadow;
        const originalBorder = businessCard.style.border;
        const originalTransition = businessCard.style.transition;
        
        // Apply highlight effect
        businessCard.style.transition = 'all 0.3s ease';
        businessCard.style.boxShadow = '0 0 20px rgba(59, 130, 246, 0.6)';
        businessCard.style.border = '2px solid rgba(59, 130, 246, 0.8)';
        
        // Remove highlight after 2 seconds
        setTimeout(() => {
          businessCard.style.boxShadow = originalBoxShadow;
          businessCard.style.border = originalBorder;
          businessCard.style.transition = originalTransition;
        }, 2000);
      } else {
        console.log('Could not find business card element for highlighting');
      }
    } else {
      console.log('Could not find target element, trying all IDs:', possibleIds);
      // Fallback: scroll to business showcase section
      const businessShowcase = document.querySelector('.business-list-section');
      if (businessShowcase) {
        businessShowcase.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'start' 
        });
      }
    }
  }
  
  function handleSearchKeyPress(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      searchBusinesses();
    }
  }
  
  function handleSearchSubmit(event) {
    event.preventDefault();
    searchBusinesses();
  }
  
  function handleExampleClick(event, exampleQuery) {
    event.preventDefault();
    searchQuery = exampleQuery;
    searchBusinesses(exampleQuery);
  }
  
  onMount(() => {
    loadBusinesses();
  });
</script>

<!-- Search Section -->
<section class="search-section">
  <article>
    <header>
      <h3>Search Legacy Businesses</h3>
      <p>Find historic businesses by name, neighborhood, or type</p>
    </header>
    
    <div class="search-interface">
      <form on:submit={handleSearchSubmit}>
        <div class="search-input-wrapper">
          <textarea 
            bind:value={searchQuery}
            on:keypress={handleSearchKeyPress}
            placeholder="Search by business name, neighborhood, or type..."
            disabled={isSearching}
            rows="2"
          ></textarea>
          <button 
            type="submit"
            disabled={isSearching || !searchQuery.trim()}
          >
            {isSearching ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>
      
      {#if showSearchResults}
        <div class="search-results">
          {#if isSearching}
            <p aria-busy="true">Searching businesses...</p>
          {:else if searchError}
            <p class="error">{searchError}</p>
          {:else if searchResults}
            {#if searchResults.results && searchResults.results.length > 0}
              <header>
                <h4>Found {searchResults.results.length} businesses - click "View Full Details" to jump to the card below</h4>
              </header>
              <div class="results-grid">
                {#each searchResults.results as business}
                  <article class="business-result">
                    <header>
                      <h4>{business.name}</h4>
                      <p><small><strong>{business.type}</strong> • {business.neighborhood} • Est. {business.established}</small></p>
                    </header>
                    <p>
                      {(() => {
                        const description = business.story || business.founding_story || business.cultural_impact || business.unique_features || business.description;
                        if (description) {
                          return description.length > 200 ? description.substring(0, 200) + '...' : description;
                        }
                        return 'No description available';
                      })()}
                    </p>
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

<!-- Business List Section -->
<section class="business-list-section">
  <article>
    <header>
      <h2>Historic Business Registry</h2>
      <p>Documented heritage applications with cultural significance, community impact, and narrative preservation spanning generations of San Francisco history</p>
    </header>
    
    {#if isLoading}
      <p aria-busy="true">Loading businesses...</p>
    {:else if businessError}
      <p class="error">{businessError}</p>
    {:else if businesses && businesses.length > 0}
      {#if enableNeighborhoodGrouping && organizedData.neighborhoods.length > 0}
        <div class="neighborhood-grouping">
          {#each organizedData.neighborhoods as neighborhood}
            <NeighborhoodCard
              neighborhood={neighborhood.name}
              businessCount={neighborhood.businessCount}
              activeCount={neighborhood.activeCount}
              types={neighborhood.types}
              avgRating={neighborhood.avgRating}
              businesses={neighborhood.businesses}
            />
          {/each}
        </div>
      {:else}
        <div class="business-grid">
          {#each filteredBusinesses as business}
            <BusinessCard {business} />
          {/each}
        </div>
      {/if}
      
      {#if organizedData.ungroupedBusinesses.length > 0}
        <div class="ungrouped-businesses">
          <h3>Other Businesses</h3>
          <div class="business-grid">
            {#each organizedData.ungroupedBusinesses as business}
              <BusinessCard {business} />
            {/each}
          </div>
        </div>
      {/if}
    {:else}
      <p>No businesses found.</p>
    {/if}
  </article>
</section>

<style>
  /* Search Section Styles */
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

  .error {
    color: var(--pico-del-color);
    font-weight: 500;
  }

  /* Business List Section Styles */
  .business-list-section {
    margin: 3rem 0;
  }

  .business-list-section header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .business-list-section h2 {
    color: var(--pico-primary);
    margin-bottom: 1rem;
  }

  .business-list-section p {
    color: var(--pico-muted-color);
    line-height: 1.6;
    max-width: 700px;
    margin: 0 auto;
  }

  .neighborhood-grouping {
    display: flex;
    flex-direction: column;
    gap: var(--pico-spacing);
  }

  .business-grid {
    display: flex;
    flex-direction: column;
    gap: var(--pico-spacing);
  }

  .ungrouped-businesses {
    margin-top: 2rem;
  }

  .ungrouped-businesses h3 {
    color: var(--pico-primary);
    margin-bottom: 1rem;
    text-align: center;
  }

  /* Responsive Design */
  @media (min-width: 768px) {
    .search-input-wrapper {
      flex-direction: row;
      align-items: flex-start;
    }
    
    .search-input-wrapper textarea {
      flex: 1;
      min-height: 60px;
      resize: vertical;
    }
  }

  @media (max-width: 768px) {
    .results-grid {
      grid-template-columns: 1fr;
    }
  }

  @media (max-width: 480px) {
    .search-input-wrapper textarea {
      padding: 0.5rem;
      font-size: 0.9rem;
      min-height: 50px;
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

    .business-list-section h2 {
      font-size: 1.25rem;
      margin-bottom: 0.75rem;
      line-height: 1.4;
    }

    .business-list-section header p {
      font-size: 0.85rem;
      margin: 0;
      padding: 0;
      line-height: 1.5;
    }
  }
</style>