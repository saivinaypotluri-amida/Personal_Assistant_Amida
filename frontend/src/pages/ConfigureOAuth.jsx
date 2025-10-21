import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Settings, Save, ArrowLeft, Eye, EyeOff } from 'lucide-react'
import api from '../api/axios'

export default function ConfigureOAuth() {
  const navigate = useNavigate()
  const [activeService, setActiveService] = useState('google')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState('')
  const [error, setError] = useState('')
  
  // Show/hide secrets
  const [showSecrets, setShowSecrets] = useState({
    google: false,
    slack: false,
    azure: false
  })

  // Google credentials
  const [googleConfig, setGoogleConfig] = useState({
    client_id: '',
    client_secret: '',
    redirect_uri: 'http://localhost:8000/api/auth/google/callback'
  })

  // Slack credentials
  const [slackConfig, setSlackConfig] = useState({
    client_id: '',
    client_secret: '',
    redirect_uri: 'http://localhost:8000/api/auth/slack/callback',
    bot_token: '',
    signing_secret: ''
  })

  // Azure OpenAI credentials
  const [azureConfig, setAzureConfig] = useState({
    endpoint: '',
    api_key: '',
    deployment: '',
    api_version: '2024-02-15-preview'
  })

  const handleSaveGoogle = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      await api.post('/auth/config/save', {
        service: 'google',
        client_id: googleConfig.client_id,
        client_secret: googleConfig.client_secret,
        additional_config: {
          redirect_uri: googleConfig.redirect_uri
        }
      })
      setSuccess('Google OAuth configuration saved successfully!')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save Google configuration')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveSlack = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      await api.post('/auth/config/save', {
        service: 'slack',
        client_id: slackConfig.client_id,
        client_secret: slackConfig.client_secret,
        additional_config: {
          redirect_uri: slackConfig.redirect_uri,
          bot_token: slackConfig.bot_token,
          signing_secret: slackConfig.signing_secret
        }
      })
      setSuccess('Slack OAuth configuration saved successfully!')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save Slack configuration')
    } finally {
      setLoading(false)
    }
  }

  const handleSaveAzure = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setSuccess('')

    try {
      await api.post('/auth/azure/configure', {
        service: 'azure_openai',
        client_id: azureConfig.endpoint,
        client_secret: azureConfig.api_key,
        additional_config: {
          endpoint: azureConfig.endpoint,
          deployment: azureConfig.deployment,
          api_version: azureConfig.api_version
        }
      })
      setSuccess('Azure OpenAI configuration saved successfully!')
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save Azure configuration')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--gray-50)', padding: '2rem' }}>
      <div className="container" style={{ maxWidth: '900px' }}>
        <button 
          className="btn btn-secondary"
          onClick={() => navigate('/dashboard')}
          style={{ marginBottom: '1rem' }}
        >
          <ArrowLeft size={16} />
          Back to Dashboard
        </button>

        <div className="card">
          <h1 style={{ fontSize: '1.75rem', fontWeight: 'bold', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Settings size={24} />
            Configure OAuth Credentials
          </h1>
          <p style={{ color: 'var(--gray-600)', marginBottom: '2rem' }}>
            Set up your own OAuth credentials for Google Workspace, Slack, and Azure OpenAI.
          </p>

          {success && (
            <div className="alert alert-success">{success}</div>
          )}

          {error && (
            <div className="alert alert-error">{error}</div>
          )}

          {/* Tabs */}
          <div style={{ display: 'flex', gap: '0.5rem', borderBottom: '2px solid var(--gray-200)', marginBottom: '2rem' }}>
            <button
              className={`btn ${activeService === 'google' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveService('google')}
              style={{ borderRadius: '0.5rem 0.5rem 0 0' }}
            >
              Google Workspace
            </button>
            <button
              className={`btn ${activeService === 'slack' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveService('slack')}
              style={{ borderRadius: '0.5rem 0.5rem 0 0' }}
            >
              Slack
            </button>
            <button
              className={`btn ${activeService === 'azure' ? 'btn-primary' : 'btn-secondary'}`}
              onClick={() => setActiveService('azure')}
              style={{ borderRadius: '0.5rem 0.5rem 0 0' }}
            >
              Azure OpenAI
            </button>
          </div>

          {/* Google Configuration */}
          {activeService === 'google' && (
            <form onSubmit={handleSaveGoogle}>
              <div className="alert alert-info" style={{ marginBottom: '1.5rem' }}>
                <strong>How to get Google OAuth credentials:</strong><br/>
                1. Go to <a href="https://console.cloud.google.com" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)' }}>Google Cloud Console</a><br/>
                2. Create a project and enable Gmail & Calendar APIs<br/>
                3. Create OAuth 2.0 credentials<br/>
                4. Copy Client ID and Client Secret here
              </div>

              <div className="form-group">
                <label className="label">Client ID</label>
                <input
                  type="text"
                  className="input"
                  value={googleConfig.client_id}
                  onChange={(e) => setGoogleConfig({...googleConfig, client_id: e.target.value})}
                  placeholder="123456789-abc...apps.googleusercontent.com"
                  required
                />
              </div>

              <div className="form-group">
                <label className="label">Client Secret</label>
                <div style={{ position: 'relative' }}>
                  <input
                    type={showSecrets.google ? "text" : "password"}
                    className="input"
                    value={googleConfig.client_secret}
                    onChange={(e) => setGoogleConfig({...googleConfig, client_secret: e.target.value})}
                    placeholder="GOCSPX-abc..."
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowSecrets({...showSecrets, google: !showSecrets.google})}
                    style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer' }}
                  >
                    {showSecrets.google ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label className="label">Redirect URI</label>
                <input
                  type="text"
                  className="input"
                  value={googleConfig.redirect_uri}
                  onChange={(e) => setGoogleConfig({...googleConfig, redirect_uri: e.target.value})}
                  required
                />
                <small style={{ color: 'var(--gray-600)', fontSize: '0.875rem' }}>
                  Add this to your Google OAuth app's authorized redirect URIs
                </small>
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                style={{ width: '100%', justifyContent: 'center' }}
                disabled={loading}
              >
                <Save size={16} />
                {loading ? 'Saving...' : 'Save Google Configuration'}
              </button>
            </form>
          )}

          {/* Slack Configuration */}
          {activeService === 'slack' && (
            <form onSubmit={handleSaveSlack}>
              <div className="alert alert-info" style={{ marginBottom: '1.5rem' }}>
                <strong>How to get Slack OAuth credentials:</strong><br/>
                1. Go to <a href="https://api.slack.com/apps" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)' }}>Slack API Dashboard</a><br/>
                2. Create a Slack App<br/>
                3. Get Client ID, Client Secret, Signing Secret, and Bot Token<br/>
                4. Copy them here
              </div>

              <div className="form-group">
                <label className="label">Client ID</label>
                <input
                  type="text"
                  className="input"
                  value={slackConfig.client_id}
                  onChange={(e) => setSlackConfig({...slackConfig, client_id: e.target.value})}
                  placeholder="1234567890.1234567890"
                  required
                />
              </div>

              <div className="form-group">
                <label className="label">Client Secret</label>
                <div style={{ position: 'relative' }}>
                  <input
                    type={showSecrets.slack ? "text" : "password"}
                    className="input"
                    value={slackConfig.client_secret}
                    onChange={(e) => setSlackConfig({...slackConfig, client_secret: e.target.value})}
                    placeholder="abc123..."
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowSecrets({...showSecrets, slack: !showSecrets.slack})}
                    style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer' }}
                  >
                    {showSecrets.slack ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label className="label">Signing Secret</label>
                <input
                  type={showSecrets.slack ? "text" : "password"}
                  className="input"
                  value={slackConfig.signing_secret}
                  onChange={(e) => setSlackConfig({...slackConfig, signing_secret: e.target.value})}
                  placeholder="abc123..."
                  required
                />
              </div>

              <div className="form-group">
                <label className="label">Bot Token</label>
                <input
                  type={showSecrets.slack ? "text" : "password"}
                  className="input"
                  value={slackConfig.bot_token}
                  onChange={(e) => setSlackConfig({...slackConfig, bot_token: e.target.value})}
                  placeholder="xoxb-..."
                />
                <small style={{ color: 'var(--gray-600)', fontSize: '0.875rem' }}>
                  Only needed for Slack bot features
                </small>
              </div>

              <div className="form-group">
                <label className="label">Redirect URI</label>
                <input
                  type="text"
                  className="input"
                  value={slackConfig.redirect_uri}
                  onChange={(e) => setSlackConfig({...slackConfig, redirect_uri: e.target.value})}
                  required
                />
                <small style={{ color: 'var(--gray-600)', fontSize: '0.875rem' }}>
                  Add this to your Slack app's redirect URLs
                </small>
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                style={{ width: '100%', justifyContent: 'center' }}
                disabled={loading}
              >
                <Save size={16} />
                {loading ? 'Saving...' : 'Save Slack Configuration'}
              </button>
            </form>
          )}

          {/* Azure OpenAI Configuration */}
          {activeService === 'azure' && (
            <form onSubmit={handleSaveAzure}>
              <div className="alert alert-info" style={{ marginBottom: '1.5rem' }}>
                <strong>How to get Azure OpenAI credentials:</strong><br/>
                1. Go to <a href="https://portal.azure.com" target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)' }}>Azure Portal</a><br/>
                2. Create an Azure OpenAI resource<br/>
                3. Deploy a model (e.g., GPT-4)<br/>
                4. Copy endpoint and API key here
              </div>

              <div className="form-group">
                <label className="label">Endpoint</label>
                <input
                  type="text"
                  className="input"
                  value={azureConfig.endpoint}
                  onChange={(e) => setAzureConfig({...azureConfig, endpoint: e.target.value})}
                  placeholder="https://your-resource.openai.azure.com/"
                  required
                />
              </div>

              <div className="form-group">
                <label className="label">API Key</label>
                <div style={{ position: 'relative' }}>
                  <input
                    type={showSecrets.azure ? "text" : "password"}
                    className="input"
                    value={azureConfig.api_key}
                    onChange={(e) => setAzureConfig({...azureConfig, api_key: e.target.value})}
                    placeholder="abc123..."
                    required
                  />
                  <button
                    type="button"
                    onClick={() => setShowSecrets({...showSecrets, azure: !showSecrets.azure})}
                    style={{ position: 'absolute', right: '10px', top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer' }}
                  >
                    {showSecrets.azure ? <EyeOff size={20} /> : <Eye size={20} />}
                  </button>
                </div>
              </div>

              <div className="form-group">
                <label className="label">Deployment Name</label>
                <input
                  type="text"
                  className="input"
                  value={azureConfig.deployment}
                  onChange={(e) => setAzureConfig({...azureConfig, deployment: e.target.value})}
                  placeholder="gpt-4"
                  required
                />
              </div>

              <div className="form-group">
                <label className="label">API Version</label>
                <input
                  type="text"
                  className="input"
                  value={azureConfig.api_version}
                  onChange={(e) => setAzureConfig({...azureConfig, api_version: e.target.value})}
                  required
                />
              </div>

              <button
                type="submit"
                className="btn btn-primary"
                style={{ width: '100%', justifyContent: 'center' }}
                disabled={loading}
              >
                <Save size={16} />
                {loading ? 'Saving...' : 'Save Azure Configuration'}
              </button>
            </form>
          )}
        </div>
      </div>
    </div>
  )
}
