import {
  createBrowserRouter,
  RouterProvider,
} from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import LandingPage from './pages/landingPage'
import HelpPage from './pages/helpPage'
import LearnPage from './pages/learnPage'
import ContentDetectPage from './pages/contentDetectPage'
import SignInPage from './pages/signInPage'
import SignUpPage from './pages/signUpPage'
import ProfilePage from './pages/profilePage'
import TermsOfService from './pages/legal/terms'
import PrivacyPolicy from './pages/legal/privacy'

import Layout from './layout'
import ErrorPage from './pages/errorPage'


  const routes = [{
    path: '/',
    element: <Layout />,
    errorElement: <ErrorPage />,
    children: [
    { path: '/', element: <LandingPage /> },
    { path: '/help', element: <HelpPage /> },
    { path: '/learn', element: <LearnPage /> },
    { path: '/content-detect', element: <ContentDetectPage /> },
    { path: '/sign-in', element: <SignInPage /> },
    { path: '/sign-up', element: <SignUpPage /> },
    { path: '/profile', element: <ProfilePage /> },
    { path: '/terms', element: <TermsOfService /> },
    { path: '/privacy-policy', element: <PrivacyPolicy /> }]
  }]


  const router = createBrowserRouter(routes);


function App() {
  return (
    <AuthProvider>
      <RouterProvider router={router} />
    </AuthProvider>
  );
}

export default App
