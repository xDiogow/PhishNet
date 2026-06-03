import { Menu, MenuButton, MenuItem, MenuItems } from '@headlessui/react'
import { ChevronDown } from 'lucide-react'

export default function Select({
  options = [],
  value,
  onChange,
  placeholder = 'Select an option',
  label,
  id,
  className = ''
}) {
  const selectedOption = options.find(opt => opt.value === value)
  const displayText = selectedOption ? selectedOption.label : placeholder
  const labelId = id ? `${id}-label` : undefined

  return (
    <Menu as="div" className={`relative inline-block w-full ${className}`}>
      {label && (
        <label id={labelId} className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <MenuButton
        aria-haspopup="listbox"
        aria-labelledby={labelId}
        className="inline-flex w-full justify-between gap-x-1.5 rounded-md bg-white border border-gray-300 px-3 py-2 text-sm font-semibold text-gray-900 hover:bg-gray-50"
      >
        <span className={selectedOption ? 'text-gray-900' : 'text-gray-500'}>
          {displayText}
        </span>
        <ChevronDown aria-hidden="true" className="size-5 text-gray-400" />
      </MenuButton>

      <MenuItems
        transition
        role="listbox"
        className="absolute right-0 z-10 mt-2 w-full origin-top-right rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 transition data-closed:scale-95 data-closed:transform data-closed:opacity-0 data-enter:duration-100 data-enter:ease-out data-leave:duration-75 data-leave:ease-in"
      >
        <div className="py-1">
          {options.map((option) => (
            <MenuItem key={option.value}>
              {({ focus }) => (
                <button
                  type="button"
                  role="option"
                  aria-selected={value === option.value}
                  onClick={() => onChange?.(option.value)}
                  className={`block w-full px-4 py-2 text-left text-sm text-gray-700 ${
                    focus ? 'bg-gray-100 text-gray-900' : ''
                  } ${value === option.value ? 'bg-blue-50 text-blue-900 font-medium' : ''}`}
                >
                  {option.label}
                </button>
              )}
            </MenuItem>
          ))}
        </div>
      </MenuItems>
    </Menu>
  )
}
