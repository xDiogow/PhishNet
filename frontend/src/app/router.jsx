import { createBrowserRouter } from "react-router-dom"

import PublicLayout from "../layouts/PublicLayout"
import ProtectedLayout from "../layouts/ProtectedLayout"
import RequireAuth from "../auth/RequireAuth"

import LandingPage from "../pages/public/LandingPage"
import Login from "../pages/public/Login"
import Register from "../pages/public/Register"
import CaughtPage from "../pages/public/CaughtPage"
import Dashboard from "../pages/protected/Dashboard"
import Campaigns from "../pages/protected/Campaigns"
import CreateCampaign from "../pages/protected/CreateCampaign"
import ViewCampaign from "../pages/protected/ViewCampaign"
import Team from "../pages/protected/Team"
import Templates from "../pages/protected/Templates"
import Instances from "../pages/protected/Instances"
import Tenants from "../pages/protected/Tenants"
import AuditLogs from "../pages/protected/AuditLogs"

export const router = createBrowserRouter([
  {
    element: <PublicLayout />,
    children: [
      { path: "/", element: <LandingPage /> },
      { path: "/login", element: <Login /> },
      { path: "/register", element: <Register /> },
      { path: "/caught", element: <CaughtPage /> },
    ],
  },
  {
    element: <RequireAuth />,
    children: [
      {
        element: <ProtectedLayout />,
        children: [
          { path: "/dashboard", element: <Dashboard /> },
          { path: "/campaigns", element: <Campaigns /> },
          { path: "/campaigns/create", element: <CreateCampaign /> },
          { path: "/campaigns/:id", element: <ViewCampaign /> },
          { path: "/team", element: <Team /> },
          { path: "/templates", element: <Templates /> },
          { path: "/instances", element: <Instances /> },
          { path: "/tenants", element: <Tenants /> },
          { path: "/audit-logs", element: <AuditLogs /> },
        ],
      },
    ],
  },
])
