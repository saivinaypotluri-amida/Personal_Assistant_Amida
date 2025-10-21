import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import api from '../api/axios'
import {
  Users,
  Activity,
  DollarSign,
  LogOut,
  Home,
  Trash2,
  ToggleLeft,
  ToggleRight,
  UserPlus
} from 'lucide-react'

export default function AdminDashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [activeTab, setActiveTab] = useState('users')
  const [users, setUsers] = useState([])
  const [logs, setLogs] = useState([])
  const [costs, setCosts] = useState([])
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (activeTab === 'users') fetchUsers()
    else if (activeTab === 'logs') fetchLogs()
    else if (activeTab === 'costs') fetchCosts()
    else if (activeTab === 'stats') fetchStats()
  }, [activeTab])

  const fetchUsers = async () => {
    setLoading(true)
    try {
      const response = await api.get('/admin/users')
      setUsers(response.data)
    } catch (err) {
      setError('Failed to fetch users')
    } finally {
      setLoading(false)
    }
  }

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const response = await api.get('/admin/logs?limit=50')
      setLogs(response.data)
    } catch (err) {
      setError('Failed to fetch logs')
    } finally {
      setLoading(false)
    }
  }

  const fetchCosts = async () => {
    setLoading(true)
    try {
      const response = await api.get('/admin/costs?days=30')
      setCosts(response.data)
    } catch (err) {
      setError('Failed to fetch costs')
    } finally {
      setLoading(false)
    }
  }

  const fetchStats = async () => {
    setLoading(true)
    try {
      const response = await api.get('/admin/stats/overall?days=30')
      setStats(response.data)
    } catch (err) {
      setError('Failed to fetch stats')
    } finally {
      setLoading(false)
    }
  }

  const toggleUserActive = async (userId) => {
    try {
      await api.patch(`/admin/users/${userId}/toggle-active`)
      fetchUsers()
    } catch (err) {
      setError('Failed to toggle user status')
    }
  }

  const deleteUser = async (userId) => {
    if (!confirm('Are you sure you want to delete this user?')) return
    
    try {
      await api.delete(`/admin/users/${userId}`)
      fetchUsers()
    } catch (err) {
      setError('Failed to delete user')
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
            🛡️ Admin Dashboard
          </h1>
          <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
            <span style={{ color: 'var(--gray-600)' }}>
              {user?.username}
            </span>
            <button
              className="btn btn-secondary"
              onClick={() => navigate('/dashboard')}
            >
              <Home size={16} />
              Dashboard
            </button>
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

        {/* Tabs */}
        <div style={{
          display: 'flex',
          gap: '0.5rem',
          marginBottom: '2rem',
          borderBottom: '1px solid var(--gray-200)',
          paddingBottom: '1rem'
        }}>
          <button
            className={`btn ${activeTab === 'users' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('users')}
          >
            <Users size={16} />
            Users
          </button>
          <button
            className={`btn ${activeTab === 'logs' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('logs')}
          >
            <Activity size={16} />
            Activity Logs
          </button>
          <button
            className={`btn ${activeTab === 'costs' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('costs')}
          >
            <DollarSign size={16} />
            Cost Tracking
          </button>
          <button
            className={`btn ${activeTab === 'stats' ? 'btn-primary' : 'btn-secondary'}`}
            onClick={() => setActiveTab('stats')}
          >
            <Activity size={16} />
            Statistics
          </button>
        </div>

        {/* Users Tab */}
        {activeTab === 'users' && (
          <div className="card">
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
              User Management
            </h2>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: 'var(--gray-100)', borderBottom: '2px solid var(--gray-200)' }}>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>ID</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Username</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Email</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Role</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Status</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Created</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {users.map((u) => (
                    <tr key={u.id} style={{ borderBottom: '1px solid var(--gray-200)' }}>
                      <td style={{ padding: '0.75rem' }}>{u.id}</td>
                      <td style={{ padding: '0.75rem' }}>{u.username}</td>
                      <td style={{ padding: '0.75rem' }}>{u.email}</td>
                      <td style={{ padding: '0.75rem' }}>
                        <span style={{
                          padding: '0.25rem 0.5rem',
                          borderRadius: '0.25rem',
                          background: u.is_admin ? 'var(--secondary)' : 'var(--gray-200)',
                          color: u.is_admin ? 'white' : 'var(--gray-700)',
                          fontSize: '0.875rem'
                        }}>
                          {u.is_admin ? 'Admin' : 'User'}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem' }}>
                        <span style={{
                          padding: '0.25rem 0.5rem',
                          borderRadius: '0.25rem',
                          background: u.is_active ? 'var(--success)' : 'var(--danger)',
                          color: 'white',
                          fontSize: '0.875rem'
                        }}>
                          {u.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem' }}>
                        {new Date(u.created_at).toLocaleDateString()}
                      </td>
                      <td style={{ padding: '0.75rem' }}>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                          <button
                            className="btn btn-secondary"
                            onClick={() => toggleUserActive(u.id)}
                            style={{ padding: '0.25rem 0.5rem', fontSize: '0.875rem' }}
                          >
                            {u.is_active ? <ToggleRight size={16} /> : <ToggleLeft size={16} />}
                          </button>
                          <button
                            className="btn btn-danger"
                            onClick={() => deleteUser(u.id)}
                            style={{ padding: '0.25rem 0.5rem', fontSize: '0.875rem' }}
                            disabled={u.id === user.id}
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Activity Logs Tab */}
        {activeTab === 'logs' && (
          <div className="card">
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
              Recent Activity
            </h2>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: 'var(--gray-100)', borderBottom: '2px solid var(--gray-200)' }}>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>User ID</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Action</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Source</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Status</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {logs.map((log) => (
                    <tr key={log.id} style={{ borderBottom: '1px solid var(--gray-200)' }}>
                      <td style={{ padding: '0.75rem' }}>{log.user_id}</td>
                      <td style={{ padding: '0.75rem' }}>{log.action}</td>
                      <td style={{ padding: '0.75rem' }}>
                        <span style={{
                          padding: '0.25rem 0.5rem',
                          borderRadius: '0.25rem',
                          background: log.source === 'slack' ? '#4A154B' : 'var(--primary)',
                          color: 'white',
                          fontSize: '0.875rem'
                        }}>
                          {log.source}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem' }}>
                        <span style={{
                          padding: '0.25rem 0.5rem',
                          borderRadius: '0.25rem',
                          background: log.status === 'success' ? 'var(--success)' : 'var(--danger)',
                          color: 'white',
                          fontSize: '0.875rem'
                        }}>
                          {log.status}
                        </span>
                      </td>
                      <td style={{ padding: '0.75rem' }}>
                        {new Date(log.timestamp).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Cost Tracking Tab */}
        {activeTab === 'costs' && (
          <div className="card">
            <h2 style={{ fontSize: '1.25rem', fontWeight: '600', marginBottom: '1rem' }}>
              Cost Tracking (Last 30 Days)
            </h2>
            <div style={{ marginBottom: '1.5rem' }}>
              <div style={{
                padding: '1rem',
                background: 'var(--gray-100)',
                borderRadius: '0.5rem',
                display: 'inline-block'
              }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)', marginBottom: '0.25rem' }}>
                  Total Cost
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>
                  ${costs.reduce((sum, c) => sum + c.estimated_cost, 0).toFixed(4)}
                </div>
              </div>
            </div>
            <div style={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ background: 'var(--gray-100)', borderBottom: '2px solid var(--gray-200)' }}>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>User ID</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Service</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Operation</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Tokens</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Cost</th>
                    <th style={{ padding: '0.75rem', textAlign: 'left' }}>Timestamp</th>
                  </tr>
                </thead>
                <tbody>
                  {costs.map((cost) => (
                    <tr key={cost.id} style={{ borderBottom: '1px solid var(--gray-200)' }}>
                      <td style={{ padding: '0.75rem' }}>{cost.user_id}</td>
                      <td style={{ padding: '0.75rem' }}>{cost.service}</td>
                      <td style={{ padding: '0.75rem' }}>{cost.operation}</td>
                      <td style={{ padding: '0.75rem' }}>{cost.tokens_used.toLocaleString()}</td>
                      <td style={{ padding: '0.75rem' }}>${cost.estimated_cost.toFixed(4)}</td>
                      <td style={{ padding: '0.75rem' }}>
                        {new Date(cost.timestamp).toLocaleString()}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Statistics Tab */}
        {activeTab === 'stats' && stats && (
          <div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
              <div className="card">
                <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)', marginBottom: '0.5rem' }}>
                  Total Users
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--primary)' }}>
                  {stats.total_users}
                </div>
              </div>
              <div className="card">
                <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)', marginBottom: '0.5rem' }}>
                  Active Users
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--success)' }}>
                  {stats.active_users}
                </div>
              </div>
              <div className="card">
                <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)', marginBottom: '0.5rem' }}>
                  Total Operations (30d)
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--secondary)' }}>
                  {stats.total_operations}
                </div>
              </div>
              <div className="card">
                <div style={{ fontSize: '0.875rem', color: 'var(--gray-600)', marginBottom: '0.5rem' }}>
                  Total Cost (30d)
                </div>
                <div style={{ fontSize: '2rem', fontWeight: 'bold', color: 'var(--warning)' }}>
                  ${stats.total_cost.toFixed(4)}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
