import { Outlet } from "react-router-dom";
import Navbar from '../components/Navbar'

export default function ProtectedLayout() {
    return (
        <div className="min-h-screen bg-gray-100">
            <Navbar />
            <main className="p-4 sm:p-6">
                <Outlet />
            </main>
        </div>
    )
}