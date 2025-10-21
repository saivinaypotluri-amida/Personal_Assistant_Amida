import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const AuthContext = createContext()

export function useAuth() {
  return useContext(AuthContext)
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)
  const [token, setToken] = useState(localStorage.getItem('token'))

  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchUser = async () => {
    try {
      const response = await axios.get('/api/auth/me')
      setUser(response.data)
    } catch (error) {
      console.error('Failed to fetch user:', error)
      logout()
    } finally {
      setLoading(false)
    }
  }

  const login = async (username, password) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)

    const response = await axios.post('/api/auth/login', formData)
    const { access_token, user: userData } = response.data
    
    localStorage.setItem('token', access_token)
    setToken(access_token)
    setUser(userData)
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
    
    return userData
  }

  const register = async (email, username, password, isAdmin = false) => {
    const response = await axios.post('/api/auth/register', {
      email,
      username,
      password,
      is_admin: isAdmin
    })
    
    const { access_token, user: userData } = response.data
    
    localStorage.setItem('token', access_token)
    setToken(access_token)
    setUser(userData)
    axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
    
    return userData
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
    delete axios.defaults.headers.common['Authorization']
  }

  const value = {
    user,
    loading,
    login,
    register,
    logout
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
