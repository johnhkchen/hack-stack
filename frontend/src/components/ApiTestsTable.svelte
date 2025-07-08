<script>
  import { onMount } from 'svelte';
  
  let endpointsData = null;
  let testResults = {};
  let isRunning = {};
  let expandedSections = {};
  let isLoadingEndpoints = false;
  let loadEndpointsError = null;
  let isAutoTesting = false;

  // Load endpoints configuration and auto-discovery data
  async function loadEndpointsData() {
    console.log('Loading endpoints data...');
    isLoadingEndpoints = true;
    loadEndpointsError = null;
    
    try {
      const response = await fetch('/api/debug/endpoints');
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log('Received data:', data);
      
      endpointsData = data;
      
      // Initialize expanded sections based on config
      expandedSections = {};
      for (const [sectionKey, sectionInfo] of Object.entries(data.organization.sections)) {
        expandedSections[sectionKey] = sectionInfo.expanded || false;
      }
      
      console.log('Loaded endpoints data successfully:', data.summary);
    } catch (error) {
      console.error('Failed to load endpoints:', error);
      loadEndpointsError = error.message;
    } finally {
      isLoadingEndpoints = false;
    }
  }

  // Toggle section expansion
  function toggleSection(sectionKey) {
    expandedSections[sectionKey] = !expandedSections[sectionKey];
    expandedSections = { ...expandedSections };
  }

  // Test a specific endpoint
  async function testEndpoint(endpoint) {
    const endpointKey = `${endpoint.path}:${endpoint.methods[0]}`;
    
    if (isRunning[endpointKey]) return;

    console.log(`Testing endpoint: ${endpointKey}`);
    isRunning[endpointKey] = true;
    isRunning = { ...isRunning };

    const startTime = Date.now();
    const testUrl = endpoint.path;

    try {
      // Prepare fetch options based on endpoint configuration
      const method = endpoint.methods[0]; // Use the configured method
      const fetchOptions = {
        method: method
      };
      
      // Add request body for POST requests if configured
      if (method === 'POST' && endpoint.request_body) {
        fetchOptions.headers = {
          'Content-Type': 'application/json'
        };
        fetchOptions.body = JSON.stringify(endpoint.request_body);
      }
      
      const response = await fetch(testUrl, fetchOptions);
      const duration = Date.now() - startTime;
      const data = response.ok ? await response.json() : await response.text();

      testResults[endpointKey] = {
        status: response.ok ? 'success' : 'error',
        statusCode: response.status,
        duration,
        timestamp: new Date().toLocaleTimeString(),
        data: response.ok ? formatResponseData(endpoint, data) : data
      };
      
      console.log(`Endpoint ${endpointKey} - Status: ${response.status}, OK: ${response.ok}, Result: ${testResults[endpointKey].status}`);
    } catch (error) {
      const duration = Date.now() - startTime;
      testResults[endpointKey] = {
        status: 'error',
        statusCode: 0,
        duration,
        timestamp: new Date().toLocaleTimeString(),
        error: error.message
      };
      
      console.log(`Endpoint ${endpointKey} error:`, error.message);
    } finally {
      isRunning[endpointKey] = false;
      isRunning = { ...isRunning };
      testResults = { ...testResults };
      console.log('Updated testResults:', testResults);
    }
  }

  // Test all endpoints in a section
  async function testSection(sectionKey) {
    if (!endpointsData || !endpointsData.organization.sections[sectionKey]) return;
    
    const section = endpointsData.organization.sections[sectionKey];
    const tests = section.endpoints.map(endpoint => testEndpoint(endpoint));
    await Promise.allSettled(tests);
  }

  // Test all endpoints
  async function testAllEndpoints() {
    if (!endpointsData) return;
    
    const allTests = [];
    for (const section of Object.values(endpointsData.organization.sections)) {
      for (const endpoint of section.endpoints) {
        allTests.push(testEndpoint(endpoint));
      }
    }
    await Promise.allSettled(allTests);
  }

  // Format response data
  function formatResponseData(endpoint, data) {
    try {
      // Keep it simple for now - just return stringified data
      return JSON.stringify(data, null, 2);
    } catch (error) {
      return String(data);
    }
  }

  // Get status icon
  function getStatusIcon(result) {
    if (!result) return '◯';
    switch (result.status) {
      case 'success': return '✓';
      case 'error': return '✗';
      default: return '◯';
    }
  }

  // Get status class
  function getStatusClass(result) {
    if (!result) return '';
    return result.status === 'success' ? 'success' : 'error';
  }

  // Get section status summary
  function getSectionStatus(section) {
    const endpoints = section.endpoints || [];
    const tested = endpoints.filter(ep => {
      const endpointKey = `${ep.path}:${ep.methods[0]}`;
      return testResults[endpointKey];
    });
    const successful = tested.filter(ep => {
      const endpointKey = `${ep.path}:${ep.methods[0]}`;
      return testResults[endpointKey]?.status === 'success';
    });
    
    const result = {
      total: endpoints.length,
      tested: tested.length,
      successful: successful.length,
      success_rate: tested.length > 0 ? Math.round((successful.length / tested.length) * 100) : 0,
      overall_progress: endpoints.length > 0 ? Math.round((successful.length / endpoints.length) * 100) : 0
    };
    
    // Debug: log status updates when there are test results
    if (tested.length > 0) {
      console.log(`\n🔍 Section ${section.name}: ${result.successful}/${result.total} working (${result.success_rate}%)`);
      console.log('Test results keys:', Object.keys(testResults));
      console.log('Endpoint keys in section:', endpoints.map(ep => `${ep.path}:${ep.methods[0]}`));
      
      // Show detailed breakdown
      endpoints.forEach(ep => {
        const endpointKey = `${ep.path}:${ep.methods[0]}`;
        const testResult = testResults[endpointKey];
        if (testResult) {
          console.log(`  ${endpointKey}: ${testResult.status} (${testResult.statusCode})`);
          console.log(`    Status check: testResult.status === 'success' ? ${testResult.status === 'success'}`);
        }
      });
      
      // Debug the filtering logic
      console.log('Tested endpoints:', tested.map(ep => {
        const endpointKey = `${ep.path}:${ep.methods[0]}`;
        return { key: endpointKey, result: testResults[endpointKey] };
      }));
      
      console.log('Successful endpoints:', successful.map(ep => {
        const endpointKey = `${ep.path}:${ep.methods[0]}`;
        return { key: endpointKey, result: testResults[endpointKey] };
      }));
    }
    
    return result;
  }

  // Get priority class
  function getPriorityClass(priority) {
    switch (priority) {
      case 'high': return 'priority-high';
      case 'medium': return 'priority-medium';
      case 'low': return 'priority-low';
      default: return 'priority-medium';
    }
  }

  // Reactive statement to force re-evaluation of section status
  $: if (testResults) {
    // This will trigger re-evaluation of section status when testResults changes
    Object.keys(testResults).length;
  }

  // Auto-test endpoints after loading
  async function autoTestEndpoints() {
    if (!endpointsData) return;
    
    isAutoTesting = true;
    console.log('Auto-testing all endpoints...');
    
    // Test all endpoints automatically
    const allTests = [];
    for (const section of Object.values(endpointsData.organization.sections)) {
      for (const endpoint of section.endpoints) {
        allTests.push(testEndpoint(endpoint));
      }
    }
    
    if (allTests.length > 0) {
      await Promise.allSettled(allTests);
      console.log('Auto-testing completed');
    }
    
    isAutoTesting = false;
  }

  // Load data and auto-test on mount
  onMount(async () => {
    await loadEndpointsData();
    // Auto-test endpoints after loading
    if (endpointsData) {
      await autoTestEndpoints();
    }
  });
</script>

<article>
  <header>
    <h2>API Endpoints</h2>
    <div class="header-actions">
      <button on:click={loadEndpointsData} disabled={isLoadingEndpoints || isAutoTesting} class="secondary">
        {isLoadingEndpoints ? 'Loading...' : 'Refresh'}
      </button>
      <button on:click={testAllEndpoints} disabled={!endpointsData || Object.values(isRunning).some(Boolean) || isAutoTesting}>
        {isAutoTesting ? 'Auto-testing...' : 'Test All'}
      </button>
    </div>
  </header>

  {#if isLoadingEndpoints}
    <div class="loading-state">
      <p aria-busy="true">Loading API endpoints...</p>
    </div>
  {:else if isAutoTesting}
    <div class="loading-state">
      <p aria-busy="true">Auto-testing API endpoints...</p>
      <small>Testing {endpointsData ? Object.values(endpointsData.organization.sections).reduce((total, section) => total + section.endpoints.length, 0) : 0} endpoints automatically</small>
    </div>
  {:else if loadEndpointsError}
    <div class="error-state">
      <p>❌ Failed to load endpoints: {loadEndpointsError}</p>
      <button on:click={loadEndpointsData}>Retry</button>
    </div>
  {:else if endpointsData}
    <!-- Summary Stats -->
    <div class="summary-stats">
      <div class="stat">
        <div class="stat-label">Total Sections</div>
        <div class="stat-value">{endpointsData.summary.total_sections}</div>
      </div>
      <div class="stat">
        <div class="stat-label">Total Endpoints</div>
        <div class="stat-value">{endpointsData.summary.endpoints_configured + endpointsData.summary.endpoints_untracked}</div>
      </div>
      <div class="stat">
        <div class="stat-label">Configured</div>
        <div class="stat-value">{endpointsData.summary.endpoints_configured}</div>
      </div>
      <div class="stat">
        <div class="stat-label">Untracked</div>
        <div class="stat-value">{endpointsData.summary.endpoints_untracked}</div>
      </div>
    </div>

    <!-- Sections -->
    <div class="sections-container">
      {#each Object.entries(endpointsData.organization.sections) as [sectionKey, section]}
        {@const sectionStatus = getSectionStatus(section)}
        {@const isExpanded = expandedSections[sectionKey]}
        {@const isPrimary = section.is_primary}
        
        <div class="section-card" class:primary={isPrimary} class:expanded={isExpanded}>
          <div class="section-header" on:click={() => toggleSection(sectionKey)}>
            <div class="section-title">
              <span class="section-icon">{isExpanded ? '▼' : '▶'}</span>
              <span class="section-name">{section.name}</span>
              {#if section.auto_populated}
                <span class="auto-badge">Auto</span>
              {/if}
            </div>
            
            <div class="section-status">
              <span class="status-summary">
                {sectionStatus.successful}/{sectionStatus.total} working
              </span>
              <button 
                on:click|stopPropagation={() => testSection(sectionKey)}
                disabled={Object.values(isRunning).some(Boolean) || isAutoTesting}
                class="test-section-btn"
              >
                Test Section
              </button>
            </div>
          </div>
          
          {#if section.description}
            <div class="section-description">{section.description}</div>
          {/if}
          
          {#if isExpanded}
            <div class="section-content">
              <div class="endpoints-grid">
                {#each section.endpoints as endpoint}
                  {@const endpointKey = `${endpoint.path}:${endpoint.methods[0]}`}
                  {@const result = testResults[endpointKey]}
                  {@const isTestingThis = isRunning[endpointKey]}
                  
                  <div class="endpoint-card {getPriorityClass(endpoint.priority)}">
                    <div class="endpoint-header">
                      <div class="endpoint-info">
                        <div class="endpoint-path">
                          <code>{endpoint.display_path || endpoint.path}</code>
                          <span class="method-badge">{endpoint.methods[0]}</span>
                        </div>
                        {#if endpoint.name}
                          <div class="endpoint-name">{endpoint.name}</div>
                        {/if}
                        {#if endpoint.description}
                          <div class="endpoint-description">{endpoint.description}</div>
                        {:else if endpoint.docstring}
                          <div class="endpoint-description">{endpoint.docstring}</div>
                        {/if}
                      </div>
                      
                      <div class="endpoint-meta">
                        {#if endpoint.priority}
                          <span class="priority-badge {getPriorityClass(endpoint.priority)}">
                            {endpoint.priority}
                          </span>
                        {/if}
                        {#if endpoint.configured}
                          <span class="config-badge">Configured</span>
                        {:else}
                          <span class="auto-badge">Auto-discovered</span>
                        {/if}
                      </div>
                    </div>
                    
                    <div class="endpoint-status">
                      <div class="status-info">
                        {#if isTestingThis}
                          <span class="status testing" aria-busy="true">Testing...</span>
                        {:else if result}
                          <span class="status {getStatusClass(result)}">
                            {getStatusIcon(result)} {result.statusCode}
                          </span>
                          <span class="duration">{result.duration}ms</span>
                        {:else}
                          <span class="status">◯ Not tested</span>
                        {/if}
                      </div>
                      
                      <button 
                        on:click={() => testEndpoint(endpoint)}
                        disabled={isTestingThis || isAutoTesting}
                        class="test-endpoint-btn"
                      >
                        Test
                      </button>
                    </div>
                    
                    {#if result && (result.data || result.error)}
                      <div class="endpoint-result">
                        <details>
                          <summary>
                            {result.status === 'success' ? '✓ Response' : '✗ Error'}
                            <span class="response-size">
                              {result.data ? `${Math.ceil(result.data.length / 100)}KB` : 'Error'}
                            </span>
                          </summary>
                          <pre><code>{result.data || result.error}</code></pre>
                        </details>
                      </div>
                    {/if}
                  </div>
                {/each}
              </div>
            </div>
          {/if}
        </div>
      {/each}
    </div>
  {:else}
    <div class="loading-state">
      <p aria-busy="true">Initializing API endpoint discovery...</p>
      <button on:click={loadEndpointsData}>Load Endpoints</button>
    </div>
  {/if}
</article>

<style>
  /* Header */
  header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
    gap: 1rem;
  }

  header h2 {
    margin: 0;
    font-size: 1.75rem;
  }

  .header-actions {
    display: flex;
    gap: 0.5rem;
  }

  /* Summary Stats */
  .summary-stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 1rem;
    margin-bottom: 1.5rem;
    padding: 1rem;
    background: var(--pico-background-color);
    border: 1px solid var(--pico-border-color);
    border-radius: var(--pico-border-radius);
  }

  .stat {
    text-align: center;
  }

  .stat-label {
    font-size: 0.875rem;
    color: var(--pico-muted-color);
    margin-bottom: 0.25rem;
  }

  .stat-value {
    font-size: 1.5rem;
    font-weight: 600;
    color: var(--pico-color);
  }

  /* Sections */
  .sections-container {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .section-card {
    background: var(--pico-background-color);
    border: 1px solid var(--pico-border-color);
    border-radius: var(--pico-border-radius);
    overflow: hidden;
    transition: all 0.2s ease;
  }

  .section-card.primary {
    border-color: var(--pico-primary);
    box-shadow: 0 0 0 1px var(--pico-primary);
  }

  .section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem;
    cursor: pointer;
    background: var(--pico-background-color);
    border-bottom: 1px solid var(--pico-border-color);
    transition: background-color 0.2s ease;
  }

  .section-header:hover {
    background: var(--pico-muted-background-color);
  }

  .section-title {
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }

  .section-icon {
    font-size: 0.75rem;
    color: var(--pico-muted-color);
    transition: transform 0.2s ease;
  }

  .section-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--pico-color);
  }

  .primary-badge {
    background: var(--pico-primary);
    color: var(--pico-primary-inverse);
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .auto-badge {
    background: #10b981;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .section-status {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .status-summary {
    font-size: 0.875rem;
    color: var(--pico-muted-color);
    font-family: var(--pico-font-family-monospace);
  }

  .success-rate {
    font-weight: 600;
    color: var(--pico-color);
  }

  .overall-progress {
    font-weight: 500;
    color: var(--pico-muted-color);
  }

  .test-section-btn {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    background: var(--pico-primary);
    color: var(--pico-primary-inverse);
    border: none;
    border-radius: var(--pico-border-radius);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .test-section-btn:hover:not(:disabled) {
    background: var(--pico-primary-hover);
    transform: translateY(-1px);
  }

  .test-section-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .section-description {
    padding: 0 1rem 1rem;
    color: var(--pico-muted-color);
    font-size: 0.875rem;
  }

  .section-content {
    padding: 1rem;
    background: var(--pico-card-background-color);
  }

  /* Endpoints Grid */
  .endpoints-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
    gap: 1rem;
  }

  .endpoint-card {
    background: var(--pico-background-color);
    border: 1px solid var(--pico-border-color);
    border-radius: var(--pico-border-radius);
    padding: 1rem;
    transition: all 0.2s ease;
  }

  .endpoint-card:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }

  .endpoint-card.priority-high {
    border-left: 4px solid #dc2626;
  }

  .endpoint-card.priority-medium {
    border-left: 4px solid #f59e0b;
  }

  .endpoint-card.priority-low {
    border-left: 4px solid #6b7280;
  }

  .endpoint-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 1rem;
    margin-bottom: 1rem;
  }

  .endpoint-info {
    flex: 1;
    min-width: 0;
  }

  .endpoint-path {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }

  .endpoint-path code {
    font-size: 0.875rem;
    color: var(--pico-color);
    background: var(--pico-muted-background-color);
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    flex: 1;
    min-width: 0;
    word-break: break-all;
  }

  .method-badge {
    background: #3b82f6;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 500;
    white-space: nowrap;
  }

  .endpoint-name {
    font-weight: 500;
    color: var(--pico-color);
    margin-bottom: 0.25rem;
  }

  .endpoint-description {
    font-size: 0.875rem;
    color: var(--pico-muted-color);
    margin-bottom: 0.25rem;
  }

  .endpoint-docstring {
    font-size: 0.8rem;
    color: var(--pico-muted-color);
    font-style: italic;
  }

  .endpoint-meta {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
    align-items: flex-end;
  }

  .priority-badge {
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
  }

  .priority-badge.priority-high {
    background: #dc2626;
    color: white;
  }

  .priority-badge.priority-medium {
    background: #f59e0b;
    color: white;
  }

  .priority-badge.priority-low {
    background: #6b7280;
    color: white;
  }

  .config-badge {
    background: #10b981;
    color: white;
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    font-size: 0.75rem;
    font-weight: 500;
  }

  .endpoint-status {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 1rem;
  }

  .status-info {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .status.success {
    color: var(--pico-ins-color);
  }

  .status.error {
    color: var(--pico-del-color);
  }

  .status.testing {
    color: var(--pico-primary);
  }

  .duration {
    font-family: var(--pico-font-family-monospace);
    font-size: 0.875rem;
    color: var(--pico-muted-color);
  }

  .test-endpoint-btn {
    padding: 0.5rem 1rem;
    font-size: 0.875rem;
    background: var(--pico-primary);
    color: var(--pico-primary-inverse);
    border: none;
    border-radius: var(--pico-border-radius);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .test-endpoint-btn:hover:not(:disabled) {
    background: var(--pico-primary-hover);
  }

  .test-endpoint-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  .endpoint-result {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--pico-border-color);
  }

  .endpoint-result details {
    margin: 0;
  }

  .endpoint-result summary {
    cursor: pointer;
    font-weight: 500;
    color: var(--pico-muted-color);
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .response-size {
    font-size: 0.75rem;
    color: var(--pico-muted-color);
    background: var(--pico-muted-background-color);
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    border: 1px solid var(--pico-border-color);
  }

  .endpoint-result pre {
    background: var(--pico-muted-background-color);
    border: 1px solid var(--pico-border-color);
    border-radius: var(--pico-border-radius);
    padding: 1rem;
    font-size: 0.75rem;
    overflow-x: auto;
    margin: 0;
    max-height: 200px;
    overflow-y: auto;
  }

  /* States */
  .loading-state,
  .error-state,
  .empty-state {
    text-align: center;
    padding: 2rem;
  }

  .loading-state p {
    margin: 0;
  }

  .error-state p {
    color: var(--pico-del-color);
    margin-bottom: 1rem;
  }

  /* Responsive */
  @media (max-width: 768px) {
    .endpoints-grid {
      grid-template-columns: 1fr;
    }
    
    .endpoint-header {
      flex-direction: column;
      align-items: flex-start;
    }
    
    .endpoint-meta {
      flex-direction: row;
      align-items: center;
    }
    
    .summary-stats {
      grid-template-columns: repeat(2, 1fr);
    }
    
    .section-status {
      flex-direction: column;
      align-items: flex-end;
      gap: 0.5rem;
    }
  }
</style>