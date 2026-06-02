import { Dialog, DialogBackdrop, DialogPanel, DialogTitle } from '@headlessui/react'
import { AlertTriangle } from 'lucide-react'

export default function ConfirmDialog({
  open,
  onClose,
  onConfirm,
  title = 'Confirm action',
  message = 'Are you sure you want to proceed?',
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  confirmButtonStyle = 'bg-red-500 hover:bg-red-400',
  icon = AlertTriangle,
  iconBgColor = 'bg-red-500/10',
  iconColor = 'text-red-400'
}) {
  const Icon = icon
  return (
    <Dialog open={open} onClose={onClose} className="relative z-50">
      <DialogBackdrop
        transition
        className="fixed inset-0 bg-gray-900/50 transition-opacity data-closed:opacity-0 data-enter:duration-300 data-enter:ease-out data-leave:duration-200 data-leave:ease-in"
      />

      <div className="fixed inset-0 z-10 w-screen overflow-y-auto">
        <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <DialogPanel
            transition
            className="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl outline -outline-offset-1 outline-gray-300 transition-all data-closed:translate-y-4 data-closed:opacity-0 data-enter:duration-300 data-enter:ease-out data-leave:duration-200 data-leave:ease-in sm:my-8 sm:w-full sm:max-w-lg data-closed:sm:translate-y-0 data-closed:sm:scale-95"
          >
            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div className="sm:flex sm:items-start">
                <div className={`mx-auto flex size-12 shrink-0 items-center justify-center rounded-full ${iconBgColor} sm:mx-0 sm:size-10`}>
                  <Icon className={`size-6 ${iconColor}`} aria-hidden="true" />
                </div>
                <div className="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left">
                  <DialogTitle className="text-base font-semibold text-gray-900">
                    {title}
                  </DialogTitle>
                  <div className="mt-2">
                    <p className="text-sm text-gray-500">{message}</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="bg-gray-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
              <button
                type="button"
                onClick={onConfirm}
                className={`inline-flex w-full justify-center rounded-md px-3 py-2 text-sm font-semibold text-white sm:ml-3 sm:w-auto ${confirmButtonStyle}`}
              >
                {confirmText}
              </button>
              <button
                type="button"
                onClick={onClose}
                className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:mt-0 sm:w-auto"
              >
                {cancelText}
              </button>
            </div>
          </DialogPanel>
        </div>
      </div>
    </Dialog>
  )
}
