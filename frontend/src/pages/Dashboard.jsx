import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'
import {
  Mail,
  Calendar,
  LogOut,
  Settings,
  Check,
  X,
  Shield,
  MessageSquare,
  Loader
} from 'lucide-react'

export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [authStatus, setAuthStatus] = useState({ google: false, slack: false, azure_openai: false })
  const [emailSummary, setEmailSummary] = useState(null)
  const [meetingResult, setMeetingResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  // Email Summary Form
  const [emailDays, setEmailDays] = useState('1')
  
  // Meeting Form
  const [attendees, setAttendees] = useState('')
  const [duration, setDuration] = useState('30')
  const [meetingTitle, setMeetingTitle] = useState('Meeting')

  useEffect(() => {
    fetchAuthStatus()
  }, [])

  const fetchAuthStatus = async () => {
    try {
      const response = await api.get('/auth/status')
      // Handle new nested status format
      const status = response.data
      setAuthStatus({
        google: status.google?.connected || false,
        slack: status.slack?.connected || false,
        azure_openai: status.azure_openai?.configured || false
      })
    } catch (err) {
      console.error('Failed to fetch auth status:', err)
    }
  }

  const handleGoogleAuth = async () => {
    try {
      const response = await api.get('/auth/google/url')
      window.location.href = response.data.url
    } catch (err) {
      setError('Failed to initiate Google authentication')
    }
  }

  const handleSlackAuth = async () => {
    try {
      const response = await api.get('/auth/slack/url')
      window.location.href = response.data.url
    } catch (err) {
      setError('Failed to initiate Slack authentication')
    }
  }

  const handleEmailSummary = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setEmailSummary(null)

    try {
      const response = await api.post('/assistant/email-summary', {
        days: parseInt(emailDays),
        source: 'portal'
      })
      setEmailSummary(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to summarize emails')
    } finally {
      setLoading(false)
    }
  }

  const handleScheduleMeeting = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    setMeetingResult(null)

    try {
      const response = await api.post('/assistant/schedule-meeting', {
        attendees: attendees.split(',').map(e => e.trim()),
        duration_minutes: parseInt(duration),
        title: meetingTitle,
        next_available: true,
        source: 'portal'
      })
      setMeetingResult(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to schedule meeting')
    } finally {
      setLoading(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  return (
    <div style={{ minHeight: '100vh', background: 'var(--gray-50)' }}>
      {/* Header */}
      <div style={{
        background: 'white',
        borderBottom: '1px solid var(--gray-200)',
        padding: '1rem 0'
      }}>
        <div className="container" style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center'
        }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'var(--gray-900)' }}>
            🤖 Amida AI Assistant
          </h1>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <span style={{ color: 'var(--gray-600)' }}>
              {user?.username}
            </span>
            {user?.is_admin && (
              <button
                className="btn btn-secondary"
                onClick={() => navigate('/admin')}
              >
                <Shield size={16} />
                Admin
              </button>
            )}
            <button className="btn btn-secondary" onClick={handleLogout}>
              <LogOut size={16} />
              Logout
            </button>
          </div>
        </div>
      </div>

      <div className="container" style={{ padding: '2rem 1rem' }}>
        {error && (
          <div className="alert alert-error">{error}</div>
        )}

        {/* Service Status */}
        <div className="card" style={{ marginBottom: '2rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', margin: 0 }}>
              <Settings size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
              Connected Services
            </h2>
            <button 
              className="btn btn-secondary"
              onClick={() => navigate('/configure-oauth')}
              style={{ fontSize: '0.875rem' }}
            >
              <Settings size={16} />
              Configure Credentials
            </button>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem' }}>
            <div style={{
              padding: '1rem',
              border: '1px solid var(--gray-200)',
              borderRadius: '0.5rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span style={{ fontWeight: '500' }}>Google Workspace</span>
              {authStatus.google ? (
                <Check size={20} color="var(--success)" />
              ) : (
                <button className="btn btn-primary" onClick={handleGoogleAuth} style={{ fontSize: '0.875rem' }}>
                  Connect
                </button>
              )}
            </div>
            <div style={{
              padding: '1rem',
              border: '1px solid var(--gray-200)',
              borderRadius: '0.5rem',
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center'
            }}>
              <span style={{ fontWeight: '500' }}>Slack</span>
              {authStatus.slack ? (
                <Check size={20} color="var(--success)" />
              ) : (
                <button className="btn btn-primary" onClick={handleSlackAuth} style={{ fontSize: '0.875rem' }}>
                  Connect
                </button>
              )}
            </div>
          </div>
          <div className="alert alert-info" style={{ marginTop: '1rem' }}>
            <strong>💡 Tip:</strong> Click "Configure Credentials" to set up your own OAuth credentials for Google, Slack, and Azure OpenAI.
          </div>
        </div>

        {/* Main Features */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', gap: '2rem' }}>
          {/* Email Summary */}
          <div className="card">
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
              <Mail size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
              Email Summary
            </h2>
            <form onSubmit={handleEmailSummary}>
              <div className="form-group">
                <label className="label">Number of days</label>
                <input
                  type="number"
                  className="input"
                  value={emailDays}
                  onChange={(e) => setEmailDays(e.target.value)}
                  min="1"
                  max="30"
                />
              </div>
              <button
                type="submit"
                className="btn btn-primary"
                style={{ width: '100%', justifyContent: 'center' }}
                disabled={loading || !authStatus.google}
              >
                {loading ? <Loader size={16} className="spin" /> : <Mail size={16} />}
                Get Email Summary
              </button>
            </form>

            {emailSummary && (
              <div style={{ marginTop: '1.5rem' }}>
                <div className="alert alert-success">
                  ✅ Found {emailSummary.total_emails} emails. Digest sent to your email!
                </div>
                <div style={{ maxHeight: '400px', overflowY: 'auto' }}>
                  {emailSummary.summaries.map((email, idx) => (
                    <div key={idx} style={{
                      padding: '1rem',
                      border: '1px solid var(--gray-200)',
                      borderRadius: '0.5rem',
                      marginBottom: '1rem'
                    }}>
                      <div style={{ fontWeight: '600', marginBottom: '0.5rem' }}>{email.subject}</div>
                      <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)', marginBottom: '0.5rem' }}>
                        From: {email.from_email}
                      </div>
                      <div style={{ marginBottom: '0.5rem' }}>{email.summary}</div>
                      {email.meeting_links.length > 0 && (
                        <div style={{ fontSize: '0.875rem' }}>
                          📅 Meeting links: {email.meeting_links.map((link, i) => (
                            <a key={i} href={link} target="_blank" rel="noopener noreferrer" style={{ color: 'var(--primary)', display: 'block' }}>
                              {link}
                            </a>
                          ))}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Schedule Meeting */}
          <div className="card">
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
              <Calendar size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
              Schedule Meeting
            </h2>
            <form onSubmit={handleScheduleMeeting}>
              <div className="form-group">
                <label className="label">Attendees (comma-separated emails)</label>
                <input
                  type="text"
                  className="input"
                  value={attendees}
                  onChange={(e) => setAttendees(e.target.value)}
                  placeholder="john@example.com, jane@example.com"
                  required
                />
              </div>
              <div className="form-group">
                <label className="label">Duration (minutes)</label>
                <input
                  type="number"
                  className="input"
                  value={duration}
                  onChange={(e) => setDuration(e.target.value)}
                  min="15"
                  step="15"
                />
              </div>
              <div className="form-group">
                <label className="label">Meeting Title</label>
                <input
                  type="text"
                  className="input"
                  value={meetingTitle}
                  onChange={(e) => setMeetingTitle(e.target.value)}
                />
              </div>
              <button
                type="submit"
                className="btn btn-primary"
                style={{ width: '100%', justifyContent: 'center' }}
                disabled={loading || !authStatus.google}
              >
                {loading ? <Loader size={16} className="spin" /> : <Calendar size={16} />}
                Schedule Meeting
              </button>
            </form>

            {meetingResult && (
              <div style={{ marginTop: '1.5rem' }}>
                {meetingResult.success ? (
                  <div className="alert alert-success">
                    ✅ {meetingResult.message}
                    {meetingResult.meeting_link && (
                      <a
                        href={meetingResult.meeting_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{ display: 'block', marginTop: '0.5rem', color: 'var(--primary)' }}
                      >
                        Join Meeting
                      </a>
                    )}
                  </div>
                ) : (
                  <div className="alert alert-error">
                    ❌ {meetingResult.message}
                    {meetingResult.conflicts && (
                      <div style={{ marginTop: '0.5rem' }}>
                        Conflicts with: {meetingResult.conflicts.join(', ')}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        </div>

        {/* Slack Integration Info */}
        <div className="card" style={{ marginTop: '2rem' }}>
          <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
            <MessageSquare size={20} style={{ display: 'inline', marginRight: '0.5rem' }} />
            Slack Commands
          </h2>
          <p style={{ marginBottom: '1rem', color: 'var(--gray-600)' }}>
            Once you've connected your Slack workspace, you can use these commands:
          </p>
          <div style={{ background: 'var(--gray-100)', padding: '1rem', borderRadius: '0.5rem', fontFamily: 'monospace' }}>
            <div style={{ marginBottom: '0.5rem' }}><strong>/emailsummary</strong> - Get your daily email digest</div>
            <div style={{ marginBottom: '0.5rem' }}><strong>/emailsummary 7 days</strong> - Get summary for last 7 days</div>
            <div><strong>/schedule email1,email2 30 Meeting Title</strong> - Schedule a meeting</div>
          </div>
        </div>
      </div>
    </div>
  )
}
