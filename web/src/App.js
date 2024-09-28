import './styles/App.scss';
import React, {useEffect, useState} from 'react';
import { useNavigate } from 'react-router';
import {BrowserRouter, Route, Routes, useParams, useSearchParams } from 'react-router-dom';
import Header from './components/Header';

import Home from './pages/Home';
import site from './site';
import Create from './pages/Create';
import Project from './pages/Project';

function useStoredState(key, defaultValue) {
  // 👇 Load stored state into regular react component state
  const [state, setState] = useState(() => {
    const storedState = localStorage.getItem(key);
    // console.log(storedState)
    if (storedState) {
      // 🚩 Data is stored as string so need to parse
      return JSON.parse(storedState);
    }

    // No stored state - load default value.
    // It could be a function initializer or plain value.
    return defaultValue;
  });

  // 👇 Keeps the exact same interface as setState - value or setter function.
  const setValue = (value) => {
    const valueToStore = value;
    localStorage.setItem(key, JSON.stringify(valueToStore));
    setState(valueToStore);
  };

  // as const tells TypeScript you want tuple type, not array.
  return [state, setValue] ;
}


function App() {

  const [cookie, setCookie] = useStoredState('cookie', "")
  const [cookieR, setCookieR] = useStoredState('cookieR', "")

  function refresh() {
      fetch(site+'auth/refresh', {method: "get", 
      headers:{
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Access-Control-Allow-Origin': '*',
      }
    }
  )
  }

  return (
    <div className="App">
      <Routes>
        <Route path='/' element={<Home/>}/>
        <Route path='/create' element={<Create/>}/>
        <Route path='/project/:project_id' element={<Project/>}/>
      </Routes>
    </div>
  );
}

export default App;
