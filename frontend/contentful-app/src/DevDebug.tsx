import { useState } from 'react';

type ActivationResult = {
  activation_id: string;
  entry_id: string;
  status: 'success' | 'error';
  processing_time: number;
  enrichment_data?: Record<string, unknown>;
  marketo_response?: Record<string, unknown>;
  errors?: string[];
};

const DevDebug = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<ActivationResult | null>(null);

  const backendUrl = (import.meta as any).env?.VITE_BACKEND_URL || 'http://localhost:8010';

  const triggerActivate = async () => {
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const res = await fetch(`${backendUrl}/activate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          entry_id: 'dev-debug-entry',
          marketo_list_id: 'ML_DEMO_001',
          enrichment_enabled: true
        })
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(Array.isArray(data?.errors) ? data.errors.join(', ') : 'Activation failed');
      }
      setResult(data as ActivationResult);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Unknown error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ fontFamily: 'sans-serif', maxWidth: 820, margin: '40px auto', padding: 16 }}>
      <h2>Dev Debug: Activation Demo</h2>
      <p>
        This development-only view runs outside Contentful to demo the backend. Backend URL:
        <code style={{ marginLeft: 8 }}>{backendUrl}</code>
      </p>

      <button onClick={triggerActivate} disabled={loading} style={{ padding: '8px 14px' }}>
        {loading ? 'Activating…' : 'Activate (Mock)'}
      </button>

      {error && (
        <pre style={{ color: '#b00020', whiteSpace: 'pre-wrap', marginTop: 16 }}>Error: {error}</pre>
      )}

      {result && (
        <div style={{ marginTop: 16 }}>
          <h3>Result</h3>
          <pre style={{ background: '#111', color: '#eee', padding: 12, borderRadius: 6, overflowX: 'auto' }}>
            {JSON.stringify(result, null, 2)}
          </pre>
        </div>
      )}

      <hr style={{ margin: '24px 0' }} />
      <details>
        <summary>What is this?</summary>
        <p>
          The Contentful App normally runs inside Contentful. When opened directly (Vite dev server), this
          debug view provides a simple button to call the FastAPI backend <code>/activate</code> endpoint and
          show the JSON response.
        </p>
      </details>
    </div>
  );
};

export default DevDebug;




