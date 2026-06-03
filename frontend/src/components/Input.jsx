export default function Input({
  id,
  name,
  type = 'text',
  required = false,
  autoComplete,
  placeholder,
  value,
  onChange,
  error,
  className = '',
  ...props
}) {
  const errorId = error && id ? `${id}-error` : undefined

  return (
    <div className="mt-2">
      <input
        id={id}
        name={name}
        type={type}
        required={required}
        aria-required={required || undefined}
        aria-invalid={error ? 'true' : undefined}
        aria-describedby={errorId}
        autoComplete={autoComplete}
        placeholder={placeholder}
        value={value}
        onChange={onChange}
        className={`block w-full rounded-md border bg-white px-3 py-1.5 text-base text-gray-900 placeholder:text-gray-500 focus:outline-none focus:ring-2 sm:text-sm/6 ${
          error
            ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
            : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500'
        } ${className}`}
        {...props}
      />
      {error && (
        <p id={errorId} className="mt-1 text-sm text-red-600">
          {error}
        </p>
      )}
    </div>
  )
}
