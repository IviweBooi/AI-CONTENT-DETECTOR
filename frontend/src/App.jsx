import {
  createBrowserRouter,
  RouterProvider,
} from 'react-router-dom'
import './App.css'
import LandingPage from './pages/landingPage'
import ContactPage from './pages/contactPage'
import LearnPage from './pages/learnPage'
import ContentDetectPage from './pages/contentDetectPage'


function App() {
  const routes = [
    { path: '/', element: <LandingPage /> },
    { path: '/contact', element: <ContactPage /> },
    { path: '/learn', element: <LearnPage /> },
    { path: '/content-detect', element: <ContentDetectPage /> },
  ]

  const router = createBrowserRouter(routes);

  return (
    <RouterProvider router={router} />
  );
}


export default App
