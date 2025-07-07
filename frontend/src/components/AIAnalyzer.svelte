<script>
  let analyzing = false;
  let result = null;
  let error = null;
  
  async function analyzeRandomBusiness() {
    analyzing = true;
    error = null;
    result = null;
    
    try {
      const response = await fetch('/api/vendor/openai', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          operation: 'analyze',
          data: {}
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      result = await response.json();
    } catch (err) {
      error = err.message;
    } finally {
      analyzing = false;
    }
  }
  
  async function findSimilarBusinesses() {
    analyzing = true;
    error = null;
    result = null;
    
    try {
      const response = await fetch('/api/vendor/weaviate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          operation: 'similarity_search',
          data: { query: 'innovative local businesses' }
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      result = await response.json();
    } catch (err) {
      error = err.message;
    } finally {
      analyzing = false;
    }
  }
  
  async function extractStructuredData() {
    analyzing = true;
    error = null;
    result = null;
    
    try {
      const response = await fetch('/api/vendor/anthropic', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          operation: 'extract_structure',
          data: {}
        })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      result = await response.json();
    } catch (err) {
      error = err.message;
    } finally {
      analyzing = false;
    }
  }
</script>

<div class="ai-analyzer">
  <div class="button-group">
    <button 
      on:click={analyzeRandomBusiness} 
      disabled={analyzing}
      class="secondary"
    >
      🔍 OpenAI Analysis
    </button>
    
    <button 
      on:click={findSimilarBusinesses} 
      disabled={analyzing}
      class="secondary"
    >
      🔗 Weaviate Search
    </button>
    
    <button 
      on:click={extractStructuredData} 
      disabled={analyzing}
      class="secondary"
    >
      📊 Anthropic Extract
    </button>
  </div>
  
  {#if analyzing}
    <div class="analysis-result" aria-busy="true">
      <p>Analyzing with AI...</p>
    </div>
  {:else if error}
    <div class="analysis-result error">
      <h4>Error</h4>
      <p>{error}</p>
    </div>
  {:else if result}
    <div class="analysis-result">
      <div class="result-header">
        <h4>Analysis Results</h4>
        <div class="meta-info">
          <span class="vendor-badge">{result._meta?.vendor || 'unknown'}</span>
          <span class="mode-badge {result._meta?.mode || 'unknown'}">{result._meta?.mode || 'unknown'}</span>
        </div>
      </div>
      
      <div class="result-content">
        {#if result.analysis}
          <div class="result-section">
            <strong>Analysis:</strong>
            <p>{result.analysis}</p>
          </div>
        {/if}
        
        {#if result.sentiment}
          <div class="result-section">
            <strong>Sentiment:</strong> 
            <span class="sentiment {result.sentiment}">{result.sentiment}</span>
          </div>
        {/if}
        
        {#if result.key_themes}
          <div class="result-section">
            <strong>Key Themes:</strong>
            <div class="theme-tags">
              {#each result.key_themes as theme}
                <span class="theme-tag">{theme}</span>
              {/each}
            </div>
          </div>
        {/if}
        
        {#if result.confidence}
          <div class="result-section">
            <strong>Confidence:</strong> 
            <div class="confidence-bar">
              <div class="confidence-fill" style="width: {result.confidence * 100}%"></div>
              <span class="confidence-text">{(result.confidence * 100).toFixed(1)}%</span>
            </div>
          </div>
        {/if}
        
        {#if result.similar_businesses}
          <div class="result-section">
            <strong>Similar Businesses:</strong>
            <div class="similar-list">
              {#each result.similar_businesses as business}
                <div class="similar-item">
                  <strong>{business.name}</strong> - {business.tagline}
                </div>
              {/each}
            </div>
          </div>
        {/if}
        
        {#if result.structured_data}
          <div class="result-section">
            <strong>Structured Data:</strong>
            <pre class="structured-data">{JSON.stringify(result.structured_data, null, 2)}</pre>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .ai-analyzer {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .button-group {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  @media (min-width: 768px) {
    .button-group {
      flex-direction: row;
    }
  }
  
  .analysis-result {
    border: 1px solid var(--pico-border-color);
    border-radius: 0.5rem;
    padding: 1rem;
    background: var(--pico-card-background-color);
  }
  
  .analysis-result.error {
    border-color: var(--pico-del-color);
    background: var(--pico-del-background-color);
  }
  
  .result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--pico-border-color);
  }
  
  .meta-info {
    display: flex;
    gap: 0.5rem;
  }
  
  .vendor-badge, .mode-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 500;
  }
  
  .vendor-badge {
    background: var(--pico-primary-background);
    color: var(--pico-primary-color);
  }
  
  .mode-badge {
    background: var(--pico-secondary-background);
    color: var(--pico-secondary-color);
  }
  
  .mode-badge.mock {
    background: #fff3cd;
    color: #856404;
  }
  
  .result-content {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }
  
  .result-section {
    padding: 0.5rem 0;
  }
  
  .theme-tags, .similar-list {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    margin-top: 0.5rem;
  }
  
  .theme-tag {
    display: inline-block;
    background: var(--pico-contrast-background);
    color: var(--pico-contrast-color);
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.8rem;
  }
  
  .sentiment {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-weight: 500;
  }
  
  .sentiment.positive {
    background: #d4edda;
    color: #155724;
  }
  
  .confidence-bar {
    position: relative;
    background: var(--pico-border-color);
    border-radius: 0.25rem;
    height: 1.5rem;
    margin-top: 0.5rem;
    overflow: hidden;
  }
  
  .confidence-fill {
    background: linear-gradient(90deg, #28a745, #20c997);
    height: 100%;
    transition: width 0.5s ease;
  }
  
  .confidence-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 0.8rem;
    font-weight: 500;
    color: white;
    text-shadow: 0 1px 2px rgba(0,0,0,0.5);
  }
  
  .similar-item {
    padding: 0.5rem;
    background: var(--pico-background-color);
    border-radius: 0.25rem;
    border: 1px solid var(--pico-border-color);
  }
  
  .structured-data {
    background: var(--pico-code-background-color);
    color: var(--pico-code-color);
    padding: 1rem;
    border-radius: 0.25rem;
    font-size: 0.8rem;
    overflow-x: auto;
  }
</style>