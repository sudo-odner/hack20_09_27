import './styles/App.scss'; // Импортируем стили для приложения
import React, { useEffect, useState } from 'react'; // Импортируем хуки React для работы с состоянием и эффектами
import { useNavigate } from 'react-router'; // Импортируем хук для управления навигацией
import { BrowserRouter, Route, Routes, useParams, useSearchParams } from 'react-router-dom'; // Импортируем компоненты React Router для управления маршрутизацией

import Home from './pages/Home'; // Импортируем компонент домашней страницы
import Create from './pages/Create'; // Импортируем компонент для создания проектов
import Project from './pages/Project'; // Импортируем компонент для отображения проекта

function App() {
  // ... (внутри функции App нет логики, поэтому здесь нет комментариев)

  return (
    <div className="App"> {/* Корневой элемент приложения */}
      <Routes> {/* Компонент для определения маршрутов */}
        <Route path='/' element={<Home/>}/> {/* Маршрут для домашней страницы */}
        <Route path='/create' element={<Create/>}/> {/* Маршрут для создания проекта */}
        <Route path='/project/:project_id' element={<Project/>}/> {/* Маршрут для просмотра проекта, где :project_id - динамический параметр */}
      </Routes>
    </div>
  );
}

export default App;