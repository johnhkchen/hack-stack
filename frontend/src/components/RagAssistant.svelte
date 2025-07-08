<script>
  let query = '';
  let isLoading = false;
  let response = null;
  let error = null;
  let showResponse = false;

  const exampleQueries = [
    'traditional food businesses',
    'family-owned businesses',
    'historic landmarks'
  ];

  async function askQuery(queryText = null) {
    const questionText = queryText || query.trim();
    
    if (!questionText) return;
    
    if (queryText) {
      query = queryText;
    }
    
    isLoading = true;
    error = null;
    showResponse = true;
    response = null;
    
    try {
      const apiResponse = await fetch('/api/v2/rag/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: questionText,
          max_results: 5
        })
      });
      
      if (!apiResponse.ok) {
        throw new Error(`HTTP ${apiResponse.status}: ${apiResponse.statusText}`);
      }
      
      const data = await apiResponse.json();
      response = data;
      
    } catch (err) {
      console.error('RAG query failed:', err);
      error = 'Sorry, I couldn\'t process your query right now. Please try again.';
    } finally {
      isLoading = false;
    }
  }

  function handleKeyPress(event) {
    if (event.key === 'Enter') {
      event.preventDefault();
      askQuery();
    }
  }

  function handleExampleClick(event, exampleQuery) {
    event.preventDefault();
    askQuery(exampleQuery);
  }
</script>

<section class="rag-section">
  <article>
    <header>
      <h2>🤖 Legacy Business Knowledge Assistant</h2>
      <p>Ask natural language questions about San Francisco's historic businesses and cultural heritage.</p>
    </header>
    
    <div class="rag-interface">
      <form on:submit|preventDefault={() => askQuery()}>
        <div class="query-input-section">
          <textarea 
            bind:value={query}
            on:keypress={handleKeyPress}
            placeholder="Ask about traditional food businesses, family-owned shops, or historic landmarks..."
            disabled={isLoading}
            rows="2"
          ></textarea>
          <button 
            type="submit"
            disabled={isLoading || !query.trim()}
          >
            {isLoading ? 'Thinking...' : 'Ask Assistant'}
          </button>
        </div>
      </form>
      
      <div class="demo-queries">
        <small><strong>Try these examples:</strong></small>
        <div class="query-examples">
          {#each exampleQueries as example}
            <button 
              type="button"
              class="query-example outline" 
              on:click={(event) => handleExampleClick(event, example)}
              disabled={isLoading}
            >
              "Tell me about {example}"
            </button>
          {/each}
        </div>
      </div>
      
      {#if showResponse}
        <div class="rag-response">
          <article>
            <header>
              <h3>Assistant Response</h3>
            </header>
            
            <div class="response-content">
              {#if isLoading}
                <p aria-busy="true">Processing your query...</p>
              {:else if error}
                <p class="error">{error}</p>
              {:else if response}
                <div class="response-text">
                  <p><strong>Assistant:</strong> {response.response}</p>
                </div>
                
                {#if response.source_contexts && response.source_contexts.length > 0}
                  <div class="response-sources">
                    <footer>
                      <details>
                        <summary><strong>Sources ({response.source_contexts.length})</strong></summary>
                        <div class="sources-grid">
                          {#each response.source_contexts as source}
                            <article class="source-item">
                              <header>
                                <h5>{source.business_name}</h5>
                                <p><small>{source.neighborhood} • Est. {source.established}</small></p>
                              </header>
                              <p><small>{source.context.substring(0, 200)}...</small></p>
                            </article>
                          {/each}
                        </div>
                      </details>
                    </footer>
                  </div>
                {/if}
              {/if}
            </div>
          </article>
        </div>
      {/if}
    </div>
  </article>
</section>

<style>
  .rag-section {
    margin: var(--pico-spacing) 0;
  }

  .rag-section header {
    text-align: center;
    margin-bottom: 2rem;
  }

  .query-examples {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    justify-content: center;
    margin-top: 1rem;
  }

  .query-example {
    font-size: 0.9rem;
    font-style: italic;
  }

  .query-input-section {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-bottom: 1.5rem;
  }

  .rag-response {
    margin-top: 1.5rem;
  }

  .response-content {
    position: relative;
  }

  .sources-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1rem;
    margin-top: 1rem;
  }

  .source-item {
    margin-bottom: 0;
  }

  .source-item header {
    margin-bottom: 0.5rem;
  }

  .source-item h5 {
    margin-bottom: 0.25rem;
  }

  .error {
    color: var(--pico-del-color);
    font-weight: 500;
  }

  /* Responsive Design */
  @media (min-width: 768px) {
    .query-input-section {
      flex-direction: row;
      align-items: flex-start;
    }
    
    .query-input-section textarea {
      flex: 1;
      min-height: 60px;
      resize: vertical;
    }
  }

  @media (max-width: 480px) {
    .query-examples {
      flex-direction: column;
      gap: 0.5rem;
      margin-top: 1rem;
    }

    .query-example {
      font-size: 0.8rem;
      padding: 0.4rem 0.6rem;
      border-radius: 0.25rem;
    }

    .query-input-section textarea {
      padding: 0.5rem;
      font-size: 0.9rem;
      min-height: 50px;
    }

    .query-input-section button {
      padding: 0.5rem 0.75rem;
      font-size: 0.9rem;
    }

    .response-text p {
      font-size: 0.85rem;
      line-height: 1.5;
    }

    .sources-grid {
      grid-template-columns: 1fr;
      gap: 0.75rem;
    }

    .source-item {
      padding: 0.5rem;
      border-radius: 0.25rem;
    }

    .source-item h5 {
      font-size: 0.9rem;
      line-height: 1.3;
    }

    .source-item p {
      font-size: 0.75rem;
      line-height: 1.4;
    }
  }
</style>