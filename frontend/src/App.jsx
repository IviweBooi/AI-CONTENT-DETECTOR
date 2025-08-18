import {
  createBrowserRouter,
  RouterProvider,
} from 'react-router-dom'
import './App.css'
import LandingPage from './pages/landingPage'
import ContactPage from './pages/contactPage'
import LearnPage from './pages/learnPage'
import ContentDetectPage from './pages/contentDetectPage'
import Layout from './layout'
import ErrorPage from './pages/errorPage'


  const routes = [{
    path: '/',
    element: <Layout />,
    errorElement: <ErrorPage />,
    children: [
    { path: '/', element: <LandingPage /> },
    { path: '/contact', element: <ContactPage /> },
    { path: '/learn', element: <LearnPage /> },
    { path: '/content-detect', element: <ContentDetectPage /> }]
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
