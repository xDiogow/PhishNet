import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import Input from '../../components/Input'
import Button from '../../components/Button'
import { register } from '../../services/authService'
import { useUser } from '../../contexts/UserContext'

export default function Register() {
  const navigate = useNavigate()
  const { setUser } = useUser()
  const [formData, setFormData] = useState({
    invitation_code: '',
    first_name: '',
    last_name: '',
    email: '',
    password: '',
    confirmPassword: ''
  })
  const [error, setError] = useState(null)
  
  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleSubmit = async(e) => {
    e.preventDefault()
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match')
      return
    }
    setError(null)
    
    try {
      const data = await register({
        invitation_code: formData.invitation_code,
        first_name: formData.first_name,
        last_name: formData.last_name,
        email: formData.email,
        password: formData.password
      })
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
          Create your account
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
              <label htmlFor="invitation_code" className="block text-sm/6 font-medium text-gray-700">
                Invitation code
              </label>
              <Input
                id="invitation_code"
                name="invitation_code"
                type="text"
                required
                placeholder="Enter your invitation code"
                value={formData.invitation_code}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="first_name" className="block text-sm/6 font-medium text-gray-700">
                First Name
              </label>
              <Input
                id="first_name"
                name="first_name"
                type="text"
                required
                autoComplete="given-name"
                value={formData.first_name}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="last_name" className="block text-sm/6 font-medium text-gray-700">
                Last Name
              </label>
              <Input
                id="last_name"
                name="last_name"
                type="text"
                required
                autoComplete="family-name"
                value={formData.last_name}
                onChange={handleChange}
              />
            </div>

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
              <label htmlFor="password" className="block text-sm/6 font-medium text-gray-700">
                Password
              </label>
              <Input
                id="password"
                name="password"
                type="password"
                required
                autoComplete="new-password"
                value={formData.password}
                onChange={handleChange}
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm/6 font-medium text-gray-700">
                Confirm password
              </label>
              <Input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                required
                autoComplete="new-password"
                value={formData.confirmPassword}
                onChange={handleChange}
              />
            </div>

            <div>
              <Button type="submit">
                Sign up
              </Button>
            </div>
          </form>

          <p className="mt-10 text-center text-sm/6 text-gray-600">
            Already a member?{' '}
            <Link to="/login" className="font-semibold text-blue-600 hover:text-blue-500">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  )
}
