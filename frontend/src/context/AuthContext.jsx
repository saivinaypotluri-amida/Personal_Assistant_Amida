import { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'
import api from '../api/axios'

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
      fetchUser()
    } else {
      setLoading(false)
    }
  }, [token])

  const fetchUser = async () => {
    try {
      const response = await api.get('/auth/me')
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
    
    // Store token - axios interceptor will handle adding it to requests
    localStorage.setItem('token', access_token)
    setToken(access_token)
    setUser(userData)
    
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
    
    // Store token - axios interceptor will handle adding it to requests
    localStorage.setItem('token', access_token)
    setToken(access_token)
    setUser(userData)
    
    return userData
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
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
