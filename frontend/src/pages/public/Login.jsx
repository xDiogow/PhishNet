import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import Input from '../../components/Input'
import Button from '../../components/Button'
import { login } from '../../services/authService'
import { useUser } from '../../contexts/UserContext'

export default function Login() {
  const navigate = useNavigate()
  const { setUser } = useUser()
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })
  const [error, setError] = useState(null)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)

    try {
      const data = await login(formData)
      if (data.user) {
        setUser(data.user)
      }
      navigate('/dashboard')
    }
    catch (error) {
      setError(error.message)
    }
  }

  return (
    <div className="flex min-h-screen flex-col justify-center px-6 py-24 lg:px-8 bg-gray-100">
      <div className="sm:mx-auto sm:w-full sm:max-w-sm">
        <h1 className="text-center text-2xl/9 font-bold tracking-tight text-gray-900">
          Sign in to your account
        </h1>
      </div>

      <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
        <div className="bg-white rounded-lg shadow p-8">
          {error && (
            <div role="alert" className="mb-4 rounded-md bg-red-50 border border-red-200 p-4">
              <p className="text-sm text-red-800">{error}</p>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm/6 font-medium text-gray-700">
                Email address
              </label>
              <Input
                id="email"
                name="email"
                type="email"
                required
                autoComplete="email"
                value={formData.email}
                onChange={handleChange}
              />
            </div>

            <div>
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="block text-sm/6 font-medium text-gray-700">
                  Password
                </label>
                <div className="text-sm">
                  <a href="#" className="font-semibold text-blue-600 hover:text-blue-500">
                    Forgot password?
                  </a>
                </div>
              </div>
              <Input
                id="password"
                name="password"
                type="password"
                required
                autoComplete="current-password"
                value={formData.password}
                onChange={handleChange}
              />
            </div>

            <div>
              <Button type="submit">
                Sign in
              </Button>
            </div>
          </form>

          <p className="mt-10 text-center text-sm/6 text-gray-600">
            Not a member?{' '}
            <Link to="/register" className="font-semibold text-blue-600 hover:text-blue-500">
              Start a 14 day free trial
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
