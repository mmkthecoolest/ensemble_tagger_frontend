import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from './templates/Home';
import UploadFile from './templates/UploadFile';
import UploadFolder from "./templates/UploadFolder";
//import AnnotateFile from "./templates/AnnotateFile";
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';

function App() {
  // usestate for setting a javascript
  // object for storing and using data
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/upload_file" element={<UploadFile />} />
        <Route path="/upload_folder" element={<UploadFolder />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
