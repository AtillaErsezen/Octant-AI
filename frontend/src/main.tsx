import { StrictMode, useState, useEffect } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'
import Demo from './Demo.tsx'

const Router = () => {
  const [route, setRoute] = useState(window.location.hash.toLowerCase());

  useEffect(() => {
    const handleHashChange = () => {
      console.log("Hash Changed:", window.location.hash);
      setRoute(window.location.hash.toLowerCase());
    }
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  if (route.includes('demo')) {
    console.log("Rendering Demo...");
    return <Demo />;
  }
  
  return <App />;
};

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Router />
  </StrictMode>,
)
