import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Home from './templates/Home';
import UploadFileSrcML from './templates/UploadFileSrcML';
import UploadFolderSrcML from './templates/UploadFolderSrcML';
//import './App.css';

function App() {
  // usestate for setting a javascript
  // object for storing and using data
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/upload_file_srcml" element={<UploadFileSrcML />} />
        <Route path="/upload_folder_srcml" element={<UploadFolderSrcML />}/>

      </Routes>
    </BrowserRouter>
  );
}

export default App;
