import {
  createBrowserRouter,
  RouterProvider,
} from 'react-router-dom'
import './App.css'
import LandingPage from './pages/landingPage'
import HelpPage from './pages/helpPage'
import LearnPage from './pages/learnPage'
import ContentDetectPage from './pages/contentDetectPage'
import SignInPage from './pages/signInPage'
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
    { path: '/sign-in', element: <SignInPage /> }]
  }]


  const router = createBrowserRouter(routes);


function App() {
  return (
    <>
    <RouterProvider router={router} />
    </>
  );
}

export default App
