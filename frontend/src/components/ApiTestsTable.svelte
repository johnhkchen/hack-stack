<script>
  let testResults = {};
  let isRunning = {};

  // Real API endpoints from the actual backend
  const apiEndpoints = [
    {
      id: 'health',
      name: 'Health Check',
      endpoint: '/api/health',
      description: 'System health and configuration status',
      type: 'system'
    },
    {
      id: 'businesses',
      name: 'Businesses List',
      endpoint: '/api/businesses?limit=5',
      description: 'Get list of businesses with real data model',
      type: 'data'
    },
    {
      id: 'business_detail',
      name: 'Business Detail',
      endpoint: '/api/businesses/1',
      description: 'Get single business by ID',
      type: 'data'
    },
    {
      id: 'search',
      name: 'Business Search',
      endpoint: '/api/search?q=cafe&limit=3',
      description: 'Search businesses with query',
      type: 'data'
    },
    {
      id: 'metrics',
      name: 'System Metrics',
      endpoint: '/api/metrics',
      description: 'Application metrics and statistics',
      type: 'system'
    },
    {
      id: 'debug',
      name: 'Debug Status',
      endpoint: '/api/debug',
      description: 'Comprehensive system debug information',
      type: 'system'
    },
    {
      id: 'vendor_openai',
      name: 'OpenAI Vendor Test',
      endpoint: '/api/debug/test/openai',
      description: 'Test OpenAI vendor integration',
      type: 'vendor'
    },
    {
      id: 'vendor_anthropic',
      name: 'Anthropic Vendor Test',
      endpoint: '/api/debug/test/anthropic',
      description: 'Test Anthropic vendor integration',
      type: 'vendor'
    },
    {
      id: 'vendor_weaviate',
      name: 'Weaviate Vector DB',
      endpoint: '/api/debug/test/weaviate',
      description: 'Weaviate sponsor integration (TBD implementation)',
      type: 'sponsor'
    },
    {
      id: 'llamaindex_status',
      name: 'LlamaIndex Status',
      endpoint: '/api/llamaindex/status',
      description: 'LlamaIndex multi-modal service capabilities',
      type: 'sponsor'
    },
    {
      id: 'llamaindex_demo',
      name: 'LlamaIndex Demo',
      endpoint: '/api/llamaindex/demo',
      description: 'Multi-modal processing demo capabilities',
      type: 'sponsor'
    },
    {
      id: 'llamaindex_documents',
      name: 'LlamaIndex Documents',
      endpoint: '/api/llamaindex/documents',
      description: 'List processed multi-modal documents',
      type: 'sponsor'
    }
  ];

  async function testEndpoint(api) {
    if (isRunning[api.id]) return;

    isRunning[api.id] = true;
    isRunning = { ...isRunning };

    const startTime = Date.now();

    try {
      const response = await fetch(api.endpoint);
      const duration = Date.now() - startTime;
      const data = response.ok ? await response.json() : await response.text();

      testResults[api.id] = {
        status: response.ok ? 'success' : 'error',
        statusCode: response.status,
        duration,
        timestamp: new Date().toLocaleTimeString(),
        data: response.ok ? formatResponseData(api, data) : data
      };
    } catch (error) {
      const duration = Date.now() - startTime;
      testResults[api.id] = {
        status: 'error',
        statusCode: 0,
        duration,
        timestamp: new Date().toLocaleTimeString(),
        error: error.message
      };
    } finally {
      isRunning[api.id] = false;
      isRunning = { ...isRunning };
      testResults = { ...testResults };
    }
  }

  async function testAllEndpoints() {
    const tests = apiEndpoints.map(api => testEndpoint(api));
    await Promise.allSettled(tests);
  }

  function getStatusIcon(result) {
    if (!result) return '◯';
    switch (result.status) {
      case 'success': return '✓';
      case 'error': return '✗';
      default: return '◯';
    }
  }

  function getStatusClass(result) {
    if (!result) return '';
    return result.status === 'success' ? 'success' : 'error';
  }

  function formatResponseData(api, data) {
    // Format response data with contextual information for different endpoint types
    let formatted = {};
    
    if (api.type === 'data' && Array.isArray(data)) {
      // Business data endpoints
      formatted.summary = `${data.length} businesses returned`;
      formatted.sample_fields = data[0] ? Object.keys(data[0]) : [];
      formatted.sample_business = data[0] || null;
      formatted.full_data = data;
    } else if (api.id === 'business_detail') {
      // Single business endpoint
      formatted.business_id = data.id;
      formatted.name = data.name;
      formatted.type = data.type;
      formatted.neighborhood = data.neighborhood;
      formatted.full_business = data;
    } else if (api.id === 'health') {
      // Health endpoint
      formatted.status = data.status;
      formatted.mode = data.mode;
      formatted.demo_ready = data.demo_ready;
      formatted.available_vendors = data.available_vendors;
      formatted.startup_time = data.startup_time;
    } else if (api.id === 'metrics') {
      // Metrics endpoint
      formatted.total_businesses = data.total_businesses;
      formatted.active_vendors = data.active_vendors;
      formatted.mode = data.mode;
      formatted.uptime = data.uptime;
    } else if (api.id === 'debug') {
      // Debug endpoint
      formatted.overall_health = data.overall_health;
      formatted.environment_mode = data.environment_mode;
      formatted.demo_ready = data.demo_ready;
      formatted.services_count = Object.keys(data.services || {}).length;
      formatted.vendors_count = Object.keys(data.vendors || {}).length;
      formatted.summary = data.summary;
    } else if (api.type === 'vendor' || api.type === 'sponsor') {
      // Vendor and sponsor test endpoints
      formatted.vendor = data.vendor;
      formatted.status = data.status;
      formatted.result_type = data.result ? Object.keys(data.result)[0] : 'none';
      formatted.has_mock_data = data.result && Object.keys(data.result).length > 0;
      
      if (api.type === 'sponsor') {
        formatted.sponsor_note = "🌟 Sponsor Integration - Implementation in Progress";
        formatted.integration_status = data.status === 'success' ? 'Mock endpoint working' : 'Endpoint not found';
      }
      
      formatted.full_result = data;
    } else {
      // Default formatting
      formatted = data;
    }
    
    return JSON.stringify(formatted, null, 2);
  }
</script>

<article>
  <header>
    <h2>API Endpoints</h2>
    <button on:click={testAllEndpoints} disabled={Object.values(isRunning).some(Boolean)}>
      Test All Endpoints
    </button>
  </header>

  <!-- Desktop Table View -->
  <figure class="desktop-table">
    <table role="table" class="api-table">
      <thead>
        <tr>
          <th>Endpoint</th>
          <th>Type</th>
          <th>Status</th>
          <th>Time</th>
          <th>Test</th>
        </tr>
      </thead>
      <tbody>
        {#each apiEndpoints as api}
          {@const result = testResults[api.id]}
          <tr>
            <td>
              <code>{api.name}</code>
              <small>{api.endpoint}</small>
            </td>
            <td>
              <kbd class="type-{api.type}">{api.type}</kbd>
            </td>
            <td>
              <div class="status-container">
                {#if isRunning[api.id]}
                  <span aria-busy="true">Testing...</span>
                {:else if result}
                  <span class="status {getStatusClass(result)}">
                    {getStatusIcon(result)} {result.statusCode}
                  </span>
                {:else}
                  <span class="status">◯ Not tested</span>
                {/if}
              </div>
            </td>
            <td>
              {#if result}
                <span class="duration">{result.duration}ms</span>
              {:else}
                —
              {/if}
            </td>
            <td>
              <button 
                on:click={() => testEndpoint(api)} 
                disabled={isRunning[api.id]}
                class="secondary"
              >
                Test
              </button>
            </td>
          </tr>
          {#if result && (result.data || result.error)}
            <tr class="result-row">
              <td colspan="5">
                <details>
                  <summary>
                    {result.status === 'success' ? '✓ Response Data' : '✗ Error Details'}
                    <span class="response-size">
                      {result.data ? `${Math.ceil(result.data.length / 100)}KB` : 'Error'}
                    </span>
                  </summary>
                  <pre><code>{result.data || result.error}</code></pre>
                </details>
              </td>
            </tr>
          {/if}
        {/each}
      </tbody>
    </table>
  </figure>

  <!-- Mobile Card View -->
  <div class="mobile-cards">
    {#each apiEndpoints as api}
      {@const result = testResults[api.id]}
      <div class="endpoint-card">
        <div class="card-header">
          <div class="endpoint-info">
            <div class="endpoint-name">{api.name}</div>
            <div class="endpoint-path">{api.endpoint}</div>
          </div>
          <kbd class="type-badge type-{api.type}">{api.type}</kbd>
        </div>
        
        <div class="card-body">
          <div class="status-section">
            <div class="status-label">Status</div>
            <div class="status-value">
              {#if isRunning[api.id]}
                <span aria-busy="true">Testing...</span>
              {:else if result}
                <span class="status {getStatusClass(result)}">
                  {getStatusIcon(result)} {result.statusCode}
                </span>
              {:else}
                <span class="status">◯ Not tested</span>
              {/if}
            </div>
          </div>
          
          {#if result}
            <div class="time-section">
              <div class="time-label">Response Time</div>
              <div class="time-value">{result.duration}ms</div>
            </div>
          {/if}
        </div>
        
        <div class="card-actions">
          <button 
            on:click={() => testEndpoint(api)} 
            disabled={isRunning[api.id]}
            class="test-button"
          >
            Test Endpoint
          </button>
        </div>
        
        {#if result && (result.data || result.error)}
          <div class="card-result">
            <details>
              <summary>
                {result.status === 'success' ? '✓ Response Data' : '✗ Error Details'}
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
</article>

<style>
  /* Mobile-first responsive design */
  
  /* Hide desktop table on mobile */
  .desktop-table {
    display: none;
  }

  /* Mobile card layout */
  .mobile-cards {
    display: flex;
    flex-direction: column;
    gap: 1rem;
  }

  .endpoint-card {
    background: var(--pico-background-color);
    border: 1px solid var(--pico-border-color);
    border-radius: var(--pico-border-radius);
    padding: 1rem;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  }

  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
    gap: 1rem;
  }

  .endpoint-info {
    flex: 1;
    min-width: 0;
  }

  .endpoint-name {
    font-weight: 600;
    font-size: 1.1rem;
    margin-bottom: 0.25rem;
    color: var(--pico-color);
  }

  .endpoint-path {
    font-family: var(--pico-font-family-monospace);
    font-size: 0.875rem;
    color: var(--pico-muted-color);
    word-break: break-all;
    line-height: 1.3;
  }

  .type-badge {
    padding: 0.25rem 0.75rem;
    border-radius: 1rem;
    font-size: 0.75rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.025em;
    flex-shrink: 0;
  }

  .type-system {
    background: #3b82f6;
    color: white;
  }

  .type-data {
    background: #10b981;
    color: white;
  }

  .type-vendor {
    background: #f59e0b;
    color: white;
  }

  .type-sponsor {
    background: #8b5cf6;
    color: white;
    position: relative;
  }


  .card-body {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-bottom: 1rem;
  }

  .status-section, .time-section {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--pico-border-color);
  }

  .status-label, .time-label {
    font-weight: 500;
    color: var(--pico-muted-color);
    font-size: 0.875rem;
  }

  .status-value, .time-value {
    font-weight: 600;
  }

  .time-value {
    font-family: var(--pico-font-family-monospace);
    font-size: 0.875rem;
  }

  .status.success {
    color: var(--pico-ins-color);
  }

  .status.error {
    color: var(--pico-del-color);
  }

  .status-container {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    min-height: 1.5rem;
  }

  .card-actions {
    display: flex;
    justify-content: center;
  }

  .test-button {
    width: 100%;
    min-height: 48px;
    font-size: 1rem;
    font-weight: 500;
    background: var(--pico-primary);
    color: var(--pico-primary-inverse);
    border: none;
    border-radius: var(--pico-border-radius);
    cursor: pointer;
    transition: all 0.2s ease;
  }

  .test-button:hover:not(:disabled) {
    background: var(--pico-primary-hover);
    transform: translateY(-1px);
  }

  .test-button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }

  .card-result {
    margin-top: 1rem;
    padding-top: 1rem;
    border-top: 1px solid var(--pico-border-color);
  }

  .card-result details {
    margin: 0;
  }

  .card-result summary, .result-row summary {
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
    background: var(--pico-background-color);
    padding: 0.25rem 0.5rem;
    border-radius: 0.25rem;
    border: 1px solid var(--pico-border-color);
    white-space: nowrap;
    margin-left: auto;
  }

  .card-result pre {
    background: var(--pico-background-color);
    border: 1px solid var(--pico-border-color);
    border-radius: var(--pico-border-radius);
    padding: 1rem;
    font-size: 0.75rem;
    overflow-x: auto;
    margin: 0;
  }

  /* Header styling */
  header {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  header h2 {
    margin: 0;
    font-size: 1.5rem;
  }

  header button {
    min-height: 48px;
    font-size: 1rem;
    font-weight: 500;
  }

  /* Desktop: Switch to table layout */
  @media (min-width: 769px) {
    .mobile-cards {
      display: none;
    }

    .desktop-table {
      display: block;
    }

    .api-table {
      width: 100%;
      table-layout: fixed;
    }

    .api-table th:nth-child(1) { width: 35%; }
    .api-table th:nth-child(2) { width: 18%; }
    .api-table th:nth-child(3) { width: 18%; }
    .api-table th:nth-child(4) { width: 15%; }
    .api-table th:nth-child(5) { width: 14%; }

    .duration {
      font-family: var(--pico-font-family-monospace);
      font-size: 0.875rem;
    }

    .result-row td {
      padding-top: 0;
    }

    .result-row details {
      margin: 0;
    }

    .result-row pre {
      margin: 0.5rem 0;
      max-height: 200px;
      overflow-y: auto;
    }

    header {
      flex-direction: row;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1rem;
    }

    header h2 {
      margin: 0;
      font-size: 1.75rem;
    }

    td small {
      display: block;
      color: var(--pico-muted-color);
      font-size: 0.75rem;
    }
  }

  /* Large desktop optimizations - table only */
  @media (min-width: 1024px) {
    .endpoint-card {
      height: fit-content;
    }
  }
</style>